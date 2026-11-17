'use strict';

/**
 * AI-based preliminary specification review for DID Method registrations.
 *
 * For each added/modified methods/*.json file in a pull request, this script:
 *   1. Loads the registry entry and fetches its `specification` URL.
 *   2. Asks Claude to evaluate the specification against the checklist in
 *      spec-review-checklist.md.
 *   3. Writes a Markdown report (for posting as a PR comment) and sets the
 *      process exit code (0 = pass, 1 = fail) so the workflow can gate merge.
 *
 * Inputs (environment variables):
 *   ANTHROPIC_API_KEY   - required. API key for the Claude API.
 *   CHANGED_FILES       - newline- or space-separated list of changed paths.
 *                         Only methods/*.json entries are reviewed.
 *   REVIEW_OUTPUT       - optional. Path to write the Markdown report to.
 *                         Defaults to ./ai-spec-review.md
 *   REVIEW_MODEL        - optional. Overrides the Claude model id.
 *
 * Exit codes:
 *   0 - all reviewed submissions passed the preliminary review (or nothing to
 *       review, or a non-blocking infrastructure issue occurred).
 *   1 - at least one submission failed a MUST criterion.
 */

const fs = require('fs');
const path = require('path');
// The Anthropic SDK is required lazily (inside main, after we know there is work
// to do and a key is present) so the no-op and misconfiguration paths still
// produce a report even if the dependency is missing.

const MODEL = process.env.REVIEW_MODEL || 'claude-opus-4-8';
const METHODS_DIR = path.join(__dirname, '../methods');
const CHECKLIST_PATH = path.join(__dirname, 'spec-review-checklist.md');
const OUTPUT_PATH = process.env.REVIEW_OUTPUT ||
  path.join(process.cwd(), 'ai-spec-review.md');

// Cap the amount of fetched spec text sent to the model so a huge page can't
// blow past the context window or run up cost. ~200k chars is comfortably under
// the model's context while covering all but the largest specs.
const MAX_SPEC_CHARS = 200000;
const FETCH_TIMEOUT_MS = 30000;

// Rate-limit handling. Specs are large and organizations may have modest
// per-minute token limits, so a 429 is expected rather than exceptional. We
// retry a bounded number of times, honoring the `retry-after` header when the
// API provides one (rate-limit windows are ~1 minute, longer than the SDK's
// built-in backoff covers). Reviews run sequentially, so this only ever delays
// one submission at a time.
const RATE_LIMIT_MAX_RETRIES = 4;
const RATE_LIMIT_MAX_WAIT_MS = 90000;
const RATE_LIMIT_DEFAULT_WAIT_MS = 30000;

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Structured-output schema the model must return for each submission.
const REVIEW_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    overall: {
      type: 'string',
      enum: ['pass', 'fail'],
      description: 'FAIL if any MUST item failed, otherwise PASS.'
    },
    summary: {
      type: 'string',
      description: 'One or two sentence plain-language summary of the review.'
    },
    items: {
      type: 'array',
      description: 'One entry per checklist criterion evaluated.',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          id: {
            type: 'string',
            description: 'Checklist id, e.g. "M1", "S2".'
          },
          title: { type: 'string', description: 'Short criterion title.' },
          level: { type: 'string', enum: ['MUST', 'SHOULD', 'OPTIONAL'] },
          status: { type: 'string', enum: ['pass', 'fail', 'warn', 'n/a'] },
          reason: {
            type: 'string',
            description:
              'Brief justification, citing the spec where relevant. ' +
              'Required when status is fail or warn.'
          }
        },
        required: ['id', 'title', 'level', 'status', 'reason']
      }
    }
  },
  required: ['overall', 'summary', 'items']
};

function parseChangedFiles() {
  const raw = process.env.CHANGED_FILES || '';
  return raw
    .split(/[\s,]+/)
    .map((f) => f.trim())
    .filter(Boolean)
    .filter((f) => f.startsWith('methods/') && f.endsWith('.json'))
    .filter((f) => {
      const base = path.basename(f);
      return !['index.html', 'index.json', 'example.json'].includes(base);
    });
}

function loadEntry(relPath) {
  const abs = path.join(__dirname, '..', relPath);
  if(!fs.existsSync(abs)) {
    // File was deleted in the PR; nothing to review.
    return {deleted: true};
  }
  const text = fs.readFileSync(abs, 'utf8');
  try {
    return {entry: JSON.parse(text)};
  } catch(e) {
    return {parseError: e.message, text};
  }
}

