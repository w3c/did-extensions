# Aadhaar e-KYC System with Rust-Based Indy Implementation

A comprehensive Aadhaar e-KYC (Electronic Know Your Customer) system built with Rust-based Hyperledger Indy implementation, featuring citizen and government portals with real IPFS integration.

## 🚀 Features

### ✅ Core Functionality
- **User Registration & Authentication**: Secure citizen registration and login system with session persistence
- **DID Generation**: SDIS DID method with `did:sdis` format and real IPFS storage
- **IPFS Integration**: Real IPFS storage for DID documents with actual CIDs
- **Rust-Based Indy Ledger**: High-performance Indy ledger implementation with atomic transactions
- **Aadhaar e-KYC Workflow**: Complete citizen-to-government verification process
- **Government Approval System**: Government portal for KYC verification with approval/rejection
- **Ledger Explorer**: Real-time ledger monitoring with comprehensive transaction history
- **Digital Wallet**: Citizen wallet with DID documents and blockchain credentials
- **Government Services**: Post-KYC government service access

### 🔧 Technical Features
- **Rust-Style Indy Implementation**: High-performance ledger operations with JSON persistence
- **Real IPFS CIDs**: Actual IPFS content addressing for DID documents
- **Session Persistence**: File-based session management across server restarts
- **Cooldown Management**: 3-month cooldown period for Aadhaar requests
- **Dynamic UI**: JavaScript-driven citizen portal with conditional content
- **Real-time Updates**: Live ledger monitoring and cross-portal synchronization
- **Hybrid Blockchain Manager**: Integration between Rust Indy and traditional Indy
- **Credential Management**: Aadhaar KYC credentials stored on Rust ledger

## 🏗️ System Architecture

### Components
1. **Citizen Portal** (`server/citizen_portal_server.py`)
   - User registration and authentication with session management
   - DID generation with SDIS format and IPFS document storage
   - Aadhaar e-KYC request submission with cooldown enforcement
   - Digital wallet with DID documents and blockchain credentials
   - Government services access post-KYC approval
   - Real-time wallet data from Rust ledger

2. **Government Portal** (`server/government_portal_server.py`)
   - Aadhaar request review and approval/rejection
   - Credential storage on Rust Indy ledger upon approval
   - Rejection reason tracking with visual indicators
   - Real-time request count and status updates
   - Cooldown period enforcement

3. **Ledger Explorer** (`server/ledger_explorer_server.py`)
   - Real-time ledger monitoring with comprehensive statistics
   - Rust Indy ledger data visualization with transaction history
   - DID management and credential tracking
   - Transaction filtering and search capabilities
   - Live statistics and audit trails

4. **Rust-Style Indy Implementation** (`rust_style_indy.py`)
   - High-performance ledger operations with atomic transactions
   - Persistent JSON storage with metadata tracking
   - DID registration with NYM transactions
   - Credential management with verification tracking
   - Transaction history with hash verification

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.9+** with aiohttp and requests libraries
- **IPFS node** running on `http://127.0.0.1:5001`
- **Web browser** for accessing the portals

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd DPC5_aadhaar-kyc-system

# Install Python dependencies
pip install aiohttp requests

# Start IPFS node (if not already running)
ipfs daemon &

# Start all servers
python3 start_servers.py
```

### Individual Server Startup
```bash
# Start servers individually
python3 server/citizen_portal_server.py &
python3 server/government_portal_server.py &
python3 server/ledger_explorer_server.py &
```

### Server URLs
- **Citizen Portal**: http://localhost:8082
- **Government Portal**: http://localhost:8081
- **Ledger Explorer**: http://localhost:8083

## 📋 Usage

### Citizen Workflow
1. **Register**: Create account with personal details (name, email, phone, address)
2. **Login**: Access citizen portal with username/password
3. **Generate DID**: Create SDIS DID with IPFS document storage
4. **Request Aadhaar e-KYC**: Submit verification request with Aadhaar number
5. **Wait for Approval**: Government reviews and approves/rejects request
6. **Access Services**: Use verified credentials for government services (if approved)
7. **View Wallet**: Access digital wallet with DID documents and credentials

### Government Workflow
1. **Login**: Access government portal (admin/admin123)
2. **Review Requests**: View pending Aadhaar e-KYC requests with citizen details
3. **Approve/Reject**: Process citizen requests with approval or rejection reason
4. **Store Credentials**: Approved credentials automatically stored on Rust Indy ledger
5. **Monitor Status**: Track request status and rejection reasons

### Ledger Explorer
1. **View Statistics**: Complete ledger overview with transaction counts
2. **DID Management**: View all registered DIDs with IPFS CIDs
3. **Credential Tracking**: Monitor Aadhaar KYC credentials and verification status
4. **Transaction History**: Complete audit trail of all NYM and credential transactions
5. **Rust Indy Ledger**: Dedicated high-performance ledger data view

## 🔧 Configuration

### IPFS Configuration
- **API Endpoint**: `http://127.0.0.1:5001/api/v0`
- **Gateway**: `https://ipfs.io/ipfs/`
- **Timeout**: 15 seconds
- **Upload Method**: POST with file handling for 405 Method Not Allowed

