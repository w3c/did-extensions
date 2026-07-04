# DID Method Specification Review Checklist

This is the checklist an AI reviewer uses to perform a **preliminary, advisory
review** of a DID Method specification when a pull request adds or modifies a
`methods/*.json` registry entry. It is the single source of truth for the
automated spec review; editors can update the criteria here without touching the
workflow code.

The criteria are derived from two sources:

1. The DID Method Registration form in
   [`.github/PULL_REQUEST_TEMPLATE.md`](../.github/PULL_REQUEST_TEMPLATE.md).
2. The Registration Process policies in the registry specification
   ([`index.html`](../index.html), "The Registration Process" section).

Each item is either **MUST** (a hard requirement — failing it fails the
preliminary review) or **SHOULD/OPTIONAL** (advisory — a failure is reported as a
warning but does not fail the review).

## How the reviewer decides

For each item the reviewer must return one of:

- `pass` — the linked specification clearly satisfies the criterion.
- `fail` — **reserved for clear-cut, unambiguous violations of a MUST
  criterion.** Use `fail` only when the specification plainly and beyond
  reasonable doubt does not satisfy the requirement (e.g. there is no Security
  Considerations section at all, or the `specification` URL does not resolve).
- `warn` — the default for anything short of a clear-cut failure: a
  SHOULD/OPTIONAL criterion is not satisfied, a MUST criterion is only partially
  satisfied or thin, the requirement is plausibly implied but not stated, or the
  reviewer is uncertain. When in doubt between `fail` and `warn`, choose `warn`.
- `n/a` — the criterion does not apply to this submission.

Because a `fail` blocks the pull request from merging, the bar for `fail` is
deliberately high: a reviewer who is not confident the violation is clear-cut
must use `warn` instead. Warnings still surface the concern to the editors for a
human decision; they do not block. This keeps the blocking gate reserved for
unambiguous problems and avoids a merge-blocking verdict flipping between runs on
a borderline case.

The reviewer must judge **only what is present in the fetched specification
text** plus the submitted JSON entry. It must not assume a section exists because
the method is well-known. If the specification cannot be fetched at all, it
cannot be reviewed: this is a hard failure of M1 and the overall verdict is
FAIL (see M1). The automated tooling detects an unreachable specification and
fails the review directly, without asking the model to guess.

The overall verdict is **FAIL** if any MUST item is `fail`; otherwise **PASS**
(warnings are surfaced but do not fail the review).

---

## MUST criteria (failing any of these fails the preliminary review)

### M1. Specification is reachable and is a DID Method specification
The `specification` URL in the JSON entry resolves to human-readable content
that is recognizably a DID Method specification (not a 404, a login wall, an
unrelated page, or an empty repository). A specification that cannot be
fetched (missing URL, network error, timeout, non-2xx response, etc.) is a
**hard `fail`** — a specification that cannot be retrieved cannot be reviewed.
The automated tooling enforces this directly.

### M2. DID Method Syntax is defined
The specification defines the DID Method Syntax — the ABNF or equivalent grammar
for the method-specific identifier (`did:<method-name>:<method-specific-id>`).
See https://www.w3.org/TR/did-1.1/#method-syntax

### M3. CRUD operations are defined
The specification describes how DIDs are operated on with this method. `fail`
only in the clear-cut case where the specification does not describe DID
operations at all (no Create/registration, no Read/Resolve). If some operations
are described but others (e.g. Update or Deactivate) are missing or only
implied, use `warn` — partial CRUD coverage is a concern for the editors, not an
automatic block. A method that is inherently read-only (e.g. an ephemeral or
deterministic method) should still explain which operations apply; if it does
not, that is a `warn`.
See https://www.w3.org/TR/did-1.1/#method-operations

### M4. Security Considerations section is present and substantive
The specification contains a Security Considerations section that includes at
least a full paragraph of prose (not merely a heading, a stub, a "TODO"/"TBD"
placeholder, or a single sentence) describing at least one concrete,
method-relevant security consideration — for example a specific threat, attack,
risk, or mitigation that applies to this DID method. `fail` (clear-cut) when the
section is absent entirely, is only a heading with no real content, or contains
no actual security consideration. `warn` when a genuine consideration is present
but the section is thin, generic, or you are uncertain whether it is substantive
enough.
See https://www.w3.org/TR/did-1.1/#security-requirements

### M5. Privacy Considerations section is present and substantive
The specification contains a Privacy Considerations section that includes at
least a full paragraph of prose (not merely a heading, a stub, a "TODO"/"TBD"
placeholder, or a single sentence) describing at least one concrete,
method-relevant privacy consideration — for example a specific way the method
affects correlation, tracking, disclosure of personal data, or a mitigation that
applies to this DID method. `fail` (clear-cut) when the section is absent
entirely, is only a heading with no real content, or contains no actual privacy
consideration. `warn` when a genuine consideration is present but the section is
thin, generic, or you are uncertain whether it is substantive enough.
See https://www.w3.org/TR/did-1.1/#privacy-requirements

### M6. Method name is indicative and non-generic
The `name` field is a plausible, function-indicative DID method name and avoids
generic placeholder terms such as "mymethod", "example", "registry", "foo", or
"test".

### M7. No unreasonable legal, security, moral, or privacy harms
Nothing in the specification indicates the method is designed to enable direct
harm to others — e.g. racist content, technologies to persecute minority
populations, or unconsented pervasive tracking. Flag only clear, on-its-face
concerns; do not speculate.

### M8. Human-readable description of the addition
The specification provides a human-readable description of what the DID method
is and does, sufficient for an implementer to understand its purpose.

---

## SHOULD / OPTIONAL criteria (advisory — reported as warnings)

### S1. `contactEmail` present (OPTIONAL)
The JSON entry includes a `contactEmail`.

### S2. `verifiableDataRegistry` present (OPTIONAL)
The JSON entry includes a `verifiableDataRegistry` describing where the DIDs are
anchored.

### S3. Intellectual-property posture is clear (SHOULD)
The specification does not raise obvious unresolved copyright, trademark, or
intellectual-property concerns. Flag only clear issues; absence of an explicit
IP statement is a warning, not a failure.