async function fetchSpec(url) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const res = await fetch(url, {
      redirect: 'follow',
      signal: controller.signal,
      headers: {'User-Agent': 'did-extensions-ai-spec-review'}
    });
    if(!res.ok) {
      return {error: `HTTP ${res.status} ${res.statusText}`};
    }
    let body = await res.text();
    let truncated = false;
    if(body.length > MAX_SPEC_CHARS) {
      body = body.slice(0, MAX_SPEC_CHARS);
      truncated = true;
    }
    return {body, truncated, contentType: res.headers.get('content-type') || ''};
  } catch(e) {
    return {error: e.name === 'AbortError' ? 'request timed out' : e.message};
  } finally {
    clearTimeout(timer);
  }
}

function buildSystemPrompt(checklist) {
  return [
    'You are a preliminary reviewer for the W3C DID Extensions registry. You',
    'evaluate a submitted DID Method registration against a fixed checklist and',
    'return a structured verdict. You are advisory: a human editor makes the',
    'final decision. Be fair and specific — judge ONLY what is present in the',
    'fetched specification text and the submitted JSON entry. Do not assume a',
    'section exists because the method is well-known. You are always given the',
    'fetched specification text; an unreachable specification is handled before',
    'you are called and never reaches you.',
    '',
    'Evaluate every checklist item and return one entry per item. Cite the',
    'relevant part of the specification in your reason when you can. The overall',
    'verdict is "fail" if and only if at least one MUST item has status "fail".',
    '',
    'A "fail" BLOCKS the pull request from merging, so the bar for "fail" is',
    'deliberately high: use it ONLY for clear-cut, unambiguous violations of a',
    'MUST criterion (for example, no Security Considerations section exists at',
    'all, or the specification URL does not resolve). If a MUST criterion is only',
    'partially satisfied, thin, plausibly implied but not stated, or you are at',
    'all uncertain, use "warn" instead of "fail". When you are on the fence',
    'between "fail" and "warn", you MUST choose "warn". Warnings still surface',
    'the concern to the human editors; they simply do not block. Do not block a',
    'submission on a debatable judgment call.',
    '',
    'CHECKLIST:',
    '',
    checklist
  ].join('\n');
}

function buildUserPrompt({relPath, entry, spec}) {
  const parts = [];
  parts.push(`Reviewing registry entry: ${relPath}`);
  parts.push('');
  parts.push('Submitted JSON entry:');
  parts.push('```json');
  parts.push(JSON.stringify(entry, null, 2));
  parts.push('```');
  parts.push('');
  // A fetch failure never reaches this function — reviewSubmission short-circuits
  // to a hard M1 failure before calling the model. This path always has a spec.
  parts.push(
    `Fetched specification from ${entry.specification} ` +
    `(content-type: ${spec.contentType})` +
    (spec.truncated ? ' — TRUNCATED to fit the review budget.' : '') + ':');
  parts.push('```');
  parts.push(spec.body);
  parts.push('```');
  return parts.join('\n');
}

// Wrap messages.create with bounded, rate-limit-aware retries. The SDK already
// retries transient errors briefly, but rate-limit windows are ~1 minute — long
// enough that we wait explicitly, honoring the `retry-after` header when present.
async function createWithRetry(client, request) {
  for(let attempt = 0; ; attempt++) {
    try {
      return await client.messages.create(request);
    } catch(e) {
      const status = e && e.status;
      const isRateLimit = status === 429;
      const isOverloaded = status === 529;
      if((!isRateLimit && !isOverloaded) ||
        attempt >= RATE_LIMIT_MAX_RETRIES) {
        throw e;
      }
      // Prefer the server's retry-after (seconds); otherwise exponential backoff.
      let waitMs;
      const retryAfter = e.headers && (e.headers['retry-after'] ||
        e.headers.get && e.headers.get('retry-after'));
      const retryAfterSec = Number(retryAfter);
      if(Number.isFinite(retryAfterSec) && retryAfterSec > 0) {
        waitMs = retryAfterSec * 1000;
      } else {
        waitMs = RATE_LIMIT_DEFAULT_WAIT_MS * Math.pow(2, attempt);
      }
      waitMs = Math.min(waitMs, RATE_LIMIT_MAX_WAIT_MS);
      const kind = isRateLimit ? 'rate limited' : 'overloaded';
      console.log(`  ${kind} (HTTP ${status}); waiting ` +
        `${Math.round(waitMs / 1000)}s before retry ` +
        `${attempt + 1}/${RATE_LIMIT_MAX_RETRIES} ...`);
      await sleep(waitMs);
    }
  }
}

