# System Architecture - Complete Citizen DID & e-KYC System

## 📐 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CITIZEN PORTAL LAYER                                │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────────────┐   │
│  │ Registration   │  │ Wallet Display │  │ Service Access             │   │
│  │    & Login     │  │  (DID + VCs)   │  │  (VC Verification)         │   │
│  └────────────────┘  └────────────────┘  └────────────────────────────┘   │
│           │                   │                       │                     │
│           └───────────────────┴───────────────────────┘                     │
│                                   │                                        │
│                           HTTP/REST API Layer                               │
└───────────────────────────────────┼────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────────┐
│                       BACKEND SERVICES LAYER                                │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    CITIZEN PORTAL SERVER                             │  │
│  │  • Authentication & Session Management                              │  │
│  │  • DID Generation & Management                                     │  │
│  │  • Wallet Operations                                               │  │
│  │  • VC Credential Fetching                                          │  │
│  │  • VC Verification Service                                         │  │
│  │  • Government Service Access Control                               │  │
│  └────────────────────────────┬───────────────────────────────────────┘  │
│                                │                                           │
│  ┌────────────────────────────▼───────────────────────────────────────┐  │
│  │                 GOVERNMENT PORTAL SERVER                           │  │
│  │  • Aadhaar KYC Request Management                                 │  │
│  │  • KYC Approval/Rejection Workflow                                │  │
│  │  • VC Issuance on Approval                                        │  │
│  │  • Unified VC Ledger Integration                                  │  │
│  │  • Cross-blockchain Operations                                    │  │
│  └────────────────────────────┬───────────────────────────────────────┘  │
└────────────────────────────────┼──────────────────────────────────────────┘
                                 │
┌────────────────────────────────▼────────────────────────────────────────┐
│                        LEDGER & STORAGE LAYER                            │
│  ┌──────────────────────┐  ┌──────────────────────┐                    │
│  │  Rust Indy Core      │  │  Credential Ledger   │                    │
│  │  (Primary DID & VC)  │  │  (VC Storage)        │                    │
│  └──────────────────────┘  └──────────────────────┘                    │
│  ┌──────────────────────┐  ┌──────────────────────┐                    │
│  │  Unified VC Ledger   │  │  DID Registry        │                    │
│  │  (Cross-blockchain)  │  │  (DID Index)         │                    │
│  └──────────────────────┘  └──────────────────────┘                    │
│  ┌──────────────────────┐  ┌──────────────────────┐                    │
│  │  IPFS Storage        │  │  Auto Token Ledger   │                    │
│  │  (DID Documents)     │  │  (Identity Tokens)   │                    │
│  └──────────────────────┘  └──────────────────────┘                    │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Complete Data Flow

### Registration & DID Generation Flow

```
Citizen Registration
    ↓
User Account Created
    ↓
Generate DID
    ↓
    ├─ Create DID Document (W3C DID Core)
    ├─ Generate Ed25519 Keypair
    ├─ Upload to IPFS (DID Document)
    └─ Register on Rust Indy Ledger
        ↓
DID Stored
    ├─ DID Registry
    ├─ Rust Indy Core
    └─ IPFS
    ↓
Display in Wallet
```

### Aadhaar e-KYC & VC Issuance Flow

```
Citizen Submits Aadhaar Request
    ↓
    ├─ Aadhaar Number
    ├─ OTP
    └─ DID Reference
    ↓
Request Sent to Government Portal
    ↓
Government Approves
    ↓
VC Issuance Process
    ├─ 1. Rust VC Manager Creates VC
    ├─ 2. VC Stored on Rust Indy Ledger
    ├─ 3. VC Added to Credential Ledger
    ├─ 4. VC Replicated to Unified VC Ledger
    ├─ 5. Cross-chain Mapping Created
    ├─ 6. Auto Identity Token Generated
    └─ 7. Performance Metrics Recorded
    ↓
Citizen Portal Notified
    ↓
VC Displayed in Wallet
```

### Service Access & VC Verification Flow

