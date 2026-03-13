![W3C Logo](https://www.w3.org/Icons/w3c_home)

[![Echidna Auto-publish](https://github.com/w3c/did-extensions/actions/workflows/auto-publish.yml/badge.svg)](https://github.com/w3c/did-extensions/actions/workflows/auto-publish.yml)

# Decentralized Identifier Extensions

This repository contains a list of known DID Extensions that are tracked
by the
[W3C Decentralized Identifier Working Group](https://www.w3.org/2019/did-wg/)
(DID WG) for the purpose of enhancing DID ecosystem interoperability. There
might be extensions to DIDs other than the ones listed here; this is not
meant to be an exhaustive or centralized list of extensions.

An Editor's Draft of this repository is available at
https://w3c.github.io/did-extensions/.

> **New to DID methods?** Start with the
> [New Method Author Guide](./ONBOARDING.md) for a step-by-step walkthrough
> of the full ecosystem — from understanding DID Core to registering your
> method.

## What This Registry Is (and Isn't)

This is a **catalog** of known DID methods and extensions — not a certification
authority, spec review board, or endorsement process. Understanding this
distinction is important:

| Process | What it does | Where it happens |
|---|---|---|
| **Registration** | Adds your method to the catalog | This repo ([did-extensions](https://github.com/w3c/did-extensions)) |
| **Evaluation** | Assesses decentralization characteristics | [DID Rubric](https://github.com/w3c/did-rubric), [DID Traits](https://github.com/decentralized-identity/did-traits) |
| **Conformance** | Tests against DID Core specification | [DID Test Suite](https://github.com/w3c/did-test-suite) |
| **Standardization** | Formal W3C/DIF standardization process | [DIF Methods WG](https://github.com/decentralized-identity/did-methods), [W3C Methods WG Charter](https://github.com/w3c/did-methods-wg-charter) |

These are **independent processes**. Registration does not imply evaluation,
conformance, or standardization. "Registered" status means the method is known
to exist — not that it has been reviewed or endorsed by the W3C.

## Adding a DID Method

In order to register a new DID method, you must add a JSON file
to the [./methods](./methods) directory and
[open a pull request](https://github.com/w3c/did-extensions/pulls)
to add the file to this repository.

Before registering, we recommend:

1. Reading the [New Method Author Guide](./ONBOARDING.md) for the full journey
2. Reviewing the [Method Naming Convention](./NAMING.md) for choosing a
   descriptive method name
3. Evaluating your method against the [DID Rubric](https://www.w3.org/TR/did-rubric/)

Here is an [example registration entry](https://w3c.github.io/did-extensions/methods/example.json):

```jsonc
{
  // These fields are required
  "name": "example",
  "status": "registered",
  "specification": "https://w3c-ccg.github.io/did-spec/",
  // These fields are optional
  "contactName": "W3C Credentials Community Group",
  "contactEmail": "",
  "contactWebsite": "",
  "verifiableDataRegistry": "DID Specification"
}
```

Your Pull Request will be automatically validated, please ensure
that all of the automated tests pass (no errors reported) or
your submission will not be reviewed. Common reasons for failed
validation includes invalidly formatted JSON files and missing
mandatory fields. There will be a checklist that you are expected
to complete and attest to its accuracy. Once you submit your request,
your pull request will be reviewed by the registry editors. Changes
regarding the required criteria may be requested. If there are at
least two reviews by registry maintainers listed in the CODEOWNERS file, and no objections or
changes requested, your DID method will be registered after a
minimum of 7 days and a maximum of 30 days.

## Adding Anything Else

Use the standard fork, branch, and pull request workflow to propose changes to
the registry. Please make branch names informative—by including the issue or
bug number for example.

Editorial changes that improve the readability of the registry or correct
spelling or grammatical mistakes are welcome.

Non-editorial changes MUST go through a review and approval process that is
[detailed in the registry](https://w3c.github.io/did-extensions/#the-registration-process).

Please read [CONTRIBUTING.md](CONTRIBUTING.md), about licensing contributions.

## Repository Structure

| Directory | Purpose |
|---|---|
| [methods/](./methods/) | One JSON file per registered DID method (225+ registered) |
| [properties/](./properties/) | DID Document property extensions beyond DID Core |
| [resolution/](./resolution/) | DID Resolution parameter and metadata extensions |
| [vocabs/](./vocabs/) | JSON-LD vocabulary/context files for registered properties |
| [json_schemas/](./json_schemas/) | JSON Schemas for validating registration entries |
| [tooling/](./tooling/) | CI build/validation scripts |
| [transitions/](./transitions/) | Status transition records for registered entries |
| [data/](./data/) | Structured cross-references between ecosystem specs |

## Structured Data

The [data/](./data/) directory contains machine-readable cross-references
linking W3C requirements, rubric evaluation criteria, test suite sections,
and registry directories:

- [cross-references.json](./data/cross-references.json) — maps each of the 22
  W3C DID requirements to relevant rubric criteria, test suite sections, and
  registry directories

## Code of Conduct

W3C functions under a [code of conduct](https://www.w3.org/Consortium/cepc/).

## New to the DID Ecosystem?

- [New Method Author Guide](./ONBOARDING.md) — step-by-step journey from
  concept to registration
- [Method Naming Convention](./NAMING.md) — guidelines for choosing descriptive
  method names
- [Ecosystem Repository Map](./REPO-MAP.md) — all active repositories across
  W3C, W3C-CCG, and DIF with supersession chains

## DID Working Group Repositories

### W3C

- [W3C DID Core Specification v1.0](https://github.com/w3c/did) (formerly `did-core`)
- [W3C DID Working Group](https://github.com/w3c/did-wg)
- [W3C DID Rubric v1.0](https://github.com/w3c/did-rubric) — 36 evaluation criteria
- [W3C DID Use Cases v1.0](https://github.com/w3c/did-use-cases) — 18 use cases, 22 requirements
- [W3C DID Test Suite and Implementation Report](https://github.com/w3c/did-test-suite)
- [W3C DID Resolution](https://github.com/w3c/did-resolution)
- [W3C DID Implementation Guide](https://github.com/w3c/did-imp-guide)
- [W3C DID Methods WG Charter](https://github.com/w3c/did-methods-wg-charter) (proposed)

### Decentralized Identity Foundation

- [DIF DID Methods WG](https://github.com/decentralized-identity/did-methods) — method evaluation and standardization
- [DIF DID Traits](https://github.com/decentralized-identity/did-traits) — method characterization
- [DIF Universal Resolver](https://github.com/decentralized-identity/universal-resolver)

For a complete map of all 40+ repositories, see [REPO-MAP.md](./REPO-MAP.md).
