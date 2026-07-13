# DID Method Naming Convention

## Principle

A DID method name should describe **what the method fundamentally does or where
it anchors identity** — not reference brands, products, or opaque acronyms.

This follows the same principle as clean code naming: a function called
`hashPassword()` tells you what it does; one called `hp7()` does not.

## Why Descriptive Names Matter

1. **Developer clarity** — a developer scanning the [method registry](https://w3c.github.io/did-extensions/)
   should understand what each method does from the name alone, without clicking
   through to each specification
2. **Reduced IP/trademark conflicts** — descriptive functional terms are
   inherently non-brandable, avoiding the governance burden of adjudicating
   trademark disputes (see [did-extensions#597](https://github.com/w3c/did-extensions/issues/597),
   [did-methods#10](https://github.com/decentralized-identity/did-methods/issues/10#issuecomment-2501758865))
3. **Ecosystem coherence** — consistent naming creates a self-documenting
   registry where method categories emerge naturally

## Current Landscape

The existing registered methods use inconsistent naming approaches:

| Naming Pattern | Examples | Clarity Level |
|---|---|---|
| Describes anchor/mechanism | `did:web`, `did:key`, `did:peer`, `did:pkh` | High — immediately clear |
| Abbreviates platform/chain | `did:ethr`, `did:sol`, `did:tz` | Medium — clear within ecosystem |
| Acronym of project name | `did:ion` (Identity Overlay Network), `did:dht` (Distributed Hash Table) | Low-Medium — requires lookup |
| Branded/opaque | `did:v1`, `did:cel`, `did:tdw` | Low — requires prior knowledge |

## Guidelines

### DO: Name after the anchoring mechanism or fundamental property

The name should answer one of these questions:

- **Where** does identity anchor? → `did:web` (web domain), `did:dns` (DNS)
- **What** cryptographic primitive is used? → `did:key` (public key), `did:pkh` (public key hash)
- **How** does resolution work? → `did:peer` (peer-to-peer), `did:self` (self-issued)

### DO: Use recognizable abbreviations for well-known platforms

When the method is specific to a blockchain or network, abbreviating the
platform name is acceptable if widely recognized:

- `did:ethr` — Ethereum (widely known abbreviation)
- `did:sol` — Solana (widely known abbreviation)

### DON'T: Use internal project names, version numbers, or marketing terms

- Avoid names that only insiders understand (e.g., project codenames)
- Avoid version-like suffixes (e.g., `did:v1`) — these confuse spec versioning
  with method identity
- Avoid names chosen for branding rather than description

### DON'T: Use acronyms that require explanation

If the acronym doesn't immediately convey the method's purpose to a developer
unfamiliar with your project, expand it or choose a more descriptive term.

## Suggested Categories

While not a strict taxonomy, method names tend to fall into natural categories
based on their anchoring mechanism:

| Category | Description | Name Examples |
|---|---|---|
| **Key-derived** | Identity derived directly from cryptographic keys | `did:key`, `did:pkh`, `did:jwk` |
| **Web-anchored** | Identity anchored to web domains or URLs | `did:web`, `did:webvh` |
| **Ledger-anchored** | Identity anchored to a specific blockchain/ledger | `did:ethr`, `did:sol`, `did:btcr` |
| **Service-anchored** | Identity anchored to a naming service or registry | `did:ens`, `did:dns` |
| **Peer/local** | Identity for direct peer-to-peer or offline use | `did:peer`, `did:self` |
| **DHT-anchored** | Identity anchored to distributed hash tables | `did:dht` |

## Applying This Convention

This convention is a **recommendation**, not a requirement for registration.
The registration process remains mechanical (valid JSON, spec URL, no
conflicts). However, authors are encouraged to consider these guidelines when
choosing a method name, as a descriptive name reduces friction for adoption
and ecosystem integration.