async function reviewSubmission(client, checklist, relPath) {
  const loaded = loadEntry(relPath);
  if(loaded.deleted) {
    return {relPath, skipped: 'file deleted in this pull request'};
  }
  if(loaded.parseError) {
    // Invalid JSON is caught by the existing validate step; surface it here too
    // but do not fail the AI review on it (the lint job owns that gate).
    return {
      relPath,
      infra: `entry is not valid JSON (${loaded.parseError}) — ` +
        'see the validation job'
    };
  }
  const entry = loaded.entry;
  if(!entry.specification) {
    return {
      relPath,
      review: {
        overall: 'fail',
        summary: 'The registry entry has no `specification` URL.',
        items: [{
          id: 'M1', title: 'Specification is reachable', level: 'MUST',
          status: 'fail', reason: 'No `specification` field present in the entry.'
        }]
      }
    };
  }

  const spec = await fetchSpec(entry.specification);
  if(spec.error) {
    // A specification that cannot be retrieved cannot be reviewed. This is a
    // hard failure of M1 (the specification must be reachable), decided by the
    // script itself — there is no point calling the model with no spec text.
    return {
      relPath,
      entry,
      specFetchError: spec.error,
      review: {
        overall: 'fail',
        summary:
          `The specification at ${entry.specification} could not be fetched ` +
          `(${spec.error}), so the submission cannot be reviewed.`,
        items: [{
          id: 'M1',
          title: 'Specification is reachable and is a DID Method specification',
          level: 'MUST',
          status: 'fail',
          reason:
            `Fetching ${entry.specification} failed: ${spec.error}. The ` +
            'specification MUST resolve to a reachable, human-readable DID ' +
            'Method specification. Fix the `specification` URL (or ensure the ' +
            'document is publicly reachable) and re-run the review.'
        }]
      }
    };
  }

  const message = await createWithRetry(client, {
    model: MODEL,
    max_tokens: 8000,
    system: buildSystemPrompt(checklist),
    output_config: {
      format: {
        type: 'json_schema',
        schema: REVIEW_SCHEMA
      }
    },
    messages: [
      {role: 'user', content: buildUserPrompt({relPath, entry, spec})}
    ]
  });

  const textBlock = message.content.find((b) => b.type === 'text');
  const review = JSON.parse(textBlock.text);
  return {relPath, entry, specFetchError: spec.error, review};
}

const STATUS_ICON = {pass: '✅', fail: '❌', warn: '⚠️', 'n/a': '➖'};

// Render a specification URL as a safe Markdown link. GitHub linkifies bare
// URLs, but we wrap it so the label is clean and any `)` in the URL can't break
// the link syntax.
function specLink(url) {
  if(!url) {
    return '_none provided_';
  }
  const safe = String(url).replace(/\)/g, '%29').replace(/\s+/g, '');
  return `[${url}](${safe})`;
}

