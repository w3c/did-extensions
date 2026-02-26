# Full Citizen DID & e-KYC System Flow - Requirements Analysis

## Current System Status vs. Requirements

### ✅ Already Implemented

1. **Citizen Registration & Login** ✅
   - Location: `static/citizen_portal_with_login.html`
   - Features: Email/password authentication, session management
   - Status: **Working**

2. **DID Generation** ✅
   - Location: `static/citizen_portal_with_login.html` (lines 1014-1400)
   - Storage: Rust Indy ledger, IPFS
   - Status: **Working**

3. **Wallet Display** ✅
   - Location: `static/citizen_portal_with_login.html` (wallet tab)
   - Shows: DID, IPFS link, DID document
   - Status: **Working**

4. **Aadhaar e-KYC Request** ✅
   - Location: Server-side in `citizen_portal_server.py`
   - Features: OTP verification, request submission
   - Status: **Working**

5. **VC Issuance on Approval** ✅
   - Location: `government_portal_server.py` + `rust_vc_credential_manager.py`
   - Storage: Multiple ledgers (Rust Indy, Unified VC Ledger)
   - Status: **Working**

### ⚠️ Needs Enhancement

1. **VC Display as Card** ⚠️
   - Current: VC data in backend, not shown as card format
   - Needed: Visual credential card in dashboard
   - Priority: **High**

2. **Government Services List** ⚠️
   - Current: Basic services structure exists
   - Needed: UI with service selection
   - Priority: **High**

3. **Service Verification with VC** ⚠️
   - Current: Not fully implemented
   - Needed: VC number verification workflow
   - Priority: **High**

4. **IPFS DID Document Update** ⚠️
   - Current: DID creation stores on IPFS
   - Needed: VC metadata appended to DID document
   - Priority: **Medium**

### ❌ Missing Features

1. **VC Number Display on Dashboard** ❌
   - Not shown to citizen after KYC approval
   - Priority: **Critical**

2. **Service-Specific Verification Page** ❌
   - No dedicated verification page per service
   - Priority: **Critical**

3. **VC Number Entry & Verification Flow** ❌
   - No UI for entering VC number
   - No backend verification against VC Ledger
   - Priority: **Critical**

## Recommended Implementation Plan

### Phase 1: VC Display & Dashboard Enhancement
1. Add VC card component to dashboard
2. Show VC number prominently
3. Display credential metadata

### Phase 2: Government Services Integration
1. Create services list UI
2. Implement service selection
3. Add service detail pages

### Phase 3: VC Verification Workflow
1. Add VC number input form
2. Implement backend verification
3. Create verification result page

### Phase 4: DID Document Enhancement
1. Update DID document with VC metadata
2. Store on IPFS with updated info
3. Show in wallet

## Current Flow Diagram

```
Citizen Login
    ↓
Check DID Status
    ↓
If no DID → Generate DID → Store on Ledger/IPFS → Show Wallet
    ↓
If has DID → Show Wallet
    ↓
Request Aadhaar KYC → Enter Aadhaar + OTP
    ↓
Send to Government Portal
    ↓
Government Approves → VC Issued
    ↓
❌ FALLS OFF HERE - VC not displayed to citizen
```

## Required Flow Diagram

```
Citizen Login
    ↓
Check DID Status
    ↓
If no DID → Generate DID → Store on Ledger/IPFS → Show Wallet
    ↓
If has DID → Show Wallet
    ↓
Request Aadhaar KYC → Enter Aadhaar + OTP
    ↓
Send to Government Portal
    ↓
Government Approves → VC Issued → Store in Ledger
    ↓
✅ NEW: Display VC Card on Dashboard with VC Number
    ↓
✅ NEW: Show Government Services List
    ↓
✅ NEW: Select Service → Enter VC Number
    ↓
✅ NEW: Verify VC against Ledger
    ↓
✅ NEW: Allow/Deny Service Access
```

