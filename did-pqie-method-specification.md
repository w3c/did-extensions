# DID Method Specification: did:pqie

**Specification Version:** 1.0.0  
**Status:** Draft — Pending W3C DID Method Registry Submission  
**Authors:** Aadhaar KYC System Team (PQIE Research Group)  
**Date:** 2026-02-25  
**Repository:** https://github.com/pqie/did-method-pqie  
**Context URL:** https://pqie.network/ns/did/v1

---

## Abstract

This paper introduces Post‑Quantum Identity Encryption (PQIE), a fully lattice‑based security layer for Decentralized Identifiers (DIDs) that encrypts entire DID Documents with Ring‑Learning‑With‑Errors (Ring‑LWE) and applies a built‑in homomorphic noise filter. The framework is blockchain‑agnostic: encrypted identities (or their hashes) can be stored on any key‑value ledgers. PQIE is positioned at the intersection of post‑quantum cryptography and self‑sovereign identity. Where traditional DID methods focus on substituting elliptic‑curve keys with lattice signatures, our approach re‑thinks the entire trust pipeline—from key material to on‑chain storage—by insisting that no part of the DID Document ever travels or rests in plaintext.

---

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

Digital identity is rapidly shifting from centralized systems to distributed systems, where users control their own credentials. The W3C Decentralized Identifier (DID) specification decouples identifiers from centralized registries by anchoring them in distributed ledgers. Yet most DID methods still rely on elliptic‑curve cryptography—susceptible to quantum attacks. Blockchain provides an immutable substrate for storing identity proofs, but quantum readiness remains an open gap.

Blockchains introduce an append‑only ledger where every state transition is cryptographically attested. This immutability is attractive to identity systems because it eliminates single points of compromise. However, the transparency of public chains also magnifies privacy risk: metadata correlation attacks can reveal social graphs or user‑credential relationships. 

Self‑Sovereign Identity (SSI) combines DIDs and Verifiable Credentials (VCs) to give individuals agency over how their data are shared. Creating a quantum‑resistant SSI stack requires post‑quantum key generation, end‑to‑end encryption, and efficient noise management. `did:pqie` addresses these needs while remaining ledger‑independent.

PQIE’s strategy of encrypting the entire DID Document mitigates leakage while retaining auditability via on‑chain hash pointers. From an economic perspective, lattice ciphertexts can be bulky, but our homomorphic filtering keeps the encrypted DID payload below 2 kB, minimizing costs over blockchain operations.

---

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

The Post-Quantum Identity Encryption (PQIE) framework ensures that no part of the DID Document ever travels or rests in plaintext. The system is composed of specialized blocks that handle the identity lifecycle:

| Block | Function | Technical Detail |
|-------|----------|------------------|
| **O: User Interface** | Identity Capture | Captures identity data, initiates "Create DID". Sends JSON to back-end. |
| **A: Key Generator** | PQ KeyPair (pk, sk) | Ring-LWE ($n=512, q=24593, \sigma=4.0$). |
| **A: DID Derivation** | Identifer Suffix | `did:pqie:` + `base58(SHA-256(pk)[:16])`. |
| **A: Doc Builder** | W3C DID Document | Assembles JSON-LD. Embeds pk in `verificationMethod`. |
| **A: PQIE Encryptor** | Digital Envelope | Ring-LWE KEM (SS = KEM(pk)) + AES-GCM(SS, Doc). |
| **B: Noise Filter** | Error Management | Homomorphic reduction: $c_i' = c_i \pmod{q/4}$ every 128 ops. |
| **B: Signature** | Non-repudiation | Lattice-based Ring-LWE signature attached to ciphertext. |
| **E: Ledger Writer** | Persistence | Stores ciphertext or hash pointer via Ledger-Agnostic Interface. |
| **F: Resolver** | Lookup & Decrypt | Retrieves $P$ (ciphertext + kem + sig), decapsulates, and verifies. |

---

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

1. **Attribute Lifting**: Map attributes to polynomial $A(x) \in \mathbb{Z}_q[x]/(x^n + 1)$ with Gaussian noise $e$.
2. **NTT Domain Mapping**: Apply Number-Theoretic Transform (NTT) to convert coefficients for efficient convolution: $A_{ntt} = NTT(A)$.
3. **Binding Transform**: Bind attributes to public key $pk_{ntt}$ via coefficient-wise multiplication: $R_{ntt} = A_{ntt} \otimes pk_{ntt}$.
4. **Side-Channel Protection**: Apply pointwise `tanh` activation to disrupt linear patterns: $c_i' = \tanh(\kappa \cdot c_i)$.
5. **Dual-Hash Generation**: Compute primary (SHA3-512) and secondary (Blake2b) digests from the processed result to form the DID string.

