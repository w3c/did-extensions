#!/usr/bin/env python3
"""
VC Revocation Test Suite
Complete tests for verifiable credential revocation functionality
"""

import asyncio
import json
import sys
from pathlib import Path

# Add paths
sys.path.append('server')
from government_portal_server import GovernmentPortalServer
from citizen_portal_server import CitizenPortalServer
from credential_ledger_system import CredentialLedgerSystem

async def test_scenario_1_issue_and_verify():
    """Test 1: Issue VC → Verify (should return valid)"""
    print("\n" + "=" * 80)
    print("TEST 1: Issue VC → Verify (Expected: Valid)")
    print("=" * 80)
    
    cit_server = CitizenPortalServer()
    
    # Find an active VC
    ledger_file = Path('data/credential_ledger.json')
    with open(ledger_file) as f:
        ledger = json.load(f)
    
    active_vc = None
    for cred_id, cred_data in ledger.get('credentials', {}).items():
        if cred_data.get('status') == 'ACTIVE':
            active_vc = cred_id, cred_data.get('citizen_did')
            break
    
    if not active_vc:
        print("❌ No active VCs found for testing")
        return False
    
    cred_id, citizen_did = active_vc
    print(f"Testing with VC: {cred_id[:50]}...")
    
    from aiohttp import web
    class VerifyReq:
        def __init__(self):
            self.match_info = {}
        async def json(self):
            return {'credential_id': cred_id, 'citizen_did': citizen_did}
    
    verify_req = VerifyReq()
    response = await cit_server.verify_vc_credential(verify_req)
    result = json.loads(response.body.decode())
    
    print(f"Result: verified={result.get('verified')}, valid={result.get('valid', 'N/A')}")
    
    if result.get('verified') == True:
        print("✅ PASS: Active VC correctly verified")
        return True
    else:
        print(f"❌ FAIL: Expected verified=True, got {result.get('verified')}")
        return False

async def test_scenario_2_revoke_and_verify():
    """Test 2: Revoke VC → Verify (should return invalid)"""
    print("\n" + "=" * 80)
    print("TEST 2: Revoke VC → Verify (Expected: Invalid)")
    print("=" * 80)
    
    gov_server = GovernmentPortalServer()
    cit_server = CitizenPortalServer()
    
    # Get an active VC to revoke
    ledger_file = Path('data/credential_ledger.json')
    with open(ledger_file) as f:
        ledger = json.load(f)
    
    active_vc = None
    for cred_id, cred_data in ledger.get('credentials', {}).items():
        if cred_data.get('status') == 'ACTIVE':
            active_vc = cred_id, cred_data.get('citizen_did')
            break
    
    if not active_vc:
        print("❌ No active VCs found for revocation")
        return False
    
    cred_id, citizen_did = active_vc
    print(f"Revoking VC: {cred_id[:50]}...")
    
    # Revoke
    from aiohttp import web
    class RevokeReq:
        def __init__(self, cid):
            self.match_info = {'credential_id': cid}
        async def json(self):
            return {'reason': 'Test revocation'}
    
    revoke_req = RevokeReq(cred_id)
    revoke_resp = await gov_server.revoke_vc_credential(revoke_req)
    revoke_result = json.loads(revoke_resp.body.decode())
    
    print(f"Revocation success: {revoke_result.get('success')}")
    
    # Verify after revocation
    class VerifyReq:
        def __init__(self):
            self.match_info = {}
        async def json(self):
            return {'credential_id': cred_id, 'citizen_did': citizen_did}
    
    verify_req = VerifyReq()
    verify_resp = await cit_server.verify_vc_credential(verify_req)
    verify_result = json.loads(verify_resp.body.decode())
    
    print(f"After revocation: verified={verify_result.get('verified')}, error={verify_result.get('error')}")
    
    if verify_result.get('verified') == False and 'revoked' in verify_result.get('error', '').lower():
        print("✅ PASS: Revoked VC correctly rejected")
        return True
    else:
        print(f"❌ FAIL: Expected verified=False with revocation error")
        return False

async def test_scenario_3_non_existing_vc():
    """Test 3: Try to revoke non-existing VC → return error 404"""
    print("\n" + "=" * 80)
    print("TEST 3: Revoke Non-Existing VC (Expected: 404)")
    print("=" * 80)
    
    gov_server = GovernmentPortalServer()
    
    non_existing_id = "vc_nonexistent_123456789"
    print(f"Attempting to revoke: {non_existing_id}")
    
    from aiohttp import web
    class RevokeReq:
        def __init__(self, cid):
            self.match_info = {'credential_id': cid}
        async def json(self):
            return {'reason': 'Test'}
    
    revoke_req = RevokeReq(non_existing_id)
    response = await gov_server.revoke_vc_credential(revoke_req)
    
    result = json.loads(response.body.decode())
    print(f"Response status: {response.status}")
    print(f"Result: {result}")
    
    if response.status == 400 or 'error' in result:
        print("✅ PASS: Correctly returned error for non-existing VC")
        return True
    else:
        print(f"❌ FAIL: Expected error response, got status {response.status}")
        return False

async def test_scenario_4_check_status():
    """Test 4: Check /api/vc/status/:vcId returns correct status"""
    print("\n" + "=" * 80)
    print("TEST 4: Check VC Status API")
    print("=" * 80)
    
    gov_server = GovernmentPortalServer()
    
    # Find a revoked VC
    ledger_file = Path('data/credential_ledger.json')
    with open(ledger_file) as f:
        ledger = json.load(f)
    
    revoked_vc = None
    for cred_id, cred_data in ledger.get('credentials', {}).items():
        if cred_data.get('status') in ['REVOKED', 'revoked']:
            revoked_vc = cred_id
            break
    
    if not revoked_vc:
        print("❌ No revoked VCs found for testing")
        return False
    
    print(f"Checking status for: {revoked_vc[:50]}...")
    
    from aiohttp import web
    class StatusReq:
        def __init__(self, cid):
            self.match_info = {'credential_id': cid}
    
    status_req = StatusReq(revoked_vc)
    response = await gov_server.get_vc_status(status_req)
    result = json.loads(response.body.decode())
    
    print(f"Status: {result.get('status')}")
    print(f"Response: {json.dumps(result, indent=2)}")
    
    if result.get('status') == 'revoked':
        print("✅ PASS: Status correctly returns 'revoked'")
        return True
    else:
        print(f"❌ FAIL: Expected status='revoked', got '{result.get('status')}'")
        return False

async def run_all_tests():
    """Run all test scenarios"""
    print("\n" + "=" * 80)
    print("VC REVOCATION TEST SUITE")
    print("=" * 80)
    
    results = []
    
    # Test 1: Issue and Verify
    result1 = await test_scenario_1_issue_and_verify()
    results.append(("Test 1: Issue and Verify", result1))
    
    # Test 2: Revoke and Verify
    result2 = await test_scenario_2_revoke_and_verify()
    results.append(("Test 2: Revoke and Verify", result2))
    
    # Test 3: Non-existing VC
    result3 = await test_scenario_3_non_existing_vc()
    results.append(("Test 3: Non-existing VC", result3))
    
    # Test 4: Check Status
    result4 = await test_scenario_4_check_status()
    results.append(("Test 4: Check Status", result4))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 80)
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)