function renderSubmission(result) {
  const lines = [];
  lines.push(`### \`${result.relPath}\`${result.entry ?
    ` — method \`did:${result.entry.name}\`` : ''}`);
  lines.push('');
  // Surface the specification link at the top of every submission so reviewers
  // can click through to confirm it exists and read it without leaving the PR.
  if(result.entry) {
    lines.push(`**Specification:** ${specLink(result.entry.specification)}`);
    lines.push('');
  }

  if(result.skipped) {
    lines.push(`_Skipped: ${result.skipped}._`);
    lines.push('');
    return {markdown: lines.join('\n'), failed: false, hadReview: false};
  }
  if(result.infra) {
    lines.push(`_Could not run the AI review: ${result.infra}._`);
    lines.push('');
    return {markdown: lines.join('\n'), failed: false, hadReview: false};
  }

  const {review} = result;
  const failed = review.overall === 'fail';
  lines.push(`**Preliminary verdict: ${failed ? '❌ FAIL' : '✅ PASS'}**`);
  lines.push('');
  lines.push(review.summary);
  lines.push('');
  if(result.specFetchError) {
    lines.push(`> ❌ The specification could not be fetched ` +
      `(${result.specFetchError}). A specification that cannot be retrieved ` +
      'cannot be reviewed, so this is a hard failure of the "specification is ' +
      'reachable" requirement (M1). Confirm the specification link above ' +
      'resolves publicly, then re-run the review.');
    lines.push('');
  }
  lines.push('| | Item | Level | Status | Notes |');
  lines.push('|---|---|---|---|---|');
  for(const item of review.items) {
    const icon = STATUS_ICON[item.status] || '';
    const notes = (item.status === 'pass' || item.status === 'n/a') ?
      '' : (item.reason || '').replace(/\n+/g, ' ').replace(/\|/g, '\\|');
    lines.push(`| ${icon} | ${item.id}. ${item.title} | ${item.level} | ` +
      `${item.status} | ${notes} |`);
  }
  lines.push('');
  return {markdown: lines.join('\n'), failed, hadReview: true};
}

async function main() {
  const changed = parseChangedFiles();
  const header = [
    '## 🤖 AI Preliminary Specification Review',
    '',
    'This is an **advisory, automated** review of the DID Method ' +
    'specification(s) referenced in this pull request, checked against the ' +
    '[registration checklist](tooling/spec-review-checklist.md). It does not ' +
    'replace review by the registry editors.',
    ''
  ];

  if(changed.length === 0) {
    const md = header.concat([
      '_No `methods/*.json` additions or changes detected; nothing to review._'
    ]).join('\n');
    fs.writeFileSync(OUTPUT_PATH, md, 'utf8');
    console.log('No method files changed; skipping AI spec review.');
    return 0;
  }

  if(!process.env.ANTHROPIC_API_KEY) {
    // Missing key is an infrastructure problem, not a submission failure.
    // Do not block the PR; emit a clear notice for a human to act on.
    const md = header.concat([
      '> ⚠️ `ANTHROPIC_API_KEY` is not configured, so the automated spec ' +
      'review could not run. A registry editor must review the ' +
      'specification(s) manually.'
    ]).join('\n');
    fs.writeFileSync(OUTPUT_PATH, md, 'utf8');
    console.error('ANTHROPIC_API_KEY is not set; skipping AI spec review.');
    return 0;
  }

  const checklist = fs.readFileSync(CHECKLIST_PATH, 'utf8');
  const Anthropic = require('@anthropic-ai/sdk');
  const client = new Anthropic();

  const sections = [];
  let anyFailed = false;
  let anyReviewed = false;
  let anyInfraIssue = false;

  for(const relPath of changed) {
    console.log(`Reviewing ${relPath} ...`);
    let result;
    try {
      result = await reviewSubmission(client, checklist, relPath);
    } catch(e) {
      // A model/transport error must not block a submission — surface it and
      // let a human take over.
      console.error(`Error reviewing ${relPath}:`, e.message);
      anyInfraIssue = true;
      sections.push([
        `### \`${relPath}\``, '',
        `_Could not complete the AI review (${e.message}). A registry editor ` +
        'must review this specification manually._', ''
      ].join('\n'));
      continue;
    }
    const rendered = renderSubmission(result);
    sections.push(rendered.markdown);
    if(rendered.failed) {
      anyFailed = true;
    }
    if(rendered.hadReview) {
      anyReviewed = true;
    } else {
      anyInfraIssue = true;
    }
  }

  let verdict;
  if(anyFailed) {
    verdict =
      '> ❌ **One or more submissions did not pass the preliminary checklist ' +
      'review.** See the details below and address the failing MUST items, ' +
      'then push an update to re-run this check.';
  } else if(anyReviewed) {
    verdict = anyInfraIssue ?
      '> ✅ **All submissions that could be reviewed passed the preliminary ' +
      'checklist review**, but at least one could not be evaluated ' +
      'automatically (see the notes below). A registry editor will perform ' +
      'the final review.' :
      '> ✅ **All reviewed submissions passed the preliminary checklist ' +
      'review.** A registry editor will still perform the final review.';
  } else {
    verdict =
      '> ⚠️ **No submission could be reviewed automatically** (see the notes ' +
      'below). A registry editor must review the specification(s) manually.';
  }

  const md = header
    .concat([verdict, ''])
    .concat(sections)
    .join('\n');
  fs.writeFileSync(OUTPUT_PATH, md, 'utf8');
  console.log(`Wrote review report to ${OUTPUT_PATH}`);

  return anyFailed ? 1 : 0;
}

main()
  .then((code) => process.exit(code))
  .catch((e) => {
    // Never hard-crash the job in a way that leaves no report; treat an
    // unexpected top-level error as non-blocking infrastructure failure.
    console.error('Unexpected error in AI spec review:', e);
    try {
      fs.writeFileSync(OUTPUT_PATH, [
        '## 🤖 AI Preliminary Specification Review', '',
        `> ⚠️ The automated review failed to run (${e.message}). A registry ` +
        'editor must review the specification(s) manually.'
      ].join('\n'), 'utf8');
    } catch(_) { /* ignore */ }
    process.exit(0);
  });
