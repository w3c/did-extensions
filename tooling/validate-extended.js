#!/usr/bin/env node

/**
 * Validate extended method JSON fields (optional — does not break existing CI).
 *
 * Checks:
 * 1. If extended fields are present, they must be well-formed
 * 2. Name collision detection (warns, does not fail)
 * 3. Category must be from allowed list
 * 4. Use case IDs must exist in data/use-cases.json
 * 5. Requirement statuses must be covered/partial/uncovered
 * 6. Overlap report against other methods with extended data
 *
 * Usage: node tooling/validate-extended.js [methods/new-method.json]
 *        node tooling/validate-extended.js --all
 */

const fs = require('fs');
const path = require('path');

const METHODS_DIR = path.join(__dirname, '..', 'methods');
const DATA_DIR = path.join(__dirname, '..', 'data');

const VALID_CATEGORIES = [
  'key-derived', 'web-anchored', 'ledger-anchored',
  'service-anchored', 'peer-local', 'dht-anchored'
];

const VALID_STATUSES = ['covered', 'partial', 'uncovered', ''];

const VALID_TIERS = ['core', 'common', 'specialized'];

// ── Load reference data ─────────────────────────────────────

let useCases = [];
try {
  const ucData = JSON.parse(fs.readFileSync(path.join(DATA_DIR, 'use-cases.json'), 'utf-8'));
  useCases = ucData.useCases.map(uc => uc.id);
} catch (e) {
  console.warn('Warning: Could not load use-cases.json — skipping UC validation');
}

// ── Load all existing methods ───────────────────────────────

function loadAllMethods() {
  const methods = [];
  try {
    const files = fs.readdirSync(METHODS_DIR).filter(f => f.endsWith('.json'));
    for (const file of files) {
      try {
        const data = JSON.parse(fs.readFileSync(path.join(METHODS_DIR, file), 'utf-8'));
        methods.push({ file, ...data });
      } catch (e) {
        // Skip unparseable files — the core validator handles those
      }
    }
  } catch (e) {
    console.warn('Warning: Could not read methods directory');
  }
  return methods;
}

// ── Validate a single method ────────────────────────────────

