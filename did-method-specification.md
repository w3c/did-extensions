# DID Method Specification: did:sdis

## Abstract

This document defines the `did:sdis` DID method, a decentralized identifier method designed for the Simulated Decentralized Identity System (SDIS). The SDIS method provides a hybrid approach combining Hyperledger Indy ledger technology with IPFS storage for decentralized identity management.

## Status of This Document

This is a working draft specification for the `did:sdis` DID method.

## Table of Contents

1. [Introduction](#introduction)
2. [DID Method Name](#did-method-name)
3. [Method-Specific Identifier](#method-specific-identifier)
4. [CRUD Operations](#crud-operations)
5. [Security Considerations](#security-considerations)
6. [Privacy Considerations](#privacy-considerations)
7. [Examples](#examples)

## Introduction

The `did:sdis` method enables the creation and management of decentralized identifiers using a hybrid ledger approach that combines:

- **Hyperledger Indy**: For DID registration and transaction management
- **IPFS**: For decentralized DID document storage
- **Rust Core**: For high-performance ledger operations
- **Ethereum Fallback**: For additional blockchain support

## DID Method Name

The namestring that shall identify this DID method is: `sdis`

A DID that uses this method MUST begin with the following prefix: `did:sdis:`

## Method-Specific Identifier

The method-specific identifier is a hierarchical identifier with the following structure:

```
did:sdis:<primary-hash>:<secondary-hash>
```

Where:
- `<primary-hash>`: 16-character hexadecimal string derived from SHA-256 hash of citizen data
- `<secondary-hash>`: 16-character hexadecimal string derived from secondary hash for uniqueness

### Identifier Generation

The identifier is generated using the following algorithm:

```python
def generate_sdis_did(citizen_data):
    # Create unique identifier from citizen data
    unique_id = f"{citizen_data['name']}_{citizen_data['email']}_{timestamp()}"
    
    # Generate primary hash
    primary_hash = hashlib.sha256(unique_id.encode()).hexdigest()[:16]
    
    # Generate secondary hash for additional uniqueness
    secondary_hash = hashlib.sha256(f"{unique_id}_secondary".encode()).hexdigest()[:16]
    
    return f"did:sdis:{primary_hash}:{secondary_hash}"
```

## CRUD Operations

### Create (Register)

To create a new `did:sdis` DID:

1. **Generate Identifier**: Use the algorithm above to create a unique DID
2. **Create DID Document**: Generate W3C-compliant DID document
3. **Store on IPFS**: Upload DID document to IPFS and obtain CID
4. **Register on Ledger**: Create NYM transaction on Indy ledger
5. **Store Metadata**: Save transaction hash and IPFS CID

**Example Registration Transaction:**
```json
{
  "operation": "NYM",
  "dest": "did:sdis:5135e697e2724d99:8b7ecf94bf0f819e",
  "verkey": "~b06c0c347c2afb02d7663f1868c6b64f5071e36ebed9381b95b4d70aaf716fa4",
  "role": "TRUST_ANCHOR",
  "ipfs_cid": "QmXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXxXx",
  "created_at": "2025-01-17T10:30:00Z"
}
```

### Read (Resolve)

To resolve a `did:sdis` DID:

1. **Parse DID**: Extract primary and secondary hashes
2. **Query Ledger**: Look up DID in Indy ledger
3. **Retrieve Document**: Fetch DID document from IPFS using stored CID
4. **Validate**: Verify document integrity and signature
5. **Return**: Return W3C-compliant DID document

**Resolution Process:**
```
GET /1.0/identifiers/did:sdis:5135e697e2724d99:8b7ecf94bf0f819e
```

**Response:**
```json
{
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:sdis:5135e697e2724d99:8b7ecf94bf0f819e",
  "verificationMethod": [{
    "id": "did:sdis:5135e697e2724d99:8b7ecf94bf0f819e#key-1",
    "type": "Ed25519VerificationKey2018",
    "controller": "did:sdis:5135e697e2724d99:8b7ecf94bf0f819e",
    "publicKeyBase58": "~b06c0c347c2afb02d7663f1868c6b64f5071e36ebed9381b95b4d70aaf716fa4"
  }],
  "authentication": ["did:sdis:5135e697e2724d99:8b7ecf94bf0f819e#key-1"],
  "assertionMethod": ["did:sdis:5135e697e2724d99:8b7ecf94bf0f819e#key-1"],
  "service": [{
    "id": "did:sdis:5135e697e2724d99:8b7ecf94bf0f819e#aadhaar-kyc",
    "type": "AadhaarKYCService",
    "serviceEndpoint": "https://aadhaar-kyc.gov.in/verify"
  }]
}
```

### Update

To update a `did:sdis` DID:

1. **Verify Authorization**: Confirm requester has update rights
2. **Create New Document**: Generate updated DID document
3. **Upload to IPFS**: Store new document and get new CID
4. **Update Ledger**: Create update transaction on ledger
5. **Invalidate Old**: Mark previous document as superseded

### Delete (Deactivate)

To deactivate a `did:sdis` DID:

1. **Verify Authorization**: Confirm requester has deactivation rights
2. **Create Deactivation Transaction**: Submit deactivation to ledger
3. **Update Document**: Mark DID document as deactivated
4. **Remove from Active Registry**: Update ledger state

## Security Considerations

### Cryptographic Security
- **Ed25519 Signatures**: All DIDs use Ed25519 for cryptographic operations
- **SHA-256 Hashing**: Identifier generation uses SHA-256 for collision resistance
- **Key Rotation**: Support for key rotation through DID document updates

### Ledger Security
- **Indy Ledger**: Leverages Hyperledger Indy's security model
- **Transaction Signing**: All ledger operations require proper signatures
- **Consensus**: Uses Indy's consensus mechanism for transaction ordering

### IPFS Security
- **Content Addressing**: DID documents identified by content hash
- **Integrity Verification**: Documents can be verified against stored hash
- **Decentralized Storage**: No single point of failure for document storage

## Privacy Considerations

### Data Minimization
- **Minimal PII**: Only essential identity data stored in DID documents
- **Selective Disclosure**: Support for selective attribute disclosure
- **Zero-Knowledge Proofs**: Framework for privacy-preserving verification

### Decentralization
- **No Central Authority**: No single entity controls DID resolution
- **Distributed Storage**: Documents stored across IPFS network
- **User Control**: Users maintain control over their identity data

## Examples

### Example DID
```
did:sdis:5135e697e2724d99:8b7ecf94bf0f819e
```

### Example DID Document
```json
{
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:sdis:5135e697e2724d99:8b7ecf94bf0f819e",
  "verificationMethod": [{
    "id": "did:sdis:5135e697e2724d99:8b7ecf94bf0f819e#key-1",
    "type": "Ed25519VerificationKey2018",
    "controller": "did:sdis:5135e697e2724d99:8b7ecf94bf0f819e",
    "publicKeyBase58": "~b06c0c347c2afb02d7663f1868c6b64f5071e36ebed9381b95b4d70aaf716fa4"
  }],
  "authentication": ["did:sdis:5135e697e2724d99:8b7ecf94bf0f819e#key-1"],
  "assertionMethod": ["did:sdis:5135e697e2724d99:8b7ecf94bf0f819e#key-1"],
  "service": [{
    "id": "did:sdis:5135e697e2724d99:8b7ecf94bf0f819e#aadhaar-kyc",
    "type": "AadhaarKYCService",
    "serviceEndpoint": "https://aadhaar-kyc.gov.in/verify"
  }],
  "created": "2025-01-17T10:30:00Z",
  "updated": "2025-01-17T10:30:00Z"
}
```

### Example Resolution Request
```bash
curl -H "Accept: application/did+ld+json" \
     "https://resolver.sdis.gov.in/1.0/identifiers/did:sdis:5135e697e2724d99:8b7ecf94bf0f819e"
```

## Implementation Status

- **✅ DID Document Generation**: W3C-compliant documents
- **✅ Indy Ledger Integration**: NYM transaction support
- **✅ IPFS Storage**: Decentralized document storage
- **✅ Rust Core**: High-performance ledger operations
- **✅ Ethereum Fallback**: Multi-blockchain support
- **🔄 Universal Resolver Driver**: In development
- **🔄 Public Resolver Service**: In development
- **⏳ W3C Registration**: Pending submission

## References

- [W3C DID Core Specification](https://www.w3.org/TR/did-core/)
- [W3C DID Method Registry](https://w3c.github.io/did-spec-registries/)
- [Hyperledger Indy Documentation](https://hyperledger-indy.readthedocs.io/)
- [IPFS Documentation](https://docs.ipfs.io/)
- [Universal Resolver](https://github.com/decentralized-identity/universal-resolver)

---

**Authors**: Aadhaar KYC System Team  
**Version**: 1.0.0  
**Date**: January 17, 2025  
**Status**: Working Draft
