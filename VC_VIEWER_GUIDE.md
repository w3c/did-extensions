# 🎫 Verifiable Credentials Viewer - Quick Reference

## 🌐 Access

**URL**: http://localhost:8083/vc-viewer

## 📊 Page Overview

The VC Viewer provides a comprehensive view of all Verifiable Credentials in your system, including transaction history, blockchain distribution, and performance analytics.

## 🎯 Key Differences from Rust Indy Ledger

### Rust Indy Ledger Explorer (http://localhost:8083)
- **Focus**: DID (Decentralized Identifier) management
- **Shows**: DID registration, DID documents, verification keys
- **Use Case**: Identity management and DID lifecycle

### NEW Verifiable Credentials Viewer (http://localhost:8083/vc-viewer)
- **Focus**: Verifiable Credential transactions and lifecycle
- **Shows**: Credential issuance, updates, revocations, cross-chain mappings
- **Use Case**: Credential tracking and blockchain analytics

## 📈 Sections Explained

### 1. Statistics Dashboard (Top Row)
Real-time counters showing:
- **Total Credentials**: All VCs ever issued
- **Active**: Currently valid credentials
- **Revoked**: Permanently invalidated credentials
- **Transactions**: Total transaction count
- **Avg Time**: Average transaction duration
- **Avg Cost**: Average transaction cost

### 2. Verifiable Credentials List
Complete table of all credentials:
| Column | Description |
|--------|-------------|
| Credential ID | Unique identifier for the VC |
| Citizen DID | Owner's Decentralized Identifier |
| Blockchain | Primary blockchain (INDY, ETHEREUM, POLKADOT, HYPERLEDGER FABRIC) |
| Type | Credential type (e.g., aadhaar_kyc) |
| Status | ACTIVE, REVOKED, or SUSPENDED |
| Issued | Timestamp of issuance |
| **Action** | Click any row to view detailed information |

### 3. Transaction Timeline
Chronological view of all credential operations:
- **ISSUANCE** (Green badge): New credential created
- **UPDATE** (Blue badge): Credential modified
- **REVOCATION** (Red badge): Credential permanently invalidated

Each transaction shows:
- Transaction ID
- Blockchain used
- Cost in tokens
- Duration in milliseconds
- Timestamp

### 4. Blockchain Distribution
Analytics showing transaction distribution:
```
Blockchain        | Transactions | Percentage
-----------------------------------------------
INDY              | 11          | 47.8%
ETHEREUM          | 5           | 21.7%
POLKADOT          | 4           | 17.4%
HYPERLEDGER_FABRIC| 3           | 13.0%
```

### 5. Cross-Chain Mappings
When credentials are replicated across blockchains:
- **Mapping ID**: Unique mapping identifier
- **Credential ID**: The credential being mapped
- **Source Blockchain**: Original blockchain
- **Target Blockchain**: Destination blockchain
- **Mapped At**: Timestamp of mapping

### 6. Performance Analytics
Real-time performance metrics:
- **Total Issuances**: Credentials created
- **Total Updates**: Modifications made
- **Total Revocations**: Invalidations performed
- **Throughput**: Transactions per second

## 🔄 Refreshing Data

Click the **"🔄 Refresh Data"** button at the top to reload all statistics and tables with the latest data from the unified VC ledger.

## 🎨 Visual Indicators

### Status Badges
- 🟢 **ACTIVE**: Credential is valid and usable
- 🔴 **REVOKED**: Credential permanently invalidated
- 🟡 **SUSPENDED**: Temporarily disabled

### Blockchain Labels
- 🟢 **INDY**: Hyperledger Indy (Primary)
- 🔵 **ETHEREUM**: Ethereum blockchain
- 🟣 **POLKADOT**: Polkadot network
- ⚪ **HYPERLEDGER FABRIC**: Fabric network

### Transaction Types
- 🟢 **ISSUANCE**: Creating new credential
- 🔵 **UPDATE**: Modifying existing credential
- 🔴 **REVOCATION**: Permanently invalidating credential

## 💡 Use Cases

### For Developers
- Monitor credential lifecycle
- Track transaction performance
- Debug cross-chain operations
- Analyze blockchain usage patterns

### For Administrators
- Audit credential operations
- Monitor system performance
- Identify bottlenecks
- Track blockchain costs

### For Compliance Officers
- Complete audit trail
- Transaction history
- Cross-chain mapping records
- Performance metrics

## 🚀 Quick Start

1. **Open the Viewer**: Navigate to http://localhost:8083/vc-viewer
2. **Review Statistics**: Check the top dashboard for system overview
3. **Browse Credentials**: Use the table to find specific VCs
4. **Analyze Transactions**: View the timeline for operation history
5. **Check Distribution**: See which blockchain has most activity
6. **Monitor Performance**: Review analytics for system health

## 🔗 Integration Points

The VC Viewer integrates with:
- **Unified VC Ledger**: Data source
- **Credential Ledger System**: Storage
- **Rust Indy Core**: Primary blockchain
- **Cross-blockchain Registry**: Multi-chain tracking
- **Performance Metrics**: Real-time analytics

## 📊 Data Flow

```
Verifiable Credential Issued
    ↓
Unified VC Ledger (Storage)
    ↓
API Endpoint (/api/ledger/unified-vc)
    ↓
VC Viewer Page (Display)
    ↓
Real-time Statistics & Analytics
```

## 🛠️ Technical Details

### API Endpoints Used
- `GET /api/ledger/unified-vc` - Complete ledger data
- `GET /api/ledger/unified-vc/performance` - Performance metrics
- `GET /api/ledger/unified-vc/mappings` - Cross-chain data

### Data Format
All data is JSON with the following structure:
```json
{
  "success": true,
  "ledger_metadata": {...},
  "credentials": [...],
  "transactions": [...],
  "blockchain_registries": {...},
  "cross_chain_mappings": [...],
  "performance_metrics": {...}
}
```

## ✅ Status Check

To verify the viewer is working:
```bash
curl http://localhost:8083/vc-viewer
```

Should return HTML content (status 200).

---

**🎉 The Verifiable Credentials Viewer gives you complete visibility into your credential ecosystem!**

