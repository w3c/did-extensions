# New DID Method Author Guide

This guide maps the journey from "I want to create a DID method" to all the
repositories, specifications, and processes involved in the W3C DID ecosystem.

## Before You Start

Creating a DID method involves more than writing a specification and registering
a name. The ecosystem provides tools for **evaluation**, **conformance testing**,
and **interoperability** — understanding these upfront will save time and produce
a stronger method.

### What This Registry Is (and Isn't)

| This registry **is** | This registry **is not** |
|---|---|
| A catalog of known DID methods | A certification authority |
| A namespace deconfliction mechanism | A spec review or approval process |
| A JSON-LD context coordination point | An endorsement of method quality |
| A discoverability aid for implementers | A guarantee of interoperability |

**"Registered" status means the method is known to exist — not that it has been
evaluated, tested, or endorsed by the W3C.**

## The Journey

### Step 1: Understand DID Core

Read the [DID Core v1.0 Specification](https://www.w3.org/TR/did-core/) to
understand the data model, syntax, and conformance requirements your method
must satisfy.

- **Spec:** [w3c.github.io/did](https://w3c.github.io/did/)
- **Repo:** [w3c/did](https://github.com/w3c/did)

### Step 2: Identify Your Use Case

The [DID Use Cases and Requirements](https://www.w3.org/TR/did-use-cases/)
document defines 22 requirements derived from 18 use cases. Identify which
requirements your method must satisfy for your target use case.

- **Spec:** [w3c.github.io/did-use-cases](https://w3c.github.io/did-use-cases/)
- **Repo:** [w3c/did-use-cases](https://github.com/w3c/did-use-cases)
- **Structured data:** [data/](https://github.com/w3c/did-use-cases/tree/main/data) (use cases, requirements, cross-reference matrix)

#### Requirement Tiers

Based on use case frequency analysis, requirements fall into three tiers:

| Tier | Criteria | Count | Examples |
|---|---|---|---|
| **Core** | Referenced by ≥70% of use cases | 8 | Decentralization, Persistence, Cryptographic Verifiability |
| **Common** | Referenced by 40–69% of use cases | 6 | Interoperability, Portability, Discoverability |
| **Specialized** | Referenced by <40% of use cases | 8 | Equivalence, Service Endpoint Support |

### Step 3: Evaluate Decentralization Characteristics

The [DID Method Rubric](https://www.w3.org/TR/did-rubric/) provides 36
evaluation criteria across 8 categories to assess your method's design
decisions. This is **not** a pass/fail test — it helps you understand and
communicate the trade-offs in your method.

- **Spec:** [w3c.github.io/did-rubric](https://w3c.github.io/did-rubric/)
- **Repo:** [w3c/did-rubric](https://github.com/w3c/did-rubric)

| Category | What it evaluates | # Criteria |
|---|---|---|
| Rulemaking | Governance of rule-making authority | 5 |
| Design | Method specification as designed | 3 |
| Operation | Rule execution and visibility | 3 |
| Enforcement | Rule compliance and violation response | 1 |
| Alternatives | Implementation diversity | 6 |
| Adoption & Diversity | Usage breadth | 5 |
| Security | Cryptographic strength and trust | 9 |
| Privacy | Privacy protection mechanisms | 4 |

### Step 4: Write Your Method Specification

Your specification **must be written in Markdown** and hosted in this repository
under `specs/<your-method>/`. This ensures:

- No broken links — spec and registration live in the same repo
- Always the latest version — no drift between registry URL and actual spec
- GitHub-native editing — anyone can fix a typo via PR without touching HTML
- Standardized structure — every spec follows the same template and sections

**Start with the template:**

```bash
cp specs/TEMPLATE.md specs/<your-method>/spec.md
```

For complex methods, split into numbered section files (see
[did:sns](https://github.com/Attestto-com/did-sns-spec/tree/main/did-sns/spec)
as the reference — 14 sections covering abstract, use cases, trust model,
privacy, CRUD, security, interoperability, and more).

The template defines 14 sections — 8 required, 3 recommended, 3 optional:

| Required | Recommended | Optional |
|---|---|---|
| Abstract | Trust Model | Metadata Schema |
| Use Case & Requirements | Interoperability | Implementation Notes |
| DID Syntax | Architectural Rationale | |
| DID Document | W3C Requirements Coverage | |
| CRUD Operations | | |
| Security Considerations | | |
| Privacy Considerations | | |
| References | | |

See [specs/README.md](./specs/README.md) for the full template documentation
and a list of the 10 best-documented methods as examples.

Also review the [DID Implementation Guide](https://www.w3.org/TR/did-imp-guide/)
for practical guidance.

- **Template:** [specs/TEMPLATE.md](./specs/TEMPLATE.md)
- **Examples:** [specs/README.md](./specs/README.md)
- **W3C Guide:** [w3c.github.io/did-imp-guide](https://w3c.github.io/did-imp-guide/)

### Step 5: Define DID Resolution Behavior

If your method supports resolution beyond the basics, review the
[DID Resolution](https://www.w3.org/TR/did-resolution/) specification.

- **Spec:** [w3c.github.io/did-resolution](https://w3c.github.io/did-resolution/)
- **Repo:** [w3c/did-resolution](https://github.com/w3c/did-resolution)
- **Threat model:** [w3c/did-resolution-threat-model](https://github.com/w3c/did-resolution-threat-model)

If your method introduces custom resolution metadata properties, register
them in the [resolution/](./resolution/) directory of this repository.

### Step 6: Run Conformance Tests

The [DID Test Suite](https://w3c.github.io/did-test-suite/) provides
conformance tests for DID Core. Running these against your method
implementation validates spec compliance.

- **Report:** [w3c.github.io/did-test-suite](https://w3c.github.io/did-test-suite/)
- **Repo:** [w3c/did-test-suite](https://github.com/w3c/did-test-suite)

### Step 7: Choose a Descriptive Method Name

Your method name should describe what the method fundamentally does or where
it anchors identity. Self-describing names help developers immediately understand
your method's characteristics without prior knowledge.

See [NAMING.md](./NAMING.md) for the naming convention and guidelines.

| Approach | Example | Clarity |
|---|---|---|
| Describes anchor/mechanism | `did:web`, `did:key`, `did:peer` | Immediately clear |
| Abbreviates platform | `did:ethr`, `did:sol` | Clear within ecosystem |
| Branded/opaque acronym | `did:ion`, `did:v1`, `did:cel` | Requires prior knowledge |

### Step 8: Register Your Method

Use the **[Self-Assessment Form](./explorer.html)** to generate your
registration JSON. The form walks you through:

1. **Select your use case** — see which requirements apply
2. **Assess each requirement** — covered / partial / uncovered with explanations
3. **Check for overlaps** — discover existing methods with similar coverage
4. **Enter method details** — name validation, category, composability
5. **Download JSON** — pre-filled registration file for your PR

Alternatively, copy the [template](./data/method-template.json) manually.

Your PR should include:

```
methods/<your-method>.json       ← registration (from the form)
specs/<your-method>/spec.md      ← specification (from the template)
```

The `specification` field in your JSON should point to your in-repo spec:

```jsonc
{
  "name": "your-method-name",
  "status": "registered",
  "specification": "./specs/your-method-name/spec.md",
  "category": "web-anchored",
  "primaryUseCase": "uc-credentials",
  "requirements": { ... }
}
```

Registration criteria are **mechanical** — valid JSON, a spec in Markdown, no
name collisions. The CI runs [validate-extended.js](./tooling/validate-extended.js)
to check naming, requirement coverage, and overlap detection.

See [the registration process](https://w3c.github.io/did-extensions/#the-registration-process)
for details.

### Step 9: Consider a Universal Resolver Driver

The [Universal Resolver](https://github.com/decentralized-identity/universal-resolver)
is a DIF project that provides a unified HTTP API for resolving any DID method.
Adding a driver makes your method immediately usable by any application that
integrates the Universal Resolver.

### Step 10: Engage with the Community

| Forum | Purpose | Link |
|---|---|---|
| W3C DID Working Group | Spec development and registration | [w3c/did-wg](https://github.com/w3c/did-wg) |
| DIF DID Methods WG | Method evaluation and standardization | [decentralized-identity/did-methods](https://github.com/decentralized-identity/did-methods) |
| W3C CCG | Community incubation | [w3c-ccg](https://github.com/w3c-ccg) |

## Frequently Confused Concepts

| Concept | What it means | Where it happens |
|---|---|---|
| **Registration** | Adding your method to the catalog | This repo (`did-extensions`) |
| **Evaluation** | Assessing decentralization characteristics | [DID Rubric](https://github.com/w3c/did-rubric), [DID Traits](https://github.com/decentralized-identity/did-traits) |
| **Conformance** | Testing against DID Core spec | [DID Test Suite](https://github.com/w3c/did-test-suite) |
| **Standardization** | Formal W3C/DIF standardization process | [DIF Methods WG](https://github.com/decentralized-identity/did-methods), [W3C Methods WG Charter](https://github.com/w3c/did-methods-wg-charter) |

These are **independent processes**. Registration does not imply evaluation,
conformance, or standardization.

## Related Resources

- [Self-Assessment Form](./explorer.html) — interactive form to assess fitness, detect overlaps, and generate JSON
- [Specification Template](./specs/TEMPLATE.md) — standard Markdown template for method specs
- [Best-Documented Methods](./specs/README.md) — top 10 reference examples
- [Ecosystem Repository Map](./REPO-MAP.md) — all active repositories across W3C, W3C-CCG, and DIF
- [Cross-References](./data/cross-references.json) — structured links between requirements, rubric criteria, and registry entries
- [Method Naming Convention](./NAMING.md) — guidelines for choosing descriptive method names