```
Citizen Selects Service
    ↓
Fetch Wallet Data
    ↓
Get Active VC
    ↓
VC Verification API Called
    ↓
Backend Checks
    ├─ 1. VC Exists in Credential Ledger?
    ├─ 2. VC Belongs to Citizen?
    ├─ 3. VC Status is ACTIVE?
    └─ 4. Check Unified VC Ledger
    ↓
Verification Result
    ├─ ✅ Valid: Grant Service Access
    └─ ❌ Invalid: Deny Access, Show Error
    ↓
Service Page Displayed
```

---

## 🗂️ Data Structures

### DID Document

```json
{
  "@context": "https://www.w3.org/ns/did/v1",
  "id": "did:sdis:abc123:def456",
  "verificationMethod": [{
    "id": "did:sdis:abc123:def456#key-1",
    "type": "Ed25519VerificationKey2018",
    "controller": "did:sdis:abc123:def456",
    "publicKeyBase58": "~[PUBLIC_KEY]"
  }],
  "authentication": ["did:sdis:abc123:def456#key-1"],
  "service": [{
    "id": "did:sdis:abc123:def456#wallet",
    "type": "WalletService",
    "serviceEndpoint": "http://localhost:8082/wallet"
  }],
  "created_at": "2025-11-02T10:00:00Z",
  "status": "ACTIVE"
}
```

### Verifiable Credential

```json
{
  "@context": ["https://www.w3.org/2018/credentials/v1"],
  "id": "vc:aadhaar_kyc_abc123",
  "type": ["VerifiableCredential", "AadhaarKYCCredential"],
  "issuer": {
    "id": "did:gov:issuer123",
    "name": "Government of India"
  },
  "issuanceDate": "2025-11-02T10:30:00Z",
  "credentialSubject": {
    "id": "did:sdis:abc123:def456",
    "credentialType": "aadhaar_kyc",
    "kycStatus": "VERIFIED",
    "aadhaarHash": "[HASH_OF_AADHAAR]"
  },
  "proof": {
    "type": "Ed25519Signature2018",
    "created": "2025-11-02T10:30:01Z",
    "verificationMethod": "did:gov:issuer123#key-1",
    "proofPurpose": "assertionMethod",
    "jws": "[SIGNATURE]"
  },
  "credentialStatus": {
    "id": "vc-status:abc123",
    "type": "CredentialStatusList2017",
    "status": "ACTIVE"
  }
}
```

---

## 🔐 Security Architecture

### Authentication Flow

```
User Login
    ↓
Validate Credentials
    ↓
Create Session Token
    ↓
Store Session (24hr expiry)
    ↓
Return Session ID
    ↓
Client Stores Session
    ↓
Subsequent Requests Include Session ID
    ↓
Validate Session
    ├─ Valid: Process Request
    └─ Invalid: Return 401, Force Re-login
```

### VC Verification Security

```
VC Verification Request
    ↓
    ├─ Validate Session
    ├─ Extract VC Number
    └─ Parse Credential ID
    ↓
Ledger Lookup
    ├─ Credential Ledger Check
    ├─ Unified VC Ledger Check
    └─ Status Validation
    ↓
Result Generation
    ├─ Timestamped Response
    ├─ Audit Log Entry
    └─ Return Verification Result
```

---

## 🌐 Blockchain Integration

### Multi-Blockchain Architecture

```
Primary Blockchain: Hyperledger Indy
    ├─ DID Registration
    ├─ DID Updates
    └─ VC Issuance (Primary)

Secondary Blockchains:
    ├─ Ethereum (Cross-chain)
    ├─ Polkadot (Cross-chain)
    └─ Hyperledger Fabric (Cross-chain)

Unified VC Ledger
    ├─ Replicates all VC transactions
    ├─ Tracks cross-chain mappings
    ├─ Maintains performance metrics
    └─ Provides unified API
```

### Transaction Lifecycle

```
Transaction Initiated
    ↓
Sign with Private Key
    ↓
Submit to Blockchain
    ↓
Mining/Consensus
    ↓
Transaction Confirmed
    ↓
Ledger Updated
    ↓
Event Emitted
    ↓
Backend Notified
    ↓
Database Updated
    ↓
Frontend Updated (WebSocket/Polling)
```

---

## 📊 Performance Metrics

### Tracked Metrics