function validateExtended(methodPath, allMethods) {
  const errors = [];
  const warnings = [];

  let method;
  try {
    method = JSON.parse(fs.readFileSync(methodPath, 'utf-8'));
  } catch (e) {
    errors.push(`Failed to parse JSON: ${e.message}`);
    return { errors, warnings };
  }

  const fileName = path.basename(methodPath);

  // ── Category ──
  if (method.category) {
    if (!VALID_CATEGORIES.includes(method.category)) {
      errors.push(`Invalid category "${method.category}". Must be one of: ${VALID_CATEGORIES.join(', ')}`);
    }
  }

  // ── Name collision ──
  if (method.name) {
    const collisions = allMethods.filter(m =>
      m.name === method.name && m.file !== fileName
    );
    if (collisions.length > 0) {
      warnings.push(`Name collision: "did:${method.name}" is already registered in ${collisions.map(c => c.file).join(', ')}. Consider "did:${method.name}-2" or a more descriptive variant.`);
    }

    // Check if name looks branded (heuristic: >6 chars, no common keywords)
    const descriptiveWords = ['web', 'key', 'peer', 'dns', 'pkh', 'jwk', 'sol', 'eth', 'dht', 'self', 'btc'];
    const isDescriptive = descriptiveWords.some(w => method.name.toLowerCase().includes(w)) || method.name.length <= 5;
    if (!isDescriptive) {
      warnings.push(`Naming: "did:${method.name}" may not be self-describing. Consider naming after the anchoring mechanism or cryptographic primitive. See NAMING.md`);
    }
  }

  // ── Use Cases ──
  if (method.primaryUseCase && useCases.length > 0) {
    if (!useCases.includes(method.primaryUseCase)) {
      warnings.push(`Unknown primaryUseCase "${method.primaryUseCase}". Known IDs: ${useCases.slice(0, 5).join(', ')}...`);
    }
  }

  if (method.supportedUseCases && Array.isArray(method.supportedUseCases) && useCases.length > 0) {
    method.supportedUseCases.forEach(uc => {
      if (!useCases.includes(uc)) {
        warnings.push(`Unknown use case ID "${uc}" in supportedUseCases`);
      }
    });
  }

  // ── Requirements ──
  if (method.requirements && typeof method.requirements === 'object') {
    Object.entries(method.requirements).forEach(([key, val]) => {
      if (typeof val !== 'object') {
        errors.push(`requirements.${key} must be an object with {tier, status, detail}`);
        return;
      }
      if (val.tier && !VALID_TIERS.includes(val.tier)) {
        errors.push(`requirements.${key}.tier "${val.tier}" invalid. Must be: ${VALID_TIERS.join(', ')}`);
      }
      if (val.status && !VALID_STATUSES.includes(val.status)) {
        errors.push(`requirements.${key}.status "${val.status}" invalid. Must be: ${VALID_STATUSES.join(', ')}`);
      }
      if (val.status && val.status !== '' && (!val.detail || val.detail.trim() === '')) {
        warnings.push(`requirements.${key}: status is "${val.status}" but detail is empty. Please explain how/why.`);
      }
    });

    // Check core requirements coverage
    const coreReqs = Object.entries(method.requirements).filter(([, v]) => v.tier === 'core');
    const uncoveredCore = coreReqs.filter(([, v]) => v.status === 'uncovered');
    if (uncoveredCore.length > 0) {
      warnings.push(`${uncoveredCore.length} core requirement(s) marked as uncovered: ${uncoveredCore.map(([k]) => k).join(', ')}. Core requirements are expected for most methods.`);
    }
  }

  // ── Extends / Calls ──
  if (method.extends && Array.isArray(method.extends)) {
    method.extends.forEach(ext => {
      if (!allMethods.find(m => m.name === ext)) {
        warnings.push(`extends: "did:${ext}" is not registered. It may not exist yet.`);
      }
    });
  }

  if (method.calls && Array.isArray(method.calls)) {
    method.calls.forEach(call => {
      if (!allMethods.find(m => m.name === call)) {
        warnings.push(`calls: "did:${call}" is not registered. It may not exist yet.`);
      }
    });
  }

  // ── Overlap detection ──
  if (method.requirements) {
    const myCovered = new Set(
      Object.entries(method.requirements)
        .filter(([, v]) => v.status === 'covered' || v.status === 'partial')
        .map(([k]) => k.toLowerCase())
    );

    if (myCovered.size > 0) {
      const overlaps = allMethods
        .filter(m => m.requirements && m.name !== method.name)
        .map(m => {
          const theirs = new Set(
            Object.entries(m.requirements)
              .filter(([, v]) => v.status === 'covered' || v.status === 'partial')
              .map(([k]) => k.toLowerCase())
          );
          const shared = [...myCovered].filter(r => theirs.has(r));
          const pct = Math.round((shared.length / myCovered.size) * 100);
          return { name: m.name, pct, shared: shared.length };
        })
        .filter(o => o.pct >= 70)
        .sort((a, b) => b.pct - a.pct);

      overlaps.forEach(o => {
        warnings.push(`High overlap (${o.pct}%) with did:${o.name} — ${o.shared} shared requirements. Consider extending or contributing to the existing method.`);
      });
    }
  }

  return { errors, warnings };
}

// ── Main ────────────────────────────────────────────────────

function main() {
  const args = process.argv.slice(2);
  const allMethods = loadAllMethods();

  let files = [];
  if (args.includes('--all')) {
    files = allMethods.map(m => path.join(METHODS_DIR, m.file));
  } else if (args.length > 0) {
    files = args.filter(a => !a.startsWith('--'));
  } else {
    console.log('Usage: node validate-extended.js [file.json] | --all');
    console.log('Validates extended DID method registration fields.');
    process.exit(0);
  }

  let hasErrors = false;

  files.forEach(file => {
    const { errors, warnings } = validateExtended(file, allMethods);

    if (errors.length > 0 || warnings.length > 0) {
      console.log(`\n─── ${path.basename(file)} ───`);
    }

    errors.forEach(e => {
      console.error(`  ✗ ERROR: ${e}`);
      hasErrors = true;
    });

    warnings.forEach(w => {
      console.warn(`  ⚠ WARNING: ${w}`);
    });

    if (errors.length === 0 && warnings.length === 0) {
      console.log(`  ✓ ${path.basename(file)} — valid`);
    }
  });

  if (hasErrors) {
    console.error('\nValidation failed with errors.');
    process.exit(1);
  } else {
    console.log('\nValidation passed (warnings are non-blocking).');
    process.exit(0);
  }
}

main();
