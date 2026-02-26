# Cross-Blockchain VC System - API Endpoints Guide

## 🎫 Auto Identity Token API (Port 8080)

All endpoints at base URL: `http://localhost:8080`

### Token Generation

#### 1. Generate Identity Token
```bash
POST /api/tokens/generate
Content-Type: application/json

{
  "citizen_did": "did:sdis:abc123:def456",
  "token_type": "identity_token",
  "additional_claims": {
    "kyc_approved": true,
    "kyc_level": "LEVEL_1",
    "government_services_access": true
  }
}
```

**Response:**
```json
{
  "success": true,
  "token_id": "auto_token_identity_token_12345...",
  "token": "eyJhbGci...",
  "token_type": "identity_token",
  "expires_at": "2025-11-03T10:30:00",
  "quantum_secure_token": {...},
  "did_data": {...},
  "vc_data": {...}
}
```

#### 2. Generate Access Token
```bash
POST /api/tokens/generate/access_token
Content-Type: application/json

{
  "citizen_did": "did:sdis:abc123:def456"
}
```

#### 3. Generate Service Token
```bash
POST /api/tokens/generate/service_token
Content-Type: application/json

{
  "citizen_did": "did:sdis:abc123:def456",
  "additional_claims": {
    "service": "government_benefits"
  }
}
```

**Misuse Protection:**
- ⚠️ Max 10 tokens per hour per DID
- ⚠️ Max 50 tokens per day per DID
- 🛡️ Auto-cooldown after 5 failed attempts

### Token Verification

#### 4. Verify Token
```bash
POST /api/tokens/verify
Content-Type: application/json

{
  "token": "eyJhbGci..."
}
```

#### 5. Verify by ID
```bash
GET /api/tokens/verify/auto_token_identity_token_12345...
```

### Token Management

#### 6. Revoke Token
```bash
POST /api/tokens/auto_token_identity_token_12345.../revoke
Content-Type: application/json

{
  "reason": "User requested revocation"
}
```

#### 7. Get Statistics
```bash
GET /api/tokens/statistics
```

**Response:**
```json
{
  "success": true,
  "total_tokens": 150,
  "active_tokens": 142,
  "expired_tokens": 5,
  "revoked_tokens": 3,
  "token_types": {
    "identity_token": 80,
    "access_token": 50,
    "service_token": 15,
    "refresh_token": 5
  }
}
```

### DID Operations

#### 8. Retrieve DID Data
```bash
GET /api/did/did:sdis:abc123:def456/retrieve
```

**Response:**
```json
{
  "success": true,
  "did": "did:sdis:abc123:def456",
  "did_document": {...},
  "citizen_data": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "status": "ACTIVE"
}
```

#### 9. Resolve DID
```bash
GET /api/did/did:sdis:abc123:def456/resolve
```

#### 10. Get VC Credentials
```bash
GET /api/did/did:sdis:abc123:def456/credentials
```

**Response:**
```json
{
  "success": true,
  "citizen_did": "did:sdis:abc123:def456",
  "credentials": [
    {
      "credential_id": "vc_aadhaar_kyc_123...",
      "type": "aadhaar_kyc",
      "status": "ACTIVE",
      "issued_at": "2025-11-01T10:00:00",
      "expires_at": "2026-11-01T10:00:00"
    }
  ],
  "total_credentials": 2
}
```

### Health & Status

#### 11. Health Check
```bash
GET /health
```

#### 12. Detailed Status
```bash
GET /status
```

---

## 🏛️ Government Portal API (Port 8081)

### Cross-Blockchain VC Ledger

#### 1. Get Unified Ledger Stats
```bash
GET /api/government/unified-vc-ledger/stats
```

**Response:**
```json
{
  "success": true,
  "total_credentials": 18,
  "total_transactions": 18,
  "cross_chain_credentials": 0,
  "supported_blockchains": ["indy", "ethereum", "polkadot", "hyperledger_fabric"],
  "performance_metrics": {
    "average_transaction_time_ms": 0.3,
    "average_transaction_cost_tokens": 0.000225,
    "total_issuances": 18,
    "total_updates": 5,
    "total_revocations": 1
  }
}
```

#### 2. Get Performance Metrics
```bash
GET /api/government/unified-vc-ledger/performance
```

#### 3. Get Blockchain Credentials
```bash
GET /api/government/unified-vc-ledger/blockchain/indy
GET /api/government/unified-vc-ledger/blockchain/ethereum
GET /api/government/unified-vc-ledger/blockchain/polkadot
GET /api/government/unified-vc-ledger/blockchain/hyperledger_fabric
```

#### 4. Get Cross-Chain Mappings
```bash
GET /api/government/cross-chain-mappings
```

### Standard Government APIs

#### 5. Get KYC Requests
```bash
GET /api/government/aadhaar-requests
```

#### 6. Approve KYC Request
```bash
POST /api/government/aadhaar-request/{request_id}/approve
Content-Type: application/json

{}
```

**What happens:**
- ✅ VC issued on Rust Indy ledger
- ✅ VC replicated to Unified VC Ledger
- ✅ Auto identity token generated
- ✅ Performance metrics recorded

#### 7. Reject KYC Request
```bash
POST /api/government/aadhaar-request/{request_id}/reject
Content-Type: application/json

{
  "reason": "Incomplete documentation"
}
```

---

## 📱 Usage Examples

### Example 1: Generate Identity Token for Government Services
```bash
curl -X POST http://localhost:8080/api/tokens/generate \
  -H "Content-Type: application/json" \
  -d '{
    "citizen_did": "did:sdis:abc123:def456",
    "token_type": "identity_token",
    "additional_claims": {
      "kyc_approved": true,
      "aadhaar_verified": true
    }
  }'
```

### Example 2: View Performance Metrics
```bash
curl http://localhost:8081/api/government/unified-vc-ledger/performance
```

### Example 3: Get All Credentials on Ethereum
```bash
curl http://localhost:8081/api/government/unified-vc-ledger/blockchain/ethereum
```

### Example 4: Retrieve Citizen Credentials
```bash
curl http://localhost:8080/api/did/did:sdis:abc123:def456/credentials
```

---

## 🔒 Security Notes

- All token generation respects misuse protection limits
- Failed attempts are automatically tracked
- Auto-cooldown prevents brute force attacks
- Quantum-secure signatures for sensitive operations

---

## 📊 Response Codes

- `200 OK`: Success
- `400 Bad Request`: Invalid parameters
- `401 Unauthorized`: Missing/invalid token
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

**Complete API Documentation**: See individual server files for detailed endpoint documentation.