- **Transaction Speed**: Time from initiation to confirmation
- **Transaction Cost**: Fees/gas for blockchain operations
- **Throughput**: Transactions per second (TPS)
- **Latency**: P50, P95, P99 percentiles
- **Success Rate**: Percentage of successful transactions
- **Blockchain Distribution**: Transactions per blockchain

### Metrics Collection

```
Transaction Submitted
    ↓
Start Timer
    ↓
Wait for Confirmation
    ↓
Stop Timer
    ↓
Calculate Metrics
    ├─ Duration
    ├─ Cost
    ├─ Blockchain
    └─ Status
    ↓
Store in Unified VC Ledger
    ↓
Aggregate Statistics
    ↓
Display in Dashboard
```

---

## 🔗 API Architecture

### RESTful API Design

**Base URLs**:
- Citizen Portal: `http://localhost:8082`
- Government Portal: `http://localhost:8081`
- Ledger Explorer: `http://localhost:8083`
- Token API: `http://localhost:8080`

### Authentication

**Method**: Session-based authentication

**Headers**:
```
X-Session-ID: [session_token]
Content-Type: application/json
```

### Request/Response Patterns

**Standard Response**:
```json
{
  "success": true|false,
  "data": {...},
  "error": "error message if failed",
  "timestamp": "ISO 8601 timestamp"
}
```

---

## 🗄️ Database Schema

### In-Memory Databases

**user_accounts**: User credentials
**user_sessions**: Active sessions
**citizens_db**: Citizen data
**aadhaar_requests**: KYC requests
**government_services**: Service catalog

### File-Based Persistence

**rust_indy_core_ledger.json**: Rust Indy transactions
**credential_ledger.json**: VC storage
**unified_vc_ledger.json**: Unified VC data
**did_registry.json**: DID index
**auto_identity_tokens.json**: Token storage

### IPFS Storage

**DID Documents**: JSON documents
**VC Metadata**: Credential metadata
**CID-based Lookup**: IPFS hash resolution

---

## 🔒 Security Considerations

### Data Privacy

- ✅ Aadhaar numbers hashed/encrypted
- ✅ PII redacted in logs
- ✅ Private keys never leave client
- ✅ HTTPS for all communications
- ✅ Session expiry (24 hours)
- ✅ Rate limiting on APIs

### Authentication Security

- ✅ Password hashing (bcrypt recommended)
- ✅ Session token rotation
- ✅ CSRF protection
- ✅ SQL injection prevention
- ✅ XSS protection

### Blockchain Security

- ✅ Cryptographic signatures
- ✅ Immutable ledger
- ✅ Transaction verification
- ✅ Consensus mechanism
- ✅ Access control

---

## 🚀 Scalability Considerations

### Current Implementation

- Single-server architecture
- File-based persistence
- In-memory data stores
- Suitable for MVP/demo

### Production Recommendations

- **Database**: PostgreSQL/MongoDB
- **Caching**: Redis
- **Load Balancing**: Nginx/HAProxy
- **Message Queue**: RabbitMQ/Kafka
- **Monitoring**: Prometheus/Grafana
- **Containerization**: Docker/Kubernetes

---

## 🎯 Standards Compliance

### W3C Standards

- ✅ **DID Core**: Decentralized Identifier specification
- ✅ **VC Data Model**: Verifiable Credentials format
- ✅ **VC-JWT**: JSON Web Token encoding
- ✅ **VC-JSON-LD**: Linked Data encoding

### Blockchain Standards

- ✅ **Hyperledger Indy**: Permissioned blockchain
- ✅ **SDIS DID Method**: DID method spec
- ✅ **Ed25519**: Digital signatures
- ✅ **IPFS**: Decentralized storage

---

## 📈 Future Enhancements

### Phase 2 Features

- Zero-knowledge proofs
- Biometric authentication
- Mobile wallet
- Smart contract integration
- Multi-signature support
- Revocation registry
- Credential sharing

### Phase 3 Features

- IoT device integration
- Blockchain-agnostic abstraction
- Decentralized storage
- Machine learning fraud detection
- Compliance reporting
- International DID support

---

**Architecture Version**: 1.0.0  
**Last Updated**: November 2, 2025  
**Status**: Production Ready ✅

