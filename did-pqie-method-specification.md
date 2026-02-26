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

## 7. CRUD Operations

### 7.1 Create

**Prerequisites:** Citizen has provided personal attributes for KYC and a post-quantum public key has been generated.

**Steps:**

1. **Generate identifier** using the algorithm in §5.2.
2. **Generate key pair** `(pk, sk)` using Ring-LWE keypair generation based on the Kyber-1024 parameters.
3. **Build DID Document** containing the public key and initial service endpoints.
4. **Sign and Encrypt**: Use the Lattice Signature (§6.2) and Digital Envelope (§6.1) to protect the document.
5. **Upload to IPFS**: The encrypted ciphertext package $P$ is uploaded to IPFS.
6. **Submit NYM transaction**: The `did:pqie` identifier, public key hash, and IPFS CID are submitted to the Hyperledger Indy ledger.

---

### 7.2 Read (Resolve)

**A `did:pqie` DID resolution involves the following verification flow:**

1. **Fetch**: Query the ledger for the `ipfs_cid` associated with the DID.
2. **Retrieve**: Fetch the encrypted package $P$ (ciphertext, kem, sig) from IPFS.
3. **Decapsulate**: Use the subject's public key $pk$ to recover the shared secret $SS = Decap(pk, kem)$.
4. **Decrypt**: Derive $key = HKDF(SS)$ and decrypt the ciphertext to reveal the JSON-LD DID Document.
5. **Verify**: Compute the digest of the decrypted doc and verify the lattice signature $sig$ against $sig\_pub$.
6. **Integrity**: Ensure the document ID matches the requested DID.

**Resolution Result:**
The resolver returns the decrypted W3C DID Document and metadata.

---

### 7.3 Update

**Authorization:** Updates MUST be authorized by the DID subject via a cryptographic challenge-response.

**Update Process:**
1. **Authentication**: Subject proves ownership via signature.
2. **Modification**: Desired changes are applied to the decrypted document.
3. **Re-encryption**: The updated document is re-encoded into a new Digital Envelope.
4. **Ledger Update**: Submit an `ATTRIB` transaction with the new IPFS CID.
5. **State Transition**: Ledger transitions from $S_n \rightarrow S_{n+1}$.

---

### 7.4 Deactivate

**Authorization:** Terminal deactivation requires an authorized government mandate or subject retirement.

**Process:**
1. **Revocation Request**: Submit signed deactivation request.
2. **Ledger Transaction**: Send `DID_DEACTIVATE` transaction.
3. **Terminal State**: Once deactivated, a DID is cryptographically invalid for all compliant verifiers.

---

## 8. Security Considerations

## 8. Security Considerations

### 8.1 Post-Quantum Security

The `did:pqie` method derives its security from the **Ring Learning With Errors (Ring-LWE)** problem. The hardness of Ring-LWE is equivalent to worst-case hard problems on ideal lattices, providing IND-CPA security.

- **Security level:** 128-bit post-quantum (equivalent to 256-bit classical security).
- **Algorithm family:** MODULE-LWE (based on the CRYSTALS-Kyber submission to NIST).
- **Key sizes:** 1024-byte public keys and 1632-byte secret keys (Kyber-1024 parameters).

### 8.2 Key Management and Protection

Private keys for `did:pqie` must be handled with extreme care, as they represent the ultimate authority over the identity.
- **Secure Enclaves**: Implementations SHOULD use Hardware Security Modules (HSMs) or Secure Enclaves (e.g., Apple T2, Android StrongBox) for key generation and storage.
- **Side-Channel Protections**: The cryptographic implementation uses constant-time polynomial arithmetic to mitigate timing attacks. The `_tanh_activation` step further obfuscates power traces.
- **Key Rotation**: Subjects MUST rotate keys if a compromise is suspected.

### 8.3 Data Availability and Persistence

Since the DID Document is stored on IPFS, its availability depends on content being pinned.
- **Pinning Services**: Government nodes and authorized registrars MUST pin DID Documents.
- **Ledger Anchoring**: The Hyperledger Indy ledger acts as a permanent, immutable index.

### 8.4 Denial of Service (DoS)

Method-specific resolvers MUST implement rate limiting to prevent infrastructure exhaustion.
- **Resolver Limits**: Public resolvers SHOULD limit requests based on IP or authenticated subject.
- **Ledger Protection**: Hyperledger Indy's consensus mechanism naturally limits transaction volume.

### 8.5 Data Forgery Prevention

The `did:pqie` method prevents forgery through post-quantum lattice signatures. Only the controller of the DID can authorize updates or deactivations.

### 8.6 Cryptographic Agility

The specification supports cryptographic agility. While Kyber-1024 is the current default, the `latticeParams` field allows for future NIST-standardized lattice algorithms.

### 8.7 Security Margin Comparison

| Scheme | n | q | Quantum Bit-Security |
|--------|---|---|----------------------|
| **PQIE-Enc** | 512 | 24577 | 256 |
| Dilithium-III | 256 | 8380417 | 192 |
| Falcon-512 | 512 | 12289 | 128 |

---

## 9. Privacy Considerations

### 9.1 Minimal PII and Metadata Leakage

DID Documents for `did:pqie` MUST NOT contain raw Aadhaar numbers or biometric data.
- **Content Minimization**: Only verification methods and service endpoints are stored.
- **Metadata Protection**: Infrastructure providers SHOULD anonymize access logs.

### 9.2 Gaussian Noise and Obfuscation

The transformation of citizen attributes into the DID identifier uses Gaussian noise masking (σ=4.0). This ensures identifier unlinkability to the underlying PII.

### 9.3 Surveillance and Correlation

Resolver implementations SHOULD mitigate surveillance risks by:
- **No-Phone-Home**: Resolvers SHOULD NOT report resolution activity.
- **Pairwise DIDs**: Subjects SHOULD use distinct DIDs for different service providers.
- **Selective Disclosure**: Verifiable Presentations SHOULD be used.

### 9.4 Stored Data Compromise

While the ledger is public, it only contains public keys and IPFS CIDs. A compromise of the ledger does not reveal PII.

### 9.5 Right to Erasure (GDPR Art. 17)

Deactivation (§7.4) provides a logical "Right to Erasure." While the ledger is immutable, a deactivated DID is cryptographically invalid.

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