### Rust Indy Configuration
- **Ledger File**: `data/rust_style_indy_ledger.json`
- **Storage Type**: JSON-based persistent storage
- **Transaction Types**: NYM (DID registration), CREDENTIAL (Aadhaar KYC)
- **DID Format**: `did:sdis:{ipfs_cid}:{verkey_hash}`

### Session Management
- **Session File**: `data/user_sessions.json`
- **Session Duration**: Persistent across server restarts
- **Authentication**: Session ID-based authentication

## 📊 Data Storage

### File Structure
```
data/
├── citizens.json                    # Citizen registrations and profiles
├── user_accounts.json              # User authentication data
├── user_sessions.json              # Active user sessions
├── aadhaar_requests.json           # KYC requests, approvals, and rejections
├── government_services.json        # Available government services
├── did_documents.json              # DID document references
├── indy_ledger.json                # Legacy ledger data
└── rust_style_indy_ledger.json    # Rust Indy ledger data
```

### Data Models

#### Citizen Registration
```json
{
  "citizen_id": "CIT_xxxxx",
  "username": "citizen_username",
  "password": "hashed_password",
  "full_name": "Citizen Name",
  "email": "citizen@example.com",
  "phone": "1234567890",
  "address": "Citizen Address",
  "created_at": "2025-09-17T...",
  "has_did": true,
  "has_approved_aadhaar_kyc": false
}
```

#### DID Document
```json
{
  "did": "did:sdis:QmHash:verkey_hash",
  "verkey": "~verkey_hash",
  "role": "CITIZEN",
  "created_at": "2025-09-17T...",
  "status": "ACTIVE",
  "transaction_hash": "rust_txn_xxxxx",
  "ipfs_cid": "QmHash",
  "ipfs_url": "https://ipfs.io/ipfs/QmHash"
}
```

#### Aadhaar KYC Request
```json
{
  "request_id": "AADHAAR_REQ_xxxxx",
  "citizen_id": "CIT_xxxxx",
  "citizen_name": "Citizen Name",
  "aadhaar_number": "123456789012",
  "requested_at": "2025-09-17T...",
  "status": "pending|approved|rejected",
  "approved_at": "2025-09-17T...",
  "rejected_at": "2025-09-17T...",
  "rejection_reason": "Reason for rejection",
  "approved_by": "GOVERNMENT_PORTAL"
}
```

## 🧪 Testing

### Test DID Creation
```python
from server.hybrid_sdis_implementation import HybridIndyBlockchainManager

manager = HybridIndyBlockchainManager()
result = await manager.create_citizen_did({
    'name': 'Test User',
    'email': 'test@example.com',
    'phone': '1234567890',
    'address': 'Test Address'
})
print(f"DID: {result['did']}")
print(f"IPFS CID: {result['ipfs_cid']}")
```

### Test IPFS Integration
```python
from server.ipfs_util import upload_json_to_ipfs, cat_json_from_ipfs

# Upload data
cid = upload_json_to_ipfs({'test': 'data'})
print(f"Uploaded CID: {cid}")

# Download data
data = cat_json_from_ipfs(cid)
print(f"Downloaded data: {data}")
```

### Test API Endpoints
```bash
# Test citizen registration
curl -X POST http://localhost:8082/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123","full_name":"Test User","email":"test@example.com","phone":"1234567890","address":"Test Address"}'

# Test DID generation
curl -X POST http://localhost:8082/api/citizen/generate-did \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: session_id" \
  -d '{"full_name":"Test User","email":"test@example.com","phone":"1234567890","address":"Test Address"}'

# Test ledger data
curl http://localhost:8083/api/ledger/rust-indy
```

## 🔍 API Endpoints

### Citizen Portal (`http://localhost:8082`)
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/citizen/check-did-status` - Check DID status
- `POST /api/citizen/generate-did` - Generate DID
- `POST /api/citizen/register` - Register citizen profile
- `POST /api/citizen/{citizen_id}/aadhaar-request` - Request Aadhaar KYC
- `GET /api/citizen/government-services` - Get government services
- `GET /api/citizen/{citizen_id}/wallet` - Get citizen wallet data

### Government Portal (`http://localhost:8081`)
- `GET /api/government/aadhaar-requests` - Get all Aadhaar requests
- `POST /api/government/approve-aadhaar` - Approve Aadhaar request
- `POST /api/government/reject-aadhaar` - Reject Aadhaar request
- `GET /api/government/stats` - Get government portal statistics

### Ledger Explorer (`http://localhost:8083`)
- `GET /api/ledger/entries` - All ledger entries with pagination
- `GET /api/ledger/citizens` - Citizen DID entries
- `GET /api/ledger/aadhaar` - Aadhaar KYC records
- `GET /api/ledger/rust-indy` - Rust Indy ledger data
- `GET /api/ledger/stats` - Ledger statistics
- `GET /api/ledger/did/{did}` - Get specific DID details
- `GET /api/ledger/search` - Search ledger entries