---

## 6. Cryptographic Elements

All `did:pqie` operations are run over ideal lattices in $R_q = \mathbb{Z}_q[x]/(x^n + 1)$ where $n=512$ and $q=24593$.

### 6.1 Key Pair Generation (Ring-LWE)

1. **Secret Key ($s$):** Sampled from a zero-centered discrete Gaussian distribution $\sigma \approx 4.0$.
2. **Public Key ($pk$):** Generate uniform $a \in R_q$. Compute $pk = (a, c = a \cdot s + e \pmod{q})$.
3. **Hardness:** Recovering $s$ from $(a, c)$ is as hard as the Shortest Vector Problem (SVP) in cyclotomic lattices.

### 6.2 PQIE Digital Envelope (Encryption)

All `did:pqie` documents are stored as encrypted blobs via a hybrid KEM/AEAD scheme:
1. **SS = KEM(pk)**: Encapsulate shared secret using Ring-LWE KEM.
2. **NTT Domain Ops**: Polynomial multiplications are performed in the NTT domain ($O(n \log n)$) for efficiency.
3. **CT = AES-GCM(SS, Doc)**: The JSON-LD DID Document is encrypted with the derived shared secret.

### 6.3 Lattice Signature (Authentication)

PQIE uses a fiat-shamir-with-abort style signature to ensure authenticity:
1. **Commitment**: Multiply public generator $A$ by fresh random polynomial $y$ (small coefficients). $t = A \cdot y$.
2. **Challenge ($c$):** Hash the document digest and $t$ to form a sparse polynomial $c \in \{-1, 0, 1\}^n$.
3. **Response ($z$):** Compute $z = y + c \cdot s$.
4. **Noise Reduction**: Apply modular inversion (Complexity $O(\log q)$) to keep $z$ within safe spectral bounds.
5. **Verification**: Confirm $A \cdot z - c \cdot pk \approx t$. If the resulting hash matches the challenge $c$ and $\|z\|$ is small, the signature is VALID.

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

### 7.1 Identity Controller Security

The security of a `did:pqie` DID relies on the controller's ability to protect their private Ring-LWE keys.
- **Key Storage**: Controllers SHOULD store private keys in hardware-backed security modules (HSM) or Trusted Execution Environments (TEE).
- **Key Loss**: Loss of the private key results in permanent loss of control over the DID. There is no central authority to recover or reset keys.
- **Key Compromise**: If a private key is compromised, the controller MUST immediately deactivate the DID or rotate keys to a new verification method.

### 7.2 Ledger Security

The `did:pqie` method assumes the underlying ledger (e.g., Hyperledger Indy) provides immutability and censorship resistance.
- **Immutability**: Once a transaction is finalized, it cannot be altered. This prevents history rewriting.
- **Consensus Attacks**: A 51% attack or similar consensus failure on the ledger could lead to the suppression of updates or deactivations.
- **Data Integrity**: The use of IPFS CIDs anchored on the ledger ensures that the document content cannot be tampered with without detection.

### 7.3 Resolver Security

Resolvers MUST ensure they are returning authentic and up-to-date DID documents.
- **Man-in-the-Middle (MITM)**: Resolvers MUST use secure transport (e.g., HTTPS) and verify the lattice signature of the DID document during resolution.
- **Denial of Service (DoS)**: Resolvers MUST implement rate limiting (§7.6) and cache-friendly policies to prevent resource exhaustion.
- **Signature Verification**: A resolver MUST NOT return a DID document that fails signature verification.

### 7.4 Post-Quantum HARDNESS (Ring-LWE)

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

### 7.7 Quantitative Security Analysis

PQIE is designed to provide 256-bit quantum security, exceeding the requirements of many standard NIST candidates. The following table compares PQIE-Enc parameters with other post-quantum schemes:

| Scheme | $n$ | $q$ | Quantum Bit‑Security |
|--------|-----|-----|----------------------|
| **PQIE-Enc** | 512 | 24577 | 256 |
| Dilithium‑III | 256 | 8380417 | 192 |
| Falcon‑512 | 512 | 12289 | 128 |

---

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

### 8.5 Selective Disclosure

PQIE optionally supports selective disclosure using a Merkle-commitment scheme for Verifiable Credentials. Claims are hashed into the leaves of a Merkle tree, and only the root commitment is signed. Credential holders can provide Merkle proofs for specific claims without revealing the entire dataset, following [W3C VC Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/) privacy-by-design principles.

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
- [PQIE: A Ledger‑Agnostic Framework for Secure DIDs](https://pqie.network/papers/pqie-framework.pdf)
