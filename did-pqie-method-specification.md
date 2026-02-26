# DID Method Specification: did:pqie

**Specification Version:** 1.0.0  
**Status:** Draft — Pending W3C DID Method Registry Submission  
**Authors:** Aadhaar KYC System Team (PQIE Research Group)  
**Date:** 2026-02-25  
**Repository:** https://github.com/pqie/did-method-pqie  
**Context URL:** https://pqie.network/ns/did/v1

---

## Abstract

This document defines the `did:pqie` DID method — a **Post-Quantum Identity Encryption** Decentralized Identifier method. It provides quantum-safe digital identity management using **Ring-LWE lattice cryptography** (Kyber-1024 compatible), dual-hash identifier generation (SHA-3-512 + Blake2b), and cross-blockchain ledger support. It is designed for national-scale identity systems (e.g., Aadhaar KYC) requiring cryptographic agility against quantum adversaries.

---

## Status of This Document

This is a **Working Draft** of the `did:pqie` DID method specification. It is being submitted for inclusion in the [W3C DID Method Registry](https://w3c.github.io/did-spec-registries/).

Conformance with the [W3C DID Core Specification](https://www.w3.org/TR/did-core/) is the normative baseline for this document.

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Terminology](#2-terminology)
3. [PQIE Architecture Overview](#3-pqie-architecture-overview)
4. [DID Method Name](#4-did-method-name)
5. [Method-Specific Identifier](#5-method-specific-identifier)
6. [CRUD Operations](#6-crud-operations)
   - 6.1 [Create](#61-create)
   - 6.2 [Read (Resolve)](#62-read-resolve)
   - 6.3 [Update](#63-update)
   - 6.4 [Deactivate](#64-deactivate)
7. [Security Considerations](#7-security-considerations)
8. [Privacy Considerations](#8-privacy-considerations)
9. [JSON-LD Context](#9-json-ld-context)
10. [Example DID Document](#10-example-did-document)
11. [Implementation Status](#11-implementation-status)
12. [References](#12-references)

---

## 1. Introduction

The `did:pqie` method addresses the growing need for **post-quantum-safe** digital identity infrastructure. As quantum computers advance toward breaking RSA and ECDSA, identity systems must migrate to lattice-based alternatives. `did:pqie` provides:

- **Quantum resistance:** Ring-LWE hardness assumption (equivalent to shortest vector problem on ideal lattices)
- **Layered redundancy:** Dual SHA-3-512 / Blake2b hash generation for collision resistance
- **Cross-chain support:** Single DID resolvable across Hyperledger Indy, Ethereum, and Fabric ledgers
- **IPFS-backed DID Documents:** Content-addressed, immutable DID document storage
- **Verifiable Credentials integration:** Native support for W3C VC Data Model 2.0 embedded in DID Documents
- **Aadhaar KYC compatibility:** Designed for India's national identity infrastructure

---

## 2. Terminology

| Term | Definition |
|------|------------|
| **PQIE** | Post-Quantum Identity Encryption — the Ring-LWE based cryptographic framework |
| **Ring-LWE** | Ring Learning With Errors — a lattice-based cryptographic hard problem |
| **NTT** | Number Theoretic Transform — acceleration for polynomial multiplication |
| **Digital Envelope** | KEM-based encryption where a shared secret protects a symmetric payload |
| **Noise Filter** | Homomorphic process to keep lattice error growth within manageable bounds |
| **Lattice signature** | Quantum-resistant signature based on Shortest Vector Problem (SVP) |

---

## 3. PQIE Architecture Overview

The Post-Quantum Identity Encryption (PQIE) framework ensures that no part of the DID Document ever travels or rests in plaintext.

1.  **Ring-LWE Engine**: Polynomial arithmetic and NTT transforms.
2.  **PQIE Encryption Layer**: "Digital Envelope" system for DID Documents (KEM + AES-GCM).
3.  **Homomorphic Noise-Filtering Layer**: Maintains payload efficiency via $c' = c \pmod{q/4}$ logic.
4.  **Ledger-Agnostic Interface**: Anchors encrypted packages to any key-value ledger.

---

## 4. DID Method Name

The namestring that identifies this DID method SHALL be: `pqie`

A DID that uses this method MUST begin with the following prefix: `did:pqie:`.

---

## 5. Method-Specific Identifier

The `did:pqie` identifier is derived from citizen attributes via the PQIE pipeline.

### 5.1 Syntax

```abnf
did-pqie    = "did:pqie:" primary-hash ":" secondary-hash ":" entropy-suffix
primary-hash   = 8HEXDIG
secondary-hash = 8HEXDIG
entropy-suffix = 8HEXDIG
```

### 5.2 Identifier Generation Algorithm

1. **Attribute Lifting**: Map attributes to polynomial $A(x)$ with Gaussian noise $e$.
2. **Ring-LWE Binding**: Bind to public key $pk$ via NTT convolution: $R_{ntt} = A_{ntt} \circ pk_{ntt}$.
3. **Non-linear Activation**: Apply `tanh` to ensure side-channel resistance.
4. **Dual-Hash**: Primary (SHA3-512) and Secondary (Blake2b) hex prefixes.

---

## 6. Cryptographic Elements

### 6.1 PQIE Digital Envelope (Encryption)

All `did:pqie` documents are stored as encrypted blobs:
1. **SS = KEM(pk)**: Encapsulate shared secret using the subject's Ring-LWE public key.
2. **CT = AES-GCM(SS, Doc)**: Encrypt the DID Document with the derived secret.

### 6.2 Lattice Signature (Authentication)

1. **Commitment**: Multiply public generator $A$ by random secret $y$.
2. **Challenge**: $c = Hash(digest || A \cdot y)$.
3. **Response**: $z = y + c \cdot s$.
4. **Verification**: $A \cdot z - c \cdot pk \approx$ challenge commitment.

---

## 6. CRUD Operations

This section defines the operations for managing `did:pqie` Decentralized Identifiers. All operations MUST be performed through a compliant PQIE-Client to ensure cryptographic integrity.

### 6.1 Create (Register)

Creating a `did:pqie` DID involves binding citizen attributes to a lattice-based identifier.

1.  **Attribute Preparation**: The controller provides a set of identity attributes (e.g., name, birth year). These are MUST be transformed into a polynomial $A(x) \in \mathbb{Z}_q[x]/(x^n + 1)$ using the PQIE lifting process.
2.  **Key Generation**: A Ring-LWE key pair $(pk, sk)$ MUST be generated using Kyber-1024 parameters ($n=512, q=24593$).
3.  **Identifier Derivation**: The identifier is generated via $H(A(x) \circ pk_{ntt})$. This process is binding and irreversible.
4.  **Document Construction**: A W3C-conformant DID Document is created, containing the public key $pk$. 
5.  **Digital Envelope**: The document MUST be encrypted using the Digital Envelope process (§6.1). A shared secret $SS$ is generated, and the document is encrypted with AES-256-GCM.
6.  **Ledger Submission**: The following metadata MUST be submitted to the ledger as a **NYM transaction** (for Hyperledger Indy):
    - `id`: The `did:pqie` identifier.
    - `public_key`: The Ring-LWE public key.
    - `ipfs_cid`: The CID of the encrypted Digital Envelope on IPFS.
    - `timestamp`: The creation time.

### 6.2 Read (Resolve)

A `did:pqie` DID resolution returns a W3C DID Resolution Result containing the `didDocument`, `didResolutionMetadata`, and `didDocumentMetadata`.

**Resolution Logic:**
1.  **Registry Lookup**: The resolver tries to resolve via a local **DID Registry** cache first.
2.  **Documents Store**: If not in cache, it checks the **DID Documents store**.
3.  **Registration Fallback**: If still not found, it falls back to querying the ledger (Hyperledger Indy).
4.  **Fetch**: Retrieve the encrypted package $P$ from IPFS using the anchored `ipfs_cid`.
5.  **Decapsulate**: Recover the shared secret $SS$ using the subject's public key or decapsulation key.
6.  **Decrypt**: Decrypt the JSON-LD document. If decryption fails, return a `securityError`.
7.  **Verify**: Verify the lattice signature.
8.  **Metadata Enrichment**: Attach `didDocumentMetadata` (e.g., `versionId`, `created`, `updated`).

**Universal Resolver Interface:**
Compliant resolvers MUST support the Universal Resolver API:
`GET /1.0/identifiers/{did}`

**Error Handling:**
| Error Code | Meaning |
|------------|---------|
| `invalidDid` | The DID string does not follow the `did:pqie` ABNF. |
| `notFound` | No registration found for this DID on the ledger. |
| `securityError` | Decryption or signature verification failed. |
| `deactivated` | The DID has been permanently revoked. |

### 6.3 Update

**Authorization:** Any update to a `did:pqie` document MUST be signed by the controller's private key. In cases where multiple controllers are defined, $M$-of-$N$ signatures SHOULD be required.

**Update Process:**
1.  **Modification**: An **authenticated partial update** is requested by the controller.
2.  **Versioning**: The `versionId` property MUST be incremented in the document.
3.  **Re-encryption**: The updated document is re-encrypted into a new Digital Envelope.
4.  **IPFS Upload**: The new package is uploaded to IPFS.
5.  **Ledger Update**: A **DID_UPDATE** (or `ATTRIB`) transaction is written to the ledger, anchoring the new `ipfs_cid`.
6.  **Consistency**: Resolvers MUST return the latest version by default.

### 6.4 Deactivate

**Authorization**: Deactivation is a terminal operation. It MUST be authorized by the **Government authority** or the primary controller.

1.  **Revocation Request**: A signed deactivation transaction is submitted to the ledger.
2.  **Registry Update**: The Registry marks the DID state as `DEACTIVATED` (deactivated: true).
3.  **Credential Revocation**: All associated Verifiable Credentials for this DID MUST be revoked.
4.  **Verification**: Subsequent resolution results MUST return a DID document with `deactivated: true`.
5.  **Irreversibility**: A deactivated `did:pqie` DID CANNOT be updated or re-activated.

---

## 7. Security Considerations

This section addresses the requirements of [DID-CORE] Section 7.1 and follows [RFC3552] guidelines.

### 7.1 Post-Quantum HARDNESS (Ring-LWE)

The core security of `did:pqie` relies on the Ring Learning With Errors (Ring-LWE) problem. Unlike RSA or ECC, which are vulnerable to Shor's algorithm, lattice-based problems remain hard for both classical and quantum adversaries. 
- **Quantum Bit-Security**: 256 bits for Kyber-1024 parameters.
- **Side-Channel Mitigation**: Implementations MUST use constant-time polynomial multiplication (NTT) to prevent timing attacks. The inclusion of the `_tanh_activation` function provides a non-linear layer that complicates power analysis attacks.

### 7.2 Key Management

Secure handling of private keys is critical.
- **Storage**: Controllers SHOULD store private keys in hardware-backed security modules (HSM) or Trusted Execution Environments (TEE).
- **Public Key Handling**: Public keys for `did:pqie` are larger than ECDSA keys (~1.2KB). Network protocols MUST accommodate these larger payloads.
- **Rotation**: Controllers SHOULD rotate keys periodically. Since `did:pqie` identifiers are tied to attributes and the initial public key, rotation is handled by adding new verification methods while preserving the DID identifier.

### 7.3 Replay Attacks

Every transaction (Update, Deactivate) MUST include a unique nonce and a reference to the previous `versionId`. Ledger nodes MUST reject any transaction that attempts to re-apply a previous state or uses a stale version identifier.

### 7.4 Data Integrity and Forgery

The use of IPFS CIDs ensures data integrity. If even a single bit of the encrypted DID Document is changed, the CID will no longer match the ledger's anchor, flagging a security violation. Lattice signatures provide non-repudiation, ensuring only the controller could have produced the update.

### 7.5 Cryptographic Agility

While the current specification defaults to Ring-LWE (Kyber-compatible), the `latticeParams` field in the DID document allows for a managed transition to future NIST-approved algorithms without changing the fundamental method structure.

### 7.6 Rate Limiting

To prevent DoS attacks on shared resolvers and ledger interfaces, implementers MUST enforce rate limiting. The default policy is:
**5 tokens/hour/user** (or requests/hour/IP).

---

## 8. Privacy Considerations

### 8.1 Minimal Disclosure and PII

The `did:pqie` method is designed for privacy-preserving KYC. 
- **PII Protection**: Raw PII (e.g., Aadhaar number) NEVER appears in the DID Document or on the ledger. 
- **Gaussian Blurring**: The attribute-to-polynomial mapping adds Gaussian noise ($\sigma=4.0$), ensuring that the resulting polynomial $A(x)$ is computationally indistinguishable from a random polynomial to anyone without the secret key.

### 8.2 Correlation and Tracking

Multi-ledger and multi-DID strategies are encouraged to prevent correlation.
- **Pairwise DIDs**: Users SHOULD generate unique DIDs for different service providers to prevent cross-service tracking.
- **Metadata Anonymity**: Ledger nodes SHOULD NOT log the IP addresses of parties performing resolution to prevent geographical tracking.

### 8.3 Observation and Surveillance

The "Encrypted-by-Default" nature of `did:pqie` DID Documents prevents passive observers (e.g., IPFS nodes, ISP) from reading the content of the DID Document. Only the authorized resolver or controller can peek inside the "Digital Envelope."

### 8.4 Right to Erasure

Aligning with GDPR Article 17, `did:pqie` supports deactivation. While the ledger record is immutable, the deactivation makes the DID cryptographically useless. Controllers wishing to achieve complete erasure MUST ensure they un-pin and remove their content from IPFS nodes they control.

---

## 10. JSON-LD Context

The `did:pqie` method defines the following custom JSON-LD context:

```json
{
  "@context": {
    "pqie": "https://pqie.network/ns/did/v1#",
    "publicKeyLattice": "pqie:publicKeyLattice",
    "latticeParams": "pqie:latticeParams"
  }
}
```

---

## 11. Example DID Document

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://pqie.network/ns/did/v1"
  ],
  "id": "did:pqie:5135e697:8b7ecf94:a3f21bc0",
  "verificationMethod": [{
    "id": "did:pqie:5135e697:8b7ecf94:a3f21bc0#key-1",
    "type": "PQIE-RingLWE2024",
    "controller": "did:pqie:5135e697:8b7ecf94:a3f21bc0",
    "publicKeyLattice": "AAAA...",
    "latticeParams": { "n": 512, "q": 24593 }
  }],
  "authentication": ["did:pqie:5135e697:8b7ecf94:a3f21bc0#key-1"],
  "service": [{
    "id": "did:pqie:5135e697:8b7ecf94:a3f21bc0#storage",
    "type": "EncryptedDIDService",
    "serviceEndpoint": "https://ipfs.io/ipfs/Qm..."
  }],
  "versionId": "1"
}
```

---

## 12. Implementation Status

| Block | Function | Status |
|-------|----------|--------|
| **A: KeyGen** | Ring-LWE Key Generator | ✅ |
| **A: DID Deriv** | Identifier Derivation | ✅ |
| **A: PQIE Enc** | Digital Envelope Encryption | ✅ |
| **B: Noise Filter** | Homomorphic Operations | ✅ |
| **B: Signature** | Lattice Authentication | ✅ |
| **E: Ledger Writer** | Indy/Blockchain Interface | ✅ |
| **F: Resolver** | Decapsulate & Verify | ✅ |

---

## 13. References

- [W3C DID Core Specification](https://www.w3.org/TR/did-core/)
- [W3C DID Method Registry](https://w3c.github.io/did-spec-registries/)
- [NIST PQC Standards](https://csrc.nist.gov/projects/post-quantum-cryptography)
- [Ring-LWE Problem Analysis](https://eprint.iacr.org/2012/230)