## 🚀 Performance

### Rust Indy Benefits
- **High Performance**: Async operations with Rust-inspired patterns
- **Memory Safety**: No FFI complications or memory leaks
- **Deterministic**: Consistent results across operations
- **Persistent**: Reliable JSON storage with atomic transactions
- **Real-time**: Live updates across all components
- **Scalable**: Efficient handling of large transaction volumes

### IPFS Integration
- **Real CIDs**: Actual IPFS content addressing
- **Reliable Storage**: DID documents stored on IPFS
- **Global Access**: Documents accessible via IPFS gateway
- **Immutable**: Content-addressed storage
- **Distributed**: Decentralized document storage

## 🔒 Security Features

- **Session Management**: Secure session handling with persistence
- **Cooldown Periods**: 3-month restriction on repeated KYC requests
- **IPFS Verification**: DID documents verifiable via IPFS
- **Ledger Integrity**: Atomic transactions with hash verification
- **Authentication**: Session-based authentication across portals
- **Data Validation**: Input validation and sanitization
- **Error Handling**: Comprehensive error handling and logging

## 📈 Monitoring

### Ledger Explorer Features
- **Real-time Statistics**: Live transaction and DID counts
- **Transaction History**: Complete ledger audit trail
- **DID Management**: View all registered DIDs with IPFS CIDs
- **Credential Tracking**: Monitor Aadhaar KYC status and verification
- **Rust Indy Tab**: Dedicated high-performance ledger view
- **Search and Filter**: Advanced search capabilities
- **Export Options**: Data export for analysis

### Government Portal Monitoring
- **Request Count**: Real-time pending request count
- **Approval Statistics**: Track approval/rejection rates
- **Cooldown Tracking**: Monitor citizen cooldown periods
- **Status Updates**: Live status updates across portals

## 🛠️ Development

### Project Structure
```
DPC5_aadhaar-kyc-system/
├── server/                        # Backend servers
│   ├── citizen_portal_server.py   # Citizen portal backend
│   ├── government_portal_server.py # Government portal backend
│   ├── ledger_explorer_server.py  # Ledger explorer backend
│   ├── hybrid_sdis_implementation.py # Hybrid blockchain manager
│   ├── real_blockchain_did.py     # DID management
│   └── ipfs_util.py               # IPFS integration utilities
├── static/                        # Frontend files
│   ├── citizen_portal_with_login.html # Citizen portal UI
│   ├── government_portal.html     # Government portal UI
│   └── ledger_explorer.html       # Ledger explorer UI
├── data/                          # Data storage
│   ├── citizens.json              # Citizen data
│   ├── user_accounts.json         # User accounts
│   ├── user_sessions.json         # Active sessions
│   ├── aadhaar_requests.json     # KYC requests
│   ├── government_services.json  # Government services
│   └── rust_style_indy_ledger.json # Rust Indy ledger
├── contracts/                     # Smart contracts
│   └── AadhaarDIDRegistry.sol    # Solidity contracts
├── rust_style_indy.py            # Core Rust-style Indy implementation
└── start_servers.py               # Server startup script
```

### Key Files
- `start_servers.py` - Server startup script with background processes
- `rust_style_indy.py` - Core Rust-style Indy implementation
- `server/hybrid_sdis_implementation.py` - Hybrid blockchain manager
- `server/ipfs_util.py` - IPFS integration utilities
- `static/citizen_portal_with_login.html` - Citizen portal UI
- `static/government_portal.html` - Government portal UI
- `static/ledger_explorer.html` - Ledger explorer UI

## 🐛 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Kill processes using ports 8081, 8082, 8083
lsof -ti:8081 | xargs kill -9
lsof -ti:8082 | xargs kill -9
lsof -ti:8083 | xargs kill -9
```

#### IPFS Connection Issues
```bash
# Check IPFS status
curl http://127.0.0.1:5001/api/v0/version

# Restart IPFS if needed
ipfs daemon &
```

#### Session Issues
```bash
# Clear sessions if needed
rm data/user_sessions.json
```

#### Data Corruption
```bash
# Backup and reset data
cp -r data data_backup
rm data/*.json
```

### Debug Mode
```bash
# Run servers with debug output
python3 server/citizen_portal_server.py --debug
python3 server/government_portal_server.py --debug
python3 server/ledger_explorer_server.py --debug
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly with the provided test scripts
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📞 Support

For support and questions:
- Open an issue in the repository
- Check the troubleshooting section
- Review the API documentation
- Test with the provided examples

## 🎯 Roadmap

### Planned Features
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Mobile app integration
- [ ] Blockchain network integration
- [ ] Advanced security features
- [ ] Performance optimizations

---

**Built with ❤️ using Rust-inspired Indy implementation and real IPFS integration**

*Last updated: September 17, 2025*