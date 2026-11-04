# DID Ecosystem Repository Map

A comprehensive map of all active repositories across the W3C, W3C Credentials
Community Group, and Decentralized Identity Foundation related to Decentralized
Identifiers.

## Supersession Chains

Before diving into the current repositories, be aware that several repositories
have been renamed or superseded:

| Old Repository | Current Repository | Notes |
|---|---|---|
| `w3c/did-core` | [w3c/did](https://github.com/w3c/did) | Renamed |
| `w3c/did-spec-registries` | [w3c/did-extensions](https://github.com/w3c/did-extensions) | Renamed |
| `w3c-ccg/did-method-registry` | [w3c/did-extensions](https://github.com/w3c/did-extensions) | Archived → superseded |
| `w3c-ccg/did-spec` | [w3c/did](https://github.com/w3c/did) | Archived → superseded |
| `w3c-ccg/did-test-suite` | [w3c/did-test-suite](https://github.com/w3c/did-test-suite) | Archived → superseded |
| `w3c-ccg/did-use-cases` | [w3c/did-use-cases](https://github.com/w3c/did-use-cases) | Archived → superseded |
| `decentralized-identity/did-tdw` | [decentralized-identity/didwebvh](https://github.com/decentralized-identity/didwebvh) | Renamed (did:tdw → did:webvh) |

## W3C Working Group (`w3c/`)

### Specifications

| Repository | Document Type | Rendered Spec | Description |
|---|---|---|---|
| [did](https://github.com/w3c/did) | Recommendation | [DID Core v1.0](https://www.w3.org/TR/did-core/) | The core DID data model, syntax, and conformance requirements |
| [did-resolution](https://github.com/w3c/did-resolution) | Working Draft | [DID Resolution v0.2](https://www.w3.org/TR/did-resolution/) | How DIDs are resolved to DID Documents |
| [did-use-cases](https://github.com/w3c/did-use-cases) | WG Note | [Use Cases & Requirements](https://www.w3.org/TR/did-use-cases/) | 18 use cases and 22 requirements for DIDs |
| [did-imp-guide](https://github.com/w3c/did-imp-guide) | WG Note | [Implementation Guide](https://www.w3.org/TR/did-imp-guide/) | Practical guidance for DID implementers |
| [did-cbor-note](https://github.com/w3c/did-cbor-note) | WG Note | — | CBOR representation of DID Documents (stale since 2021) |

### Evaluation & Testing

| Repository | Purpose | Rendered |
|---|---|---|
| [did-rubric](https://github.com/w3c/did-rubric) | 36 evaluation criteria across 8 categories for assessing DID methods | [DID Rubric v1.0](https://www.w3.org/TR/did-rubric/) |
| [did-test-suite](https://github.com/w3c/did-test-suite) | Conformance test suite and implementation report for DID Core | [Test Report](https://w3c.github.io/did-test-suite/) |
| [did-resolution-threat-model](https://github.com/w3c/did-resolution-threat-model) | Threat model analysis for DID Resolution | — |

### Registry

| Repository | Purpose | Rendered |
|---|---|---|
| [did-extensions](https://github.com/w3c/did-extensions) | Registry of DID methods, properties, resolution metadata, and vocabularies | [DID Extensions](https://w3c.github.io/did-extensions/) |

### Governance

| Repository | Purpose |
|---|---|
| [did-wg](https://github.com/w3c/did-wg) | Working Group home page, meeting minutes, administration |
| [did-wg-charter](https://github.com/w3c/did-wg-charter) | Current DID Working Group charter |
| [did-methods-wg-charter](https://github.com/w3c/did-methods-wg-charter) | Proposed new WG specifically for evaluating and standardizing DID methods |

## W3C Credentials Community Group (`w3c-ccg/`)

### Active Method Specifications

| Repository | Method | Description |
|---|---|---|
| [did-key-spec](https://github.com/w3c-ccg/did-key-spec) | `did:key` | Ephemeral/static key pair DIDs (ledger-independent) |
| [did-method-web](https://github.com/w3c-ccg/did-method-web) | `did:web` | HTTPS domain-based DIDs (likely migrating to WG) |
| [did-pkh](https://github.com/w3c-ccg/did-pkh) | `did:pkh` | Blockchain public key hash DIDs |
| [did-cel-spec](https://github.com/w3c-ccg/did-cel-spec) | `did:cel` | Cryptographic Event Log DIDs |
| [did-linked-resources](https://github.com/w3c-ccg/did-linked-resources) | — | DID-Linked Resources specification |

### Testing & Education

| Repository | Purpose |
|---|---|
| [did-key-test-suite](https://github.com/w3c-ccg/did-key-test-suite) | Test suite for did:key interoperability |
| [did-resolution-mocha-test-suite](https://github.com/w3c-ccg/did-resolution-mocha-test-suite) | Mocha-based test suite for DID Resolution compliance |
| [did-primer](https://github.com/w3c-ccg/did-primer) | Educational primer on DIDs (stale since 2021) |

## Decentralized Identity Foundation (`decentralized-identity/`)

### Specifications

| Repository | Purpose |
|---|---|
| [didcomm-messaging](https://github.com/decentralized-identity/didcomm-messaging) | DIDComm v2 specification — DID-based encrypted messaging protocol |
| [did-registration](https://github.com/decentralized-identity/did-registration) | Specification for DID create/update/deactivate operations |
| [didwebvh](https://github.com/decentralized-identity/didwebvh) | did:web + Verifiable History specification (formerly did:tdw) |
| [did-dht](https://github.com/decentralized-identity/did-dht) | did:dht method specification (Distributed Hash Table) |
| [well-known-did-configuration](https://github.com/decentralized-identity/well-known-did-configuration) | Specification for DID /.well-known resources |

### Libraries & Tools

| Repository | Language | Purpose |
|---|---|---|
| [universal-resolver](https://github.com/decentralized-identity/universal-resolver) | Java | Universal DID Resolver — unified HTTP API for resolving any DID method |
| [did-resolver](https://github.com/decentralized-identity/did-resolver) | JavaScript | Universal did-resolver interface library |
| [did-jwt](https://github.com/decentralized-identity/did-jwt) | JavaScript | Create and verify DID-based JWTs |
| [did-jwt-vc](https://github.com/decentralized-identity/did-jwt-vc) | JavaScript | W3C Verifiable Credentials/Presentations in JWT format |
| [did-common-java](https://github.com/decentralized-identity/did-common-java) | Java | Common DID operations library |
| [did-key.rs](https://github.com/decentralized-identity/did-key.rs) | Rust | did:key implementation |
| [ethr-did-resolver](https://github.com/decentralized-identity/ethr-did-resolver) | JavaScript | DID resolver driver for did:ethr |
| [web-did-resolver](https://github.com/decentralized-identity/web-did-resolver) | JavaScript | DID resolver driver for did:web |
| [didwebvh-ts](https://github.com/decentralized-identity/didwebvh-ts) | TypeScript | did:webvh implementation |
| [didwebvh-rs](https://github.com/decentralized-identity/didwebvh-rs) | Rust | did:webvh implementation |
| [veramo](https://github.com/decentralized-identity/veramo) | JavaScript | Veramo framework for Verifiable Data (DIDs, VCs) |

### Governance & Evaluation

| Repository | Purpose |
|---|---|
| [did-methods](https://github.com/decentralized-identity/did-methods) | DID Methods Working Group — method evaluation and standardization |
| [did-traits](https://github.com/decentralized-identity/did-traits) | DID Traits — characterizing DID method properties |
| [did-spec-extensions](https://github.com/decentralized-identity/did-spec-extensions) | Extension parameters and properties for DID spec registries |
