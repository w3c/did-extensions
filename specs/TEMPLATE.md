# did:<method-name> — DID Method Specification

> **One-line description:** _What this method does and where it anchors identity._

| Field | Value |
|---|---|
| Method Name | `did:<method-name>` |
| Specification Version | v0.1.0 |
| Status | Provisional |
| Category | _key-derived / web-anchored / ledger-anchored / service-anchored / peer-local / dht-anchored_ |
| Verifiable Data Registry | _e.g., Ethereum, Solana, Web, IPFS_ |
| Implementations | _count + links_ |
| Test Coverage | _N tests, N failures_ |

## Sections

This specification follows the [W3C DID Extensions standard template](../specs/TEMPLATE.md).
Sections marked **REQUIRED** must be present for registration. Sections marked
**RECOMMENDED** are expected for well-documented methods. **OPTIONAL** sections
depend on the method's complexity.

| # | Section | Status | Description |
|---|---------|--------|-------------|
| 1 | [Abstract](#1-abstract) | REQUIRED | What is this method — one paragraph |
| 2 | [Use Case & Requirements](#2-use-case--requirements) | REQUIRED | Target use case, identity tiers, requirement coverage |
| 3 | [DID Syntax](#3-did-syntax) | REQUIRED | ABNF grammar, method-specific identifier format |
| 4 | [DID Document](#4-did-document) | REQUIRED | Example DID Documents for each identity tier |
| 5 | [CRUD Operations](#5-crud-operations) | REQUIRED | Create, Resolve, Update, Deactivate |
| 6 | [Security Considerations](#6-security-considerations) | REQUIRED | Threat model, cryptographic guarantees |
| 7 | [Privacy Considerations](#7-privacy-considerations) | REQUIRED | PII exposure, correlation risks, mitigations |
| 8 | [Trust Model](#8-trust-model) | RECOMMENDED | Trust hierarchy, anchor points, grading |
| 9 | [Interoperability](#9-interoperability) | RECOMMENDED | Universal Resolver, SDK support, protocol compatibility |
| 10 | [Architectural Rationale](#10-architectural-rationale) | RECOMMENDED | Why this design — trade-offs, comparisons |
| 11 | [W3C Requirements Coverage](#11-w3c-requirements-coverage) | RECOMMENDED | Coverage matrix against 22 W3C requirements |
| 12 | [Metadata Schema](#12-metadata-schema) | OPTIONAL | On-chain/storage layout, flags, versioning |
| 13 | [Implementation Notes](#13-implementation-notes) | OPTIONAL | Method-specific integration details |
| 14 | [References](#14-references) | REQUIRED | W3C, IETF, and other normative/informative references |

---

## 1. Abstract

_One paragraph: what is this DID method, what problem does it solve, and what
makes it different from existing methods._

<!-- Example from did:sns:
The `did:sns` method binds W3C Decentralized Identifiers to human-readable
.sol domain aliases — enabling institutions, fintechs, and regulated entities
to issue, verify, and present identity credentials across jurisdictions and
blockchains.
-->

## 2. Use Case & Requirements

### Primary Use Case

_Describe the focal use case this method targets. Reference the
[W3C Use Cases](https://www.w3.org/TR/did-use-cases/) where applicable._

<!-- Example: Multi-issuer regulated identity for financial compliance -->

### Identity Tiers

_If your method supports multiple levels of identity assurance, define them here._

| Tier | Name | Description | Anchoring |
|---|---|---|---|
| 1 | _Basic_ | _Description_ | _Where/how_ |
| 2 | _Enhanced_ | _Description_ | _Where/how_ |

### Requirement Coverage

_Map your method against the [22 W3C DID requirements](https://www.w3.org/TR/did-use-cases/#requirements).
Use the self-assessment from your [method registration JSON](../methods/)._

| Requirement | Tier | Status | Detail |
|---|---|---|---|
| Decentralization | Core | _covered/partial/uncovered_ | _How_ |
| Control | Core | _covered/partial/uncovered_ | _How_ |
| ... | ... | ... | ... |

## 3. DID Syntax

### Method Name

```
did:method-name
```

### Method-Specific Identifier

_Define the ABNF grammar for your method-specific identifier._

```abnf
method-specific-id = *( unreserved / pct-encoded )
```

### Examples

```
did:<method>:example-identifier-1
did:<method>:example-identifier-2
```

## 4. DID Document

### Example: Basic DID Document

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/suites/ed25519-2020/v1"
  ],
  "id": "did:<method>:example",
  "verificationMethod": [{
    "id": "did:<method>:example#key-1",
    "type": "Ed25519VerificationMethod2020",
    "controller": "did:<method>:example",
    "publicKeyMultibase": "z6Mk..."
  }],
  "authentication": ["did:<method>:example#key-1"],
  "assertionMethod": ["did:<method>:example#key-1"]
}
```

_Add additional examples for each identity tier or use case variant._

## 5. CRUD Operations

### Create

_How is a DID created? What are the inputs, outputs, and side effects?_

### Read (Resolve)

_How is a DID resolved to a DID Document? What is the resolution protocol?_

**Resolution Input:**
```
did:<method>:example
```

**Resolution Output:**
```json
{
  "didDocument": { },
  "didDocumentMetadata": {
    "created": "2026-01-01T00:00:00Z",
    "updated": "2026-03-01T00:00:00Z"
  },
  "didResolutionMetadata": {
    "contentType": "application/did+ld+json"
  }
}
```

### Update

_How is a DID Document updated? Who is authorized to update?_

### Deactivate

_How is a DID deactivated? What does resolution return after deactivation?_

## 6. Security Considerations

_Address at minimum:_

- **Authentication:** How is the DID controller authenticated?
- **Authorization:** Who can perform CRUD operations?
- **Integrity:** How is DID Document integrity guaranteed?
- **Confidentiality:** What information is exposed during resolution?
- **Cryptographic Algorithms:** What algorithms are supported? Migration plan?
- **Key Compromise:** What happens if keys are compromised?
- **Denial of Service:** How resilient is resolution to DoS?

## 7. Privacy Considerations

_Address at minimum:_

- **Surveillance:** Can resolution be monitored?
- **Correlation:** Can multiple DIDs be linked to the same entity?
- **PII Exposure:** What personal information is in the DID Document?
- **Data Minimization:** How does the method minimize data exposure?
- **Right to be Forgotten:** Can a DID be fully removed?

## 8. Trust Model

_RECOMMENDED: Define the trust hierarchy and anchor points._

| Model | Description | Trust Anchor |
|---|---|---|
| _A_ | _Description_ | _What provides trust_ |
| _B_ | _Description_ | _What provides trust_ |

## 9. Interoperability

_RECOMMENDED: Document compatibility with the ecosystem._

| Component | Status | Notes |
|---|---|---|
| Universal Resolver | _Driver available / Planned / N/A_ | _Link_ |
| DIDComm v2 | _Supported / Planned / N/A_ | |
| Verifiable Credentials | _Supported / Planned / N/A_ | |
| SD-JWT | _Supported / Planned / N/A_ | |
| _Framework (Veramo, Credo, etc.)_ | _Supported / Planned / N/A_ | |

## 10. Architectural Rationale

_RECOMMENDED: Explain why this design was chosen. Compare with alternatives.
Document trade-offs._

## 11. W3C Requirements Coverage

_RECOMMENDED: Full matrix against 22 W3C requirements. This can reference
the requirements section in the method registration JSON._

## 12. Metadata Schema

_OPTIONAL: If your method uses on-chain storage, binary layouts, or custom
metadata formats, define them here._

## 13. Implementation Notes

_OPTIONAL: Method-specific integration details, SDK usage, deployment notes._

### Reference Implementation

| Component | Language | Repository |
|---|---|---|
| _Resolver_ | _TypeScript_ | _Link_ |
| _Driver_ | _Java_ | _Link_ |

## 14. References

### Normative References

- [DID Core v1.0](https://www.w3.org/TR/did-core/) — W3C Recommendation
- [DID Resolution](https://www.w3.org/TR/did-resolution/) — W3C Working Draft

### Informative References

- [DID Use Cases and Requirements](https://www.w3.org/TR/did-use-cases/) — W3C Note
- [DID Rubric v1.0](https://www.w3.org/TR/did-rubric/) — W3C Note
- [DID Implementation Guide](https://www.w3.org/TR/did-imp-guide/) — W3C Note
