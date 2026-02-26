#!/usr/bin/env python3
"""
End-to-End Flow Verification Script
Runs through the entire Citizen Registration -> Aadhaar KYC -> Service Access flow to verify it works programmatically.
"""
import requests
import json
import time
import uuid

CITIZEN_URL = "http://localhost:8082"
GOV_URL = "http://localhost:8081"
EXPLORER_URL = "http://localhost:8083"

def run_test():
    print("🚀 Starting End-to-End Verification Flow...")
    
    test_id = str(uuid.uuid4())[:8]
    test_email = f"e2e.test.{test_id}@example.com"
    
    # --- PHASE 1: REGISTRATION ---
    print("\n--- PHASE 1: REGISTRATION ---")
    
    # 1. Register Account
    print(f"1. Registering new citizen account ({test_email})...")
    reg_data = {
        "name": f"E2E Test User {test_id}",
        "email": test_email,
        "password": "securepassword123"
    }
    r = requests.post(f"{CITIZEN_URL}/api/auth/register", json=reg_data)
    if r.status_code != 200:
        print(f"❌ Account registration failed: {r.text}")
        return
    user_id = r.json().get("user_id")
    print(f"✅ Account created: {user_id}")
    
    # 2. Login
    print("2. Logging in...")
    login_data = {
        "email": test_email,
        "password": "securepassword123"
    }
    session = requests.Session()
    r = session.post(f"{CITIZEN_URL}/api/auth/login", json=login_data)
    if r.status_code != 200:
        print(f"❌ Login failed: {r.text}")
        return
    login_res = r.json()
    session_id = login_res.get("session_id")
    print(f"✅ Logged in successfully. Session ID: {session_id}")
    
    # Configure session to always send X-Session-ID
    session.headers.update({"X-Session-ID": session_id})
    
    # 3. Generate DID
    print("3. Submitting citizen details and generating DID...")
    citizen_details = {
        "name": f"E2E Test User {test_id}",
        "email": test_email,
        "phone": "9876543210",
        "address": "123 Automation St, Tech City",
        "dob": "1990-01-01",
        "gender": "Male",
        "aadhaar_number": f"99988877{test_id}"
    }
    r = session.post(f"{CITIZEN_URL}/api/citizen/generate-did", json=citizen_details)
    if r.status_code != 200:
        print(f"❌ DID generation failed: {r.text}")
        return
    did_res = r.json()
    did = did_res.get("did")
    citizen_id = did_res.get("citizen_id")
    print(f"✅ DID generated: {did}")
    print(f"   IPFS/Cloud URL: {did_res.get('ipfs_url') or did_res.get('cloud_url')}")
    print(f"   Transaction Hash: {did_res.get('transaction_hash')}")
    
    # Wait for ledger propagation
    time.sleep(2)
    
    # --- PHASE 2: KYC REQUEST & APPROVAL ---
    print("\n--- PHASE 2: KYC REQUEST & APPROVAL ---")
    
    # 1. Submit KYC Request (Requires getting the session to recognize the wallet)
    print("1. Refreshing wallet data...")
    session.get(f"{CITIZEN_URL}/api/citizen/{citizen_id}/wallet")
    
    print("2. Submitting Aadhaar KYC request...")
    kyc_data = {
        "aadhaar_number": f"99988877{test_id}",
        "otp": "123456"
    }
    r = session.post(f"{CITIZEN_URL}/api/citizen/{citizen_id}/aadhaar-request", json=kyc_data)
    if r.status_code != 200:
        print(f"❌ KYC request failed: {r.text}")
        return
    req_res = r.json()
    request_id = req_res.get("request_id")
    print(f"✅ KYC request submitted: {request_id}")
    
    # Wait for propagation
    time.sleep(2)
    
    # 3. Approve in Government Portal
    print("3. Approving KYC request in Government Portal...")
    gov_approve_data = {
        "request_id": request_id,
        "action": "APPROVE",
        "reason": "E2E test auto-approval",
        "level": "LEVEL_1"
    }
    # Note: Currently Government portal API doesn't require session for simplicity in some endpoints, 
    r = requests.post(f"{GOV_URL}/api/government/aadhaar-request/{request_id}/approve", json=gov_approve_data)
    if r.status_code != 200:
        print(f"❌ Government approval failed: {r.text}")
        return
    print("✅ KYC request approved by Government")
    
    # Wait for notifications to propagate
    time.sleep(3)
    
    # 4. Check Citizen Wallet for VC
    print("4. Checking Citizen Wallet for Verifiable Credential...")
    r = session.get(f"{CITIZEN_URL}/api/citizen/{citizen_id}/wallet")
    if r.status_code != 200:
        print(f"❌ Failed to fetch wallet: {r.text}")
        return
    wallet_data = r.json()
    wallet = wallet_data.get("wallet", {})
    credentials = wallet.get("vc_credentials", [])
    
    # Also check if it's in the old location just in case
    if not credentials and "credentials" in wallet_data:
        credentials = wallet_data.get("credentials", [])
        
    if len(credentials) == 0:
        print("❌ No credentials found in wallet after approval")
        # Let's see what the wallet actually returned
        print(json.dumps(wallet_data, indent=2))
        return
    
    vc = credentials[0]
    print(f"✅ Found VC in wallet: {vc.get('credential_type')} ({vc.get('status')})")
    
    # --- PHASE 3: SERVICE ACCESS ---
    print("\n--- PHASE 3: SERVICE ACCESS ---")
    print("1. Attempting to access Government Service (Passport Application)...")
    service_data = {
        "service_id": "SERVICE_PASSPORT",
        "service_name": "Passport Application"
    }
    r = session.post(f"{CITIZEN_URL}/api/citizen/{citizen_id}/service-request", json=service_data)
    if r.status_code != 200:
        print(f"❌ Service access failed: {r.text}")
        return
    service_res = r.json()
    if service_res.get("success"):
        print(f"✅ Service access GRANTED")
        print(f"   Message: {service_res.get('message')}")
        if service_res.get('token'):
            print(f"   Auto Identity Token used: {service_res.get('token')[:20]}...")
        else:
            print(f"   Request ID: {service_res.get('request_id')}")
    else:
        print(f"❌ Service access DENIED: {service_res.get('error')}")
        return
        
    print("\n🎉 ALL E2E TESTS PASSED SUCCESSFULLY! 🎉")

if __name__ == "__main__":
    run_test()
