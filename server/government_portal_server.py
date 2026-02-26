#!/usr/bin/env python3
"""
Government Portal Server for Aadhaar KYC System
Handles government approval workflow with Rust VC Credential integration
"""

import os
import sys
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from aiohttp import web, ClientSession

# Import the new Rust VC Credential Manager
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server.rust_vc_credential_manager import GovernmentPortalVCIntegration
from server.did_registry_system import DIDRegistrySystem
from server.credential_ledger_system import CredentialLedgerSystem
from server.auto_identity_token_generator import AutoIdentityTokenGenerator
from server.quantum_secure_signature_system import QuantumSecureSignatureSystem
from server.unified_vc_ledger import UnifiedVCLedger
from server.revocation_criteria_system import RevocationCriteria, RevocationReason
from server.service_ledger_system import ServiceLedgerSystem

class GovernmentPortalServer:
    """Government Portal Server for Aadhaar KYC"""
    
    def __init__(self):
        self.app = web.Application()
        self.aadhaar_requests = {}  # Store Aadhaar requests
        self.approved_aadhaar = {}  # Store approved Aadhaar records
        self.aadhaar_ledger = {}  # Store Aadhaar KYC ledger entries
        
        # Initialize Rust VC Credential integration
        self.vc_integration = GovernmentPortalVCIntegration()
        self.did_registry = DIDRegistrySystem()
        self.credential_ledger = CredentialLedgerSystem()
        self.auto_token_generator = AutoIdentityTokenGenerator()
        self.quantum_signature_system = QuantumSecureSignatureSystem()
        self.unified_vc_ledger = UnifiedVCLedger()  # NEW: Unified cross-blockchain ledger
        self.service_ledger = ServiceLedgerSystem()
        
        # Load shared data from file
        self.load_shared_data()
        
        # Setup routes
        self.setup_routes()
    
    async def initialize(self):
        """Initialize the government portal with VC integration"""
        try:
            print("🚀 Initializing Government Portal with Rust VC integration...")
            
            # Initialize VC integration
            await self.vc_integration.initialize()
            
            # Initialize Auto Identity Token Generator
            await self.auto_token_generator.initialize()
            
            print("✅ Government Portal initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Government Portal: {e}")
            return False
    
    def load_shared_data(self):
        """Load shared data from file"""
        try:
            shared_file_path = Path(__file__).parent.parent / 'data' / 'aadhaar_requests.json'
            
            if shared_file_path.exists():
                with open(shared_file_path, 'r') as f:
                    shared_data = json.load(f)
                
                self.aadhaar_requests = shared_data.get("aadhaar_requests", {})
                self.approved_aadhaar = shared_data.get("approved_aadhaar", {})
                self.aadhaar_ledger = shared_data.get("aadhaar_ledger", {})
                
                print(f"📋 Loaded {len(self.aadhaar_requests)} Aadhaar requests from shared file")
            else:
                print("📋 No shared data file found, starting with empty data")
                
        except Exception as e:
            print(f"❌ Error loading shared data: {e}")
    
    def save_shared_data(self):
        """Save shared data to file"""
        try:
            shared_file_path = Path(__file__).parent.parent / 'data' / 'aadhaar_requests.json'
            
            shared_data = {
                "aadhaar_requests": self.aadhaar_requests,
                "approved_aadhaar": self.approved_aadhaar,
                "aadhaar_ledger": self.aadhaar_ledger
            }
            
            with open(shared_file_path, 'w') as f:
                json.dump(shared_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ Error saving shared data: {e}")
            return False
    
    def generate_verifiable_credential_hash(self, citizen_did, aadhaar_number, otp):
        """Generate verifiable credential hash from Aadhaar + DID + OTP"""
        # Create credential data
        credential_data = {
            "citizen_did": citizen_did,
            "aadhaar_number": aadhaar_number,
            "otp": otp,
            "timestamp": datetime.now().isoformat(),
            "credential_type": "AADHAAR_KYC"
        }
        
        # Generate hash
        credential_string = json.dumps(credential_data, sort_keys=True)
        vc_hash = hashlib.sha256(credential_string.encode()).hexdigest()
        
        return vc_hash, credential_data
        
    def setup_routes(self):
        """Setup all routes"""
        
        # Government portal routes
        self.app.router.add_get('/api/government/aadhaar-requests', self.get_all_aadhaar_requests)
        self.app.router.add_get('/api/government/aadhaar-request/{request_id}', self.get_aadhaar_request)
        self.app.router.add_post('/api/government/aadhaar-request/{request_id}/approve', self.approve_aadhaar_request)
        self.app.router.add_post('/api/government/aadhaar-request/{request_id}/reject', self.reject_aadhaar_request)
        self.app.router.add_get('/api/government/aadhaar-ledger', self.get_aadhaar_ledger)
        
        # Quantum-secure signature routes
        self.app.router.add_post('/api/government/verify-quantum-signature', self.verify_quantum_signature)
        self.app.router.add_post('/api/government/verify-token-signature', self.verify_token_signature)
        self.app.router.add_get('/api/government/signature-statistics', self.get_signature_statistics)
        
        # NEW: VC Credential and Registry routes
        self.app.router.add_get('/api/government/did-registry/status', self.get_did_registry_status)
        self.app.router.add_get('/api/government/did-registry/search', self.search_did_registry)
        self.app.router.add_get('/api/government/credential-ledger/status', self.get_credential_ledger_status)
        self.app.router.add_get('/api/government/credential-ledger/search', self.search_credential_ledger)
        self.app.router.add_get('/api/government/vc-transactions/status', self.get_vc_transaction_log_status)
        self.app.router.add_post('/api/government/credential/{credential_id}/revoke', self.revoke_vc_credential)
        self.app.router.add_post('/api/government/did/{did}/revoke', self.revoke_did)
        self.app.router.add_post('/api/government/revoke-did', self.revoke_did_body)   # ← W3C spec alias: body {did, reason}


        # Service request routes
        self.app.router.add_get('/api/government/service-requests', self.get_service_requests)
        self.app.router.add_get('/api/government/service-requests/{request_id}', self.get_service_request)
        self.app.router.add_post('/api/government/service-requests/{request_id}/approve', self.approve_service_request)
        self.app.router.add_post('/api/government/service-requests/{request_id}/reject', self.reject_service_request)
        
        # NEW: VC Status API routes
        self.app.router.add_get('/api/vc/status/{credential_id}', self.get_vc_status)
        
        # NEW: Cross-Blockchain VC Ledger routes
        self.app.router.add_get('/api/government/unified-vc-ledger/stats', self.get_unified_vc_ledger_stats)
        self.app.router.add_get('/api/government/unified-vc-ledger/performance', self.get_unified_vc_performance)
        self.app.router.add_get('/api/government/unified-vc-ledger/blockchain/{blockchain}', self.get_blockchain_credentials)
        self.app.router.add_get('/api/government/cross-chain-mappings', self.get_cross_chain_mappings)
        
        # Static files
        self.app.router.add_static('/static', Path(__file__).parent.parent / 'static', name='static')
        
        # Add route for root to serve index
        self.app.router.add_get('/', self.serve_index)
        
        # Add CORS headers manually
        @web.middleware
        async def cors_middleware(request, handler):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Session-ID'
            return response
        
        self.app.middlewares.append(cors_middleware)
    
    async def serve_index(self, request):
        """Serve the main government portal page"""
        try:
            file_path = Path(__file__).parent.parent / 'static' / 'government_portal.html'
            if file_path.exists():
                return web.FileResponse(file_path)
            else:
                return web.Response(text="Government Portal HTML file not found", status=404)
        except Exception as e:
            print(f"❌ Error serving index: {e}")
            return web.Response(text=f"Error: {e}", status=500)
    
    async def get_all_aadhaar_requests(self, request):
        """4. Government portal can see all citizen requests as verifiable credentials with pagination"""
        try:
            # CRITICAL: Always reload shared data to get latest updates
            self.load_shared_data()
            print(f"📊 Government Portal: Loaded {len(self.aadhaar_requests)} requests")
            
            # Get pagination parameters
            page = int(request.query.get('page', 1))
            limit = int(request.query.get('limit', 20))  # Default 20 requests per page
            status_filter = request.query.get('status', '')  # Filter by status
            
            # Get all Aadhaar requests (both pending and approved)
            all_requests = []
            
            for request_id, req_data in self.aadhaar_requests.items():
                # Apply status filter
                if status_filter and req_data['status'] != status_filter:
                    continue
                
                # Generate verifiable credential hash
                vc_hash, credential_data = self.generate_verifiable_credential_hash(
                    req_data['citizen_did'],
                    req_data['aadhaar_number'],
                    req_data['otp']
                )
                
                request_info = {
                    'request_id': request_id,
                    'citizen_did': req_data['citizen_did'],
                    'citizen_name': req_data['citizen_name'],
                    'aadhaar_number': req_data['aadhaar_number'],
                    'otp': req_data['otp'],
                    'requested_at': req_data['requested_at'],
                    'status': req_data['status'],
                    'verifiable_credential': {
                        'hash': vc_hash,
                        'credential_data': credential_data,
                        'credential_type': 'AADHAAR_KYC',
                        'issuer': 'GOVERNMENT_OF_INDIA',
                        'issued_at': req_data.get('approved_at') or req_data.get('requested_at') or datetime.now().isoformat()
                    }
                }
                
                # Add approval info if approved
                if req_data['status'] == 'APPROVED':
                    approved_at_str = req_data.get('approved_at') or req_data.get('requested_at') or datetime.now().isoformat()
                    request_info['approved_at'] = approved_at_str
                    request_info['approved_by'] = req_data.get('approved_by')
                    
                    # Calculate 24h expiry
                    try:
                        from datetime import timezone, timedelta
                        approved_dt = datetime.fromisoformat(approved_at_str.replace('Z', ''))
                        expires_dt = approved_dt + timedelta(hours=24)
                        expires_at_str = expires_dt.isoformat()
                        request_info['expires_at'] = expires_at_str
                        request_info['verifiable_credential']['issued_at'] = approved_at_str
                        request_info['verifiable_credential']['expires_at'] = expires_at_str
                        
                        # ── Auto-revoke if 24h has passed ──────────────────
                        now = datetime.now()
                        if expires_dt < now and req_data.get('status') != 'REVOKED':
                            print(f"⏰ Auto-revoking expired credential for DID: {req_data['citizen_did']}")
                            # Mark as revoked in memory
                            self.aadhaar_requests[request_id]['status'] = 'REVOKED'
                            self.aadhaar_requests[request_id]['revoked_at'] = now.isoformat()
                            self.aadhaar_requests[request_id]['revocation_reason'] = 'Credential expired after 24 hours'
                            req_data['status'] = 'REVOKED'
                            request_info['status'] = 'REVOKED'
                            request_info['revocation_reason'] = 'Credential expired after 24 hours'
                            # Update approved_aadhaar
                            cdid = req_data['citizen_did']
                            if cdid in self.approved_aadhaar:
                                self.approved_aadhaar[cdid]['status'] = 'REVOKED'
                                self.approved_aadhaar[cdid]['revoked_at'] = now.isoformat()
                                self.approved_aadhaar[cdid]['revocation_reason'] = 'Auto-expired after 24 hours'
                            self.save_shared_data()
                    except Exception as e:
                        print(f"⚠️ Expiry check failed: {e}")
                
                # Add rejection info if rejected
                if req_data['status'] == 'REJECTED':
                    request_info['rejected_at'] = req_data.get('rejected_at')
                    request_info['rejected_by'] = req_data.get('rejected_by')
                    request_info['rejection_reason'] = req_data.get('rejection_reason')
                
                # Add revocation info
                if req_data.get('status') == 'REVOKED':
                    request_info['revoked_at'] = req_data.get('revoked_at')
                    request_info['revocation_reason'] = req_data.get('revocation_reason')
                
                all_requests.append(request_info)

            
            # Sort by requested date (newest first)
            all_requests.sort(key=lambda x: x['requested_at'], reverse=True)
            
            # Calculate pagination
            total_requests = len(all_requests)
            start_index = (page - 1) * limit
            end_index = start_index + limit
            paginated_requests = all_requests[start_index:end_index]
            
            # Calculate pagination info
            total_pages = (total_requests + limit - 1) // limit
            has_next = page < total_pages
            has_prev = page > 1
            
            # Count by status
            pending_count = sum(1 for req in all_requests if req['status'] == 'PENDING')
            approved_count = sum(1 for req in all_requests if req['status'] == 'APPROVED')
            
            return web.json_response({
                'success': True,
                'total_requests': total_requests,
                'pending_requests': pending_count,
                'approved_requests': approved_count,
                'requests': paginated_requests,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'limit': limit,
                    'has_next': has_next,
                    'has_prev': has_prev,
                    'start_index': start_index + 1,
                    'end_index': min(end_index, total_requests)
                },
                'filters': {
                    'status': status_filter
                }
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Failed to fetch requests: {str(e)}'
            }, status=500)
    
    async def get_aadhaar_request(self, request):
        """Get specific Aadhaar request details"""
        request_id = request.match_info['request_id']
        
        if request_id not in self.aadhaar_requests:
            return web.json_response({
                'error': 'Request not found'
            }, status=404)
        
        req_data = self.aadhaar_requests[request_id]
        
        return web.json_response({
            'request_id': request_id,
            'citizen_did': req_data['citizen_did'],
            'citizen_name': req_data['citizen_name'],
            'aadhaar_number': req_data['aadhaar_number'],
            'otp': req_data['otp'],
            'status': req_data['status'],
            'requested_at': req_data['requested_at']
        })
    
    async def approve_aadhaar_request(self, request):
        """5. Government approve request and store on Indy ledger"""
        request_id = request.match_info['request_id']
        
        # Reload shared data to get latest requests
        self.load_shared_data()
        
        if request_id not in self.aadhaar_requests:
            return web.json_response({
                'error': 'Request not found'
            }, status=404)
        
        try:
            req_data = self.aadhaar_requests[request_id]
            
            # Update request status
            req_data['status'] = 'APPROVED'
            req_data['approved_at'] = datetime.now().isoformat()
            req_data['approved_by'] = 'GOVERNMENT_OFFICIAL'
            
            # Generate final verifiable credential hash
            vc_hash, credential_data = self.generate_verifiable_credential_hash(
                req_data['citizen_did'],
                req_data['aadhaar_number'],
                req_data['otp']
            )
            
            # Create approved Aadhaar record
            aadhaar_record = {
                'record_id': f"AADHAAR_REC_{request_id}",
                'citizen_did': req_data['citizen_did'],
                'citizen_name': req_data['citizen_name'],
                'aadhaar_number': req_data['aadhaar_number'],
                'status': 'VERIFIED',
                'verified_at': datetime.now().isoformat(),
                'verified_by': 'GOVERNMENT_PORTAL',
                'kyc_level': 'LEVEL_1',
                'verifiable_credential_hash': vc_hash,
                'credential_data': credential_data
            }
            
            # Store approved record
            self.approved_aadhaar[req_data['citizen_did']] = aadhaar_record
            
            # Create Aadhaar KYC ledger entry
            ledger_entry = {
                'ledger_id': f"AADHAAR_KYC_LEDGER_{secrets.token_hex(8)}",
                'transaction_type': 'AADHAAR_KYC_APPROVAL',
                'citizen_did': req_data['citizen_did'],
                'citizen_name': req_data['citizen_name'],
                'aadhaar_number': req_data['aadhaar_number'],
                'verifiable_credential_hash': vc_hash,
                'status': 'APPROVED',
                'approved_at': datetime.now().isoformat(),
                'approved_by': 'GOVERNMENT_OFFICIAL',
                'kyc_level': 'LEVEL_1',
                'ledger_timestamp': datetime.now().isoformat()
            }
            
            # Store in Aadhaar ledger
            self.aadhaar_ledger[ledger_entry['ledger_id']] = ledger_entry
            
            # Store on Indy ledger (simulated)
            await self.store_aadhaar_on_ledger(aadhaar_record)
            
            # NEW: Issue VC credential using Rust VC integration
            citizen_data = {
                'name': req_data['citizen_name'],
                'email': req_data.get('email', ''),
                'phone': req_data.get('phone', ''),
                'address': req_data.get('address', ''),
                'dob': req_data.get('dob', ''),
                'gender': req_data.get('gender', ''),
                'aadhaar_number': req_data['aadhaar_number'],
                'citizen_did': req_data['citizen_did']  # Pass existing citizen_did
            }
            
            # Issue Aadhaar KYC VC credential via Rust VC integration
            vc_result = await self.vc_integration.approve_kyc_request_with_vc(request_id, citizen_data)
            
            if vc_result['success']:
                print(f"✅ VC credential issued: {vc_result['transaction_id']}")
                
                # Update DID document on IPFS with new credential
                try:
                    from server.did_document_updater import DIDDocumentUpdater
                    updater = DIDDocumentUpdater()
                    update_result = await updater.update_did_document_on_ipfs(req_data['citizen_did'], force_update=True)
                    if update_result.get('success'):
                        print(f"✅ DID document updated on IPFS: {update_result.get('ipfs_cid')}")
                        ledger_entry['did_document_ipfs_cid'] = update_result.get('ipfs_cid')
                        ledger_entry['did_document_ipfs_url'] = update_result.get('ipfs_url')
                    else:
                        print(f"⚠️ DID document update failed: {update_result.get('error')}")
                except Exception as e:
                    print(f"⚠️ Failed to update DID document: {e}")
                
                # Update ledger entry with VC information
                ledger_entry['vc_credential_id'] = vc_result['vc_credential']['id']
                ledger_entry['vc_transaction_id'] = vc_result.get('transaction_id')
                ledger_entry['vc_issued_at'] = vc_result['approved_at']
                ledger_entry['pqie_transaction'] = vc_result.get('pqie_transaction')
                
                # Store VC credential in credential ledger
                await self.credential_ledger.store_credential_transaction(
                    vc_result['vc_credential'],
                    {
                        'transaction_type': 'CREDENTIAL_ISSUANCE',
                        'transaction_id': vc_result.get('transaction_id') or (vc_result.get('pqie_transaction') or {}).get('transaction_id'),
                        'citizen_did': vc_result['citizen_did'],
                        'credential_type': 'aadhaar_kyc',
                        'issued_at': vc_result['approved_at'],
                        'status': 'ISSUED',
                        'ledger_type': 'rust_indy_core',
                        'pqie_protected': True
                    }
                )
                
                # NEW: Also issue on unified cross-blockchain ledger (indy as primary) with cross_chain=True
                unified_result = await self.unified_vc_ledger.issue_credential(
                    req_data['citizen_did'],
                    {
                        'type': 'kyc',
                        'level': 'LEVEL_1',
                        'status': 'VERIFIED',
                        'citizen_data': citizen_data,
                        'vc_credential_id': vc_result['vc_credential']['id']
                    },
                    'indy',
                    cross_chain=True
                )
                if unified_result['success']:
                    print(f"✅ Unified VC issued on Indy with cross-chain support: {unified_result['credential_id']}")
                    ledger_entry['unified_vc_credential_id'] = unified_result['credential_id']
                    ledger_entry['unified_transaction_id'] = unified_result['transaction_id']
                    
                    # NEW: Create cross-chain mappings for other systems
                    for target in ['ethereum', 'polkadot', 'hyperledger_fabric']:
                        mapping_result = await self.unified_vc_ledger.create_cross_chain_mapping(
                            unified_result['credential_id'], target)
                        if mapping_result['success']:
                            print(f"🌐 Created cross-chain mapping for {target}: {mapping_result['transaction_id']}")
                        else:
                            print(f"⚠️ Failed to create cross-chain mapping for {target}: {mapping_result.get('error')}")
            else:
                print(f"⚠️ VC credential issuance failed: {vc_result.get('error', 'Unknown error')}")
            
            # Add credential to Rust ledger
            await self.add_credential_to_rust_ledger(aadhaar_record)
            
            # Generate Auto Identity Token for the citizen
            auto_token_result = await self.generate_auto_identity_token(req_data['citizen_did'], citizen_data)
            
            # Notify citizen portal of approval with auto identity token
            await self.notify_citizen_portal(req_data['citizen_did'], 'APPROVED', auto_token_result)
            
            # Save changes to shared file
            self.save_shared_data()
            
            response_data = {
                'success': True,
                'message': 'Aadhaar e-KYC approved and stored on Indy ledger',
                'record_id': aadhaar_record['record_id'],
                'ledger_id': ledger_entry['ledger_id'],
                'citizen_did': req_data['citizen_did'],
                'vc_credential_id': vc_result['vc_credential']['id'] if vc_result['success'] else None,
                'verifiable_credential_hash': vc_hash,
                'status': 'APPROVED',
                'cooldown_info': {
                    'cooldown_period_days': 90,
                    'next_request_allowed_after': (datetime.now() + timedelta(days=90)).isoformat(),
                    'message': 'Citizen cannot make another Aadhaar e-KYC request for 3 months (90 days)'
                }
            }
            
            # Add auto identity token information if generated successfully
            if auto_token_result and auto_token_result.get('success'):
                response_data['auto_identity_token'] = {
                    'token_id': auto_token_result.get('token_id'),
                    'token_type': auto_token_result.get('token_type'),
                    'expires_at': auto_token_result.get('expires_at'),
                    'generated_at': datetime.now().isoformat(),
                    'message': 'Auto Identity Token generated for government services access'
                }
            
            return web.json_response(response_data)
            
        except Exception as e:
            return web.json_response({
                'error': f'Approval failed: {str(e)}'
            }, status=500)
    
    async def reject_aadhaar_request(self, request):
        """Reject Aadhaar request"""
        request_id = request.match_info['request_id']
        
        # Reload shared data to get latest requests
        self.load_shared_data()
        
        if request_id not in self.aadhaar_requests:
            return web.json_response({
                'error': 'Request not found'
            }, status=404)
        
        try:
            data = await request.json()
            rejection_reason = data.get('reason', 'No reason provided')
            
            req_data = self.aadhaar_requests[request_id]
            
            # Update request status
            req_data['status'] = 'REJECTED'
            req_data['rejected_at'] = datetime.now().isoformat()
            req_data['rejected_by'] = 'GOVERNMENT_OFFICIAL'
            req_data['rejection_reason'] = rejection_reason
            
            # Save changes to shared file
            self.save_shared_data()
            
            return web.json_response({
                'success': True,
                'message': 'Aadhaar e-KYC request rejected',
                'citizen_did': req_data['citizen_did'],
                'status': 'REJECTED',
                'reason': rejection_reason,
                'rejected_at': req_data['rejected_at']
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Rejection failed: {str(e)}'
            }, status=500)
    
    async def notify_citizen_portal(self, citizen_did, status, auto_token_result=None):
        """Notify citizen portal of approval status with auto identity token"""
        try:
            print(f"📢 Notifying citizen portal for DID {citizen_did}: Status {status}")
            
            # Make API call to citizen portal
            async with ClientSession() as session:
                notification_data = {
                    'citizen_did': citizen_did,
                    'status': status,
                    'auto_identity_token': auto_token_result.get('quantum_token') if auto_token_result and auto_token_result.get('success') else None
                }
                
                async with session.post(
                    'http://localhost:8082/api/citizen/notify-kyc-approval',
                    json=notification_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"✅ Citizen portal notification sent: {result.get('message')}")
                        return True
                    else:
                        print(f"❌ Citizen portal notification failed: {response.status}")
                        return False
            
        except Exception as e:
            print(f"❌ Failed to notify citizen portal: {e}")
            return False
    
    async def generate_auto_identity_token(self, citizen_did, citizen_data):
        """Generate auto identity token for approved citizen"""
        try:
            print(f"🎫 Generating Auto Identity Token for citizen DID: {citizen_did}")
            
            # Generate identity token with additional claims
            additional_claims = {
                'kyc_approved': True,
                'kyc_level': 'LEVEL_1',
                'aadhaar_verified': True,
                'government_services_access': True,
                'citizen_name': citizen_data.get('name', ''),
                'aadhaar_number': citizen_data.get('aadhaar_number', '')
            }
            
            # Generate the auto identity token
            token_result = await self.auto_token_generator.generate_auto_identity_token(
                citizen_did, 
                'identity_token', 
                additional_claims
            )
            
            if token_result['success']:
                print(f"✅ Auto Identity Token generated successfully: {token_result['token_id']}")
                return token_result
            else:
                print(f"❌ Failed to generate Auto Identity Token: {token_result.get('error', 'Unknown error')}")
                return {"success": False, "error": token_result.get('error', 'Token generation failed')}
                
        except Exception as e:
            print(f"❌ Error generating Auto Identity Token: {e}")
            return {"success": False, "error": str(e)}
    
    async def verify_quantum_signature(self, request):
        """Verify quantum-secure signature for government services"""
        try:
            data = await request.json()
            signature_id = data.get('signature_id')
            message = data.get('message')
            
            if not signature_id or not message:
                return web.json_response({
                    'error': 'signature_id and message are required'
                }, status=400)
            
            # Verify the quantum signature
            verification_result = await self.quantum_signature_system.verify_signature(
                signature_id, message
            )
            
            if verification_result['success']:
                return web.json_response({
                    'success': True,
                    'is_valid': verification_result['is_valid'],
                    'verification_method': verification_result['verification_method'],
                    'quantum_secure': verification_result['quantum_secure'],
                    'verified_at': verification_result['verified_at']
                })
            else:
                return web.json_response({
                    'success': False,
                    'error': verification_result['error']
                }, status=400)
                
        except Exception as e:
            return web.json_response({
                'error': f'Signature verification failed: {str(e)}'
            }, status=500)
    
    async def verify_token_signature(self, request):
        """Verify auto identity token signature"""
        try:
            data = await request.json()
            quantum_token = data.get('quantum_token')
            
            if not quantum_token:
                return web.json_response({
                    'error': 'quantum_token is required'
                }, status=400)
            
            # Import the quantum secure integration
            from quantum_secure_signature_system import QuantumSecureTokenIntegration
            quantum_integration = QuantumSecureTokenIntegration()
            
            # Verify the quantum-secure token
            verification_result = await quantum_integration.verify_quantum_secure_token(
                quantum_token
            )
            
            if verification_result['success']:
                return web.json_response({
                    'success': True,
                    'is_valid': verification_result['is_valid'],
                    'quantum_secure': verification_result['quantum_secure'],
                    'verification_method': verification_result['verification_method'],
                    'verified_at': verification_result['verified_at'],
                    'citizen_did': quantum_token.get('citizen_did'),
                    'token_id': quantum_token.get('token_id')
                })
            else:
                return web.json_response({
                    'success': False,
                    'error': verification_result['error']
                }, status=400)
                
        except Exception as e:
            return web.json_response({
                'error': f'Token verification failed: {str(e)}'
            }, status=500)
    
    async def get_signature_statistics(self, request):
        """Get quantum signature system statistics"""
        try:
            stats = await self.quantum_signature_system.get_signature_statistics()
            
            return web.json_response({
                'success': True,
                'statistics': stats
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Failed to get signature statistics: {str(e)}'
            }, status=500)
    
    async def store_aadhaar_on_ledger(self, aadhaar_record):
        """Store approved Aadhaar record on Indy ledger"""
        try:
            # Import the blockchain manager
            from hybrid_sdis_implementation import HybridIndyBlockchainManager
            
            blockchain_manager = HybridIndyBlockchainManager()
            
            # Create Aadhaar KYC credential data
            credential_data = {
                'credential_type': 'AADHAAR_KYC',
                'citizen_did': aadhaar_record['citizen_did'],
                'citizen_name': aadhaar_record['citizen_name'],
                'aadhaar_number': aadhaar_record['aadhaar_number'],
                'kyc_level': aadhaar_record['kyc_level'],
                'verified_at': aadhaar_record['verified_at'],
                'verified_by': aadhaar_record['verified_by'],
                'status': aadhaar_record['status']
            }
            
            # Store credential on Indy ledger
            ledger_result = await blockchain_manager.blockchain_manager.store_credential_on_ledger(
                aadhaar_record['citizen_did'],
                credential_data,
                'AADHAAR_KYC'
            )
            
            print(f"📜 Stored Aadhaar record on Indy ledger:")
            print(f"   Record ID: {aadhaar_record['record_id']}")
            print(f"   Citizen DID: {aadhaar_record['citizen_did']}")
            print(f"   Aadhaar Number: {aadhaar_record['aadhaar_number']}")
            print(f"   Status: {aadhaar_record['status']}")
            print(f"   Verified At: {aadhaar_record['verified_at']}")
            print(f"   Ledger Hash: {ledger_result.get('ledger_hash', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Failed to store Aadhaar record on Indy ledger: {e}")
            # Fallback to local storage
            print(f"📜 Storing Aadhaar record locally:")
            print(f"   Record ID: {aadhaar_record['record_id']}")
            print(f"   Citizen DID: {aadhaar_record['citizen_did']}")
            print(f"   Aadhaar Number: {aadhaar_record['aadhaar_number']}")
            print(f"   Status: {aadhaar_record['status']}")
            print(f"   Verified At: {aadhaar_record['verified_at']}")
            print(f"   VC Hash: {aadhaar_record.get('verifiable_credential_hash', 'N/A')}")
        
        # Simulate ledger storage
        ledger_record = {
            'transaction_type': 'AADHAAR_KYC_APPROVAL',
            'record_id': aadhaar_record['record_id'],
            'citizen_did': aadhaar_record['citizen_did'],
            'aadhaar_number': aadhaar_record['aadhaar_number'],
            'status': 'VERIFIED',
            'verifiable_credential_hash': aadhaar_record.get('verifiable_credential_hash'),
            'stored_at': datetime.now().isoformat(),
            'ledger_type': 'AADHAAR_KYC_LEDGER'
        }
        
        # In real implementation, this would be stored on actual Indy ledger
        return ledger_record
    
    async def add_credential_to_rust_ledger(self, aadhaar_record):
        """Add approved Aadhaar credential to Rust Indy Core ledger"""
        try:
            import hashlib
            from datetime import datetime
            
            citizen_did = aadhaar_record['citizen_did']
            credential_id = f'rust_cred_{hashlib.sha256(citizen_did.encode()).hexdigest()[:16]}'
            revoked_at = datetime.now().isoformat()
            
            credential_entry = {
                'credential_id': credential_id,
                'credential_type': 'AADHAAR_KYC',
                'citizen_did': citizen_did,
                'citizen_name': aadhaar_record.get('citizen_name', ''),
                'aadhaar_number': aadhaar_record.get('aadhaar_number', ''),
                'kyc_level': aadhaar_record.get('kyc_level', 'Level 1'),
                'verified_at': aadhaar_record.get('verified_at', revoked_at),
                'verified_by': aadhaar_record.get('verified_by', 'Government of India'),
                'status': aadhaar_record.get('status', 'APPROVED'),
                'verifiable_credential_hash': aadhaar_record.get('verifiable_credential_hash', ''),
                'record_id': aadhaar_record.get('record_id', credential_id),
                'ledger_id': f'AADHAAR_KYC_LEDGER_{citizen_did.split(":")[-1][:8]}'
            }
            
            tx_hash = hashlib.sha256(json.dumps(credential_entry, sort_keys=True).encode()).hexdigest()
            
            # Write to rust_indy_core_ledger.json
            ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
            ledger_data = {}
            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    ledger_data = json.load(f)
            
            transactions = ledger_data.get('transactions', {})
            metadata = ledger_data.get('metadata', {})
            
            transactions[credential_id] = {
                'id': credential_id,
                'transaction_type': 'CREDENTIAL',
                'data': credential_entry,
                'timestamp': revoked_at + 'Z',
                'hash': tx_hash,
                'status': 'COMMITTED',
                'seq_no': metadata.get('total_transactions', 0) + 1
            }
            
            metadata['total_transactions'] = len(transactions)
            metadata['last_updated'] = revoked_at + 'Z'
            ledger_data['transactions'] = transactions
            ledger_data['metadata'] = metadata
            
            with open(ledger_file, 'w') as f:
                json.dump(ledger_data, f, indent=2)
            
            # Also write to rust_style_indy_ledger.json (as before)
            rust_style_file = Path(__file__).parent.parent / 'data' / 'rust_style_indy_ledger.json'
            if rust_style_file.exists():
                with open(rust_style_file, 'r') as f:
                    rust_style = json.load(f)
            else:
                rust_style = {'credentials': {}, 'transactions': {}, 'metadata': {}}
            
            rust_style.setdefault('credentials', {})[citizen_did] = credential_entry
            rust_style.setdefault('transactions', {})[credential_id] = {
                'id': credential_id,
                'transaction_type': 'CREDENTIAL',
                'data': credential_entry,
                'timestamp': revoked_at + 'Z',
                'status': 'COMMITTED'
            }
            rust_style.setdefault('metadata', {})['last_updated'] = revoked_at + 'Z'
            with open(rust_style_file, 'w') as f:
                json.dump(rust_style, f, indent=2)
            
            print(f"✅ Credential written to rust_indy_core_ledger.json: {credential_id}")
            print(f"   Citizen: {aadhaar_record.get('citizen_name')} | DID: {citizen_did}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add credential to Rust ledger: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # NEW: VC Credential and Registry API endpoints
    
    async def get_did_registry_status(self, request):
        """Get DID registry status"""
        try:
            status = await self.did_registry.get_registry_statistics()
            return web.json_response(status)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def search_did_registry(self, request):
        """Search DID registry"""
        try:
            # Get search parameters
            search_type = request.query.get('type', '')  # email, phone, aadhaar, name, status
            search_value = request.query.get('value', '')
            
            if not search_type or not search_value:
                return web.json_response({'error': 'Missing search type or value'}, status=400)
            
            # Perform search
            if search_type == 'email':
                result = await self.did_registry.get_did_by_email(search_value)
            elif search_type == 'phone':
                result = await self.did_registry.get_did_by_phone(search_value)
            elif search_type == 'aadhaar':
                result = await self.did_registry.get_did_by_aadhaar(search_value)
            elif search_type == 'name':
                result = await self.did_registry.lookup_did('by_name', search_value)
            elif search_type == 'status':
                result = await self.did_registry.get_dids_by_status(search_value)
            else:
                return web.json_response({'error': 'Invalid search type'}, status=400)
            
            return web.json_response(result)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_credential_ledger_status(self, request):
        """Get credential ledger status"""
        try:
            status = await self.credential_ledger.get_ledger_statistics()
            return web.json_response(status)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def search_credential_ledger(self, request):
        """Search credential ledger"""
        try:
            # Get search parameters
            citizen_did = request.query.get('citizen_did', '')
            credential_type = request.query.get('credential_type', '')
            status = request.query.get('status', '')
            
            # Build search criteria
            search_criteria = {}
            if citizen_did:
                search_criteria['citizen_did'] = citizen_did
            if credential_type:
                search_criteria['credential_type'] = credential_type
            if status:
                search_criteria['status'] = status
            
            if not search_criteria:
                return web.json_response({'error': 'No search criteria provided'}, status=400)
            
            # Perform search
            result = await self.credential_ledger.search_credentials(search_criteria)
            return web.json_response(result)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_vc_transaction_log_status(self, request):
        """Get VC transaction log status"""
        try:
            status = await self.vc_integration.vc_manager.get_vc_transaction_log_status()
            return web.json_response(status)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def revoke_vc_credential(self, request):
        """Revoke VC credential - marks status as REVOKED in all ledger files"""
        try:
            credential_id = request.match_info['credential_id']
            
            # Get revocation reason from request body
            data = {}
            try:
                data = await request.json()
            except:
                pass
            
            reason_text = data.get('reason', 'Administrative revocation')
            reason_code = data.get('reason_code', 'VC_ADMINISTRATIVE')
            revoked_by = data.get('revoked_by', 'Government Official')
            citizen_did_from_body = data.get('citizen_did', '').strip()
            
            revoked_at = datetime.now().isoformat()
            revocation_updated = False
            resolved_citizen_did = citizen_did_from_body or None
            
            print(f"🔄 Revoke request: credential_id={credential_id}, citizen_did={citizen_did_from_body}")
            
            data_dir = Path(__file__).parent.parent / 'data'
            
            # ── 1. rust_vc_ledger.json ──────────────────────────────
            rust_vc_file = data_dir / 'rust_vc_ledger.json'
            if rust_vc_file.exists():
                with open(rust_vc_file, 'r') as f:
                    rust_vc = json.load(f)
                
                # Update credential entry keyed by citizen_did or credential_id
                creds = rust_vc.get('credentials', {})
                txs = rust_vc.get('transactions', {})
                
                # Try to find by citizen_did match or ID
                for key in list(creds.keys()):
                    cred = creds[key]
                    if (key == citizen_did_from_body or 
                        key == credential_id or
                        cred.get('citizen_did') == citizen_did_from_body):
                        cred['status'] = 'REVOKED'
                        cred['revoked_at'] = revoked_at
                        cred['revocation_reason'] = reason_text
                        cred['revoked_by'] = revoked_by
                        resolved_citizen_did = resolved_citizen_did or cred.get('citizen_did', key)
                        revocation_updated = True
                        print(f"✅ Revoked credential in rust_vc_ledger.json: {key}")
                
                # Also mark the CREDENTIAL transactions
                for tx_id, tx in txs.items():
                    if isinstance(tx, dict) and tx.get('transaction_type') == 'CREDENTIAL':
                        tx_data = tx.get('data', {})
                        if (tx_data.get('citizen_did') == citizen_did_from_body or
                            tx_id == credential_id):
                            tx_data['status'] = 'REVOKED'
                            tx_data['revoked_at'] = revoked_at
                            tx_data['revocation_reason'] = reason_text
                            tx['data'] = tx_data
                            resolved_citizen_did = resolved_citizen_did or tx_data.get('citizen_did')
                            revocation_updated = True
                
                # Add a REVOCATION transaction
                if resolved_citizen_did:
                    rev_tx_id = f"revoke_{secrets.token_hex(8)}"
                    txs[rev_tx_id] = {
                        'id': rev_tx_id,
                        'transaction_type': 'CREDENTIAL_REVOCATION',
                        'data': {
                            'citizen_did': resolved_citizen_did,
                            'credential_id': credential_id,
                            'revocation_reason': reason_text,
                            'reason_code': reason_code,
                            'revoked_by': revoked_by,
                            'revoked_at': revoked_at
                        },
                        'timestamp': revoked_at + 'Z',
                        'status': 'COMMITTED'
                    }
                    rust_vc['transactions'] = txs
                
                with open(rust_vc_file, 'w') as f:
                    json.dump(rust_vc, f, indent=2)
            
            # ── 2. rust_style_indy_ledger.json ─────────────────────
            rust_style_file = data_dir / 'rust_style_indy_ledger.json'
            if rust_style_file.exists():
                with open(rust_style_file, 'r') as f:
                    rust_style = json.load(f)
                
                for key in list(rust_style.get('credentials', {}).keys()):
                    cred = rust_style['credentials'][key]
                    if (key == citizen_did_from_body or
                        key == credential_id or
                        cred.get('citizen_did') == citizen_did_from_body):
                        cred['status'] = 'REVOKED'
                        cred['revoked_at'] = revoked_at
                        cred['revocation_reason'] = reason_text
                        cred['revoked_by'] = revoked_by
                        resolved_citizen_did = resolved_citizen_did or cred.get('citizen_did', key)
                        revocation_updated = True
                        print(f"✅ Revoked in rust_style_indy_ledger: {key}")
                
                for tx_id, tx in rust_style.get('transactions', {}).items():
                    if isinstance(tx, dict) and tx.get('transaction_type') == 'CREDENTIAL':
                        tx_data = tx.get('data', {})
                        if tx_data.get('citizen_did') == citizen_did_from_body:
                            tx_data['status'] = 'REVOKED'
                            tx_data['revoked_at'] = revoked_at
                            tx['data'] = tx_data
                            revocation_updated = True
                
                with open(rust_style_file, 'w') as f:
                    json.dump(rust_style, f, indent=2)
            
            # ── 3. credential_ledger.json ───────────────────────────
            try:
                await self.credential_ledger.revoke_credential(credential_id, reason_text)
            except Exception as e:
                print(f"⚠️ credential_ledger revoke: {e}")
            
            # ── 4. rust_indy_core_ledger.json ─────────────────────── (PRIMARY LEDGER)
            import hashlib as _hashlib
            core_ledger_file = data_dir / 'rust_indy_core_ledger.json'
            try:
                core_data = {}
                if core_ledger_file.exists():
                    with open(core_ledger_file, 'r') as f:
                        core_data = json.load(f)
                core_txs = core_data.get('transactions', {})
                
                # Mark existing CREDENTIAL transactions as REVOKED
                for tx_id, tx in list(core_txs.items()):
                    if isinstance(tx, dict) and tx.get('transaction_type') == 'CREDENTIAL':
                        tx_data = tx.get('data', {})
                        if (tx_data.get('citizen_did') == citizen_did_from_body or tx_id == credential_id):
                            tx_data['status'] = 'REVOKED'
                            tx_data['revoked_at'] = revoked_at
                            tx_data['revocation_reason'] = reason_text
                            tx['data'] = tx_data
                            tx['status'] = 'REVOKED'
                            print(f"✅ Marked CREDENTIAL tx as REVOKED in rust_indy_core_ledger: {tx_id}")
                
                # Add CREDENTIAL_REVOCATION transaction
                if resolved_citizen_did or citizen_did_from_body:
                    rev_id = f"revocation_{_hashlib.sha256((citizen_did_from_body + revoked_at).encode()).hexdigest()[:16]}"
                    core_txs[rev_id] = {
                        'id': rev_id,
                        'transaction_type': 'CREDENTIAL_REVOCATION',
                        'data': {
                            'citizen_did': resolved_citizen_did or citizen_did_from_body,
                            'original_credential_id': credential_id,
                            'revocation_reason': reason_text,
                            'reason_code': reason_code,
                            'revoked_by': revoked_by,
                            'revoked_at': revoked_at,
                            'status': 'COMMITTED'
                        },
                        'timestamp': revoked_at + 'Z',
                        'hash': _hashlib.sha256((credential_id + revoked_at).encode()).hexdigest(),
                        'status': 'COMMITTED',
                        'seq_no': len(core_txs) + 1
                    }
                    core_data['transactions'] = core_txs
                    core_data.setdefault('metadata', {})['last_updated'] = revoked_at + 'Z'
                    core_data['metadata']['total_transactions'] = len(core_txs)
                    with open(core_ledger_file, 'w') as f:
                        json.dump(core_data, f, indent=2)
                    print(f"✅ CREDENTIAL_REVOCATION recorded in rust_indy_core_ledger.json")
                    revocation_updated = True
            except Exception as e:
                print(f"⚠️ rust_indy_core_ledger update failed: {e}")
            
            # ── 5. approved_aadhaar ─────────────────────────────────
            if resolved_citizen_did and resolved_citizen_did in self.approved_aadhaar:
                self.approved_aadhaar[resolved_citizen_did]['status'] = 'REVOKED'
                self.approved_aadhaar[resolved_citizen_did]['revoked_at'] = revoked_at
                self.approved_aadhaar[resolved_citizen_did]['revocation_reason'] = reason_text
                self.save_shared_data()
                print(f"✅ Marked approved_aadhaar REVOKED for: {resolved_citizen_did}")
                revocation_updated = True
            
            # ── 6. aadhaar_requests ─────────────────────────────────
            for req_id, req in self.aadhaar_requests.items():
                if req.get('citizen_did') == (resolved_citizen_did or citizen_did_from_body):
                    if req.get('status') == 'APPROVED':
                        self.aadhaar_requests[req_id]['status'] = 'REVOKED'
                        self.aadhaar_requests[req_id]['revoked_at'] = revoked_at
                        self.aadhaar_requests[req_id]['revocation_reason'] = reason_text
                        self.save_shared_data()
                        print(f"✅ Marked aadhaar_requests REVOKED for request: {req_id}")
            
            # ── 7. Update DID document on IPFS ──────────────────────
            if resolved_citizen_did:
                try:
                    from server.did_document_updater import DIDDocumentUpdater
                    updater = DIDDocumentUpdater()
                    
                    # First load and modify DID doc to include full revocation info
                    did_doc_data = await updater._load_did_document(resolved_citizen_did)
                    if did_doc_data:
                        doc = did_doc_data.get('document', {})
                        doc['credentialStatus'] = 'REVOKED'
                        doc['revocationDetails'] = {
                            'revoked_at': revoked_at,
                            'revocation_reason': reason_text,
                            'reason_code': reason_code,
                            'revoked_by': revoked_by
                        }
                        doc['revokedCredentials'] = doc.get('revokedCredentials', 0) + 1
                        doc['activeCredentials'] = max(0, doc.get('activeCredentials', 1) - 1)
                        doc['updated_at'] = revoked_at
                        did_doc_data['document'] = doc
                        await updater._save_did_document(resolved_citizen_did, did_doc_data)
                    
                    # Now re-upload to IPFS
                    update_result = await updater.update_did_document_on_ipfs(resolved_citizen_did, force_update=True)
                    if update_result.get('success'):
                        print(f"✅ DID document re-pinned to IPFS with REVOKED status: {update_result.get('ipfs_cid')}")
                    else:
                        print(f"⚠️ DID document IPFS update failed: {update_result.get('error')}")
                except Exception as e:
                    print(f"⚠️ DID document update failed: {e}")
            
            if not revocation_updated and not resolved_citizen_did:
                return web.json_response({
                    'success': False,
                    'error': f'Could not find credential for ID/DID: {credential_id}. No credential found to revoke.'
                }, status=404)
            
            return web.json_response({
                'success': True,
                'message': f'Credential revoked successfully',
                'citizen_did': resolved_citizen_did,
                'revoked_at': revoked_at,
                'reason': reason_text,
                'ledger_source': 'all_ledgers'
            })
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({'error': str(e)}, status=500)
    
    async def revoke_did_body(self, request):
        """POST /api/government/revoke-did
        W3C-spec alias: DID passed in the request body instead of URL path.
        Body: {"did": "did:pqie:...", "reason": "...", "revoked_by": "..."}
        Delegates to the same full revocation flow as /api/government/did/{did}/revoke."""
        try:
            data = await request.json()
            did    = data.get('did', '').strip()
            reason = data.get('reason', 'Administrative DID revocation')
            if not did:
                return web.json_response({'success': False, 'error': '"did" is required'}, status=400)
            # reuse the registry + ledger revocation logic
            result_registry = await self.did_registry.revoke_did(did, reason)
            if not result_registry.get('success'):
                return web.json_response(
                    {'success': False, 'error': result_registry.get('error', 'Failed to revoke in registry')},
                    status=400
                )
            ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
            from rust_indy_core import IndyRustCore
            rust_core = IndyRustCore(str(ledger_file))
            result_ledger = await rust_core.revoke_did(did, reason)
            return web.json_response({
                'success': True,
                'message': f'DID {did} revoked — DID_DEACTIVATE recorded on ledger',
                'registry_result': result_registry,
                'ledger_result':   result_ledger,
                'deactivated':     True,
            })
        except Exception as e:
            import traceback; traceback.print_exc()
            return web.json_response({'success': False, 'error': str(e)}, status=500)

    async def revoke_did(self, request):

        """Revoke a DID - marks in registry and records on Rust Indy ledger"""
        try:
            did = request.match_info['did']
            
            # Get revocation reason
            try:
                data = await request.json()
                reason = data.get('reason', 'Administrative DID revocation')
            except:
                reason = 'Administrative DID revocation'
            
            # 1. Update DID Registry
            result_registry = await self.did_registry.revoke_did(did, reason)
            
            if not result_registry.get('success'):
                return web.json_response({'error': result_registry.get('error', 'Failed to revoke in registry')}, status=400)
            
            # 2. Record on Rust Indy Ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
            from rust_indy_core import IndyRustCore
            rust_core = IndyRustCore(str(ledger_file))
            
            result_ledger = await rust_core.revoke_did(did, reason)
            
            # 3. Force update all related VC statuses in credential ledger as well
            # The rust_core.revoke_did already marks them in rust_indy_core_ledger.json
            
            return web.json_response({
                'success': True,
                'message': f'DID {did} revoked successfully',
                'registry_result': result_registry,
                'ledger_result': result_ledger
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_vc_status(self, request):
        """Get VC credential revocation status"""
        try:
            credential_id = request.match_info['credential_id']
            
            # Load credential ledger
            ledger_data = await self.credential_ledger._load_ledger()
            
            if credential_id not in ledger_data.get('credentials', {}):
                return web.json_response({
                    'error': 'VC not found'
                }, status=404)
            
            credential = ledger_data['credentials'][credential_id]
            status = credential.get('status', 'UNKNOWN')
            
            # Check if revoked
            if status in ['REVOKED', 'revoked']:
                return web.json_response({
                    'vc_id': credential_id,
                    'status': 'revoked',
                    'revoked_by': credential.get('revoked_by', 'Government Authority'),
                    'revoked_at': credential.get('revoked_at', 'N/A'),
                    'reason': credential.get('revocation_reason', 'N/A')
                })
            else:
                return web.json_response({
                    'vc_id': credential_id,
                    'status': 'active',
                    'credential_type': credential.get('credential_type'),
                    'issued_at': credential.get('issued_at'),
                    'expires_at': credential.get('expires_at')
                })
                
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_aadhaar_ledger(self, request):
        """Get all Aadhaar KYC ledger entries"""
        try:
            ledger_entries = list(self.aadhaar_ledger.values())
            ledger_entries.sort(key=lambda x: x.get('ledger_timestamp', ''), reverse=True)
            
            return web.json_response({
                'success': True,
                'total_entries': len(ledger_entries),
                'ledger_entries': ledger_entries
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Failed to fetch ledger entries: {str(e)}'
            }, status=500)
    
    async def get_unified_vc_ledger_stats(self, request):
        """Get unified VC ledger statistics"""
        try:
            stats = await self.unified_vc_ledger.get_ledger_statistics()
            return web.json_response(stats)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_unified_vc_performance(self, request):
        """Get unified VC ledger performance metrics"""
        try:
            metrics = await self.unified_vc_ledger.get_performance_metrics()
            return web.json_response({
                'success': True,
                'performance_metrics': metrics
            })
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_blockchain_credentials(self, request):
        """Get credentials for a specific blockchain"""
        try:
            blockchain = request.match_info['blockchain']
            
            # Load ledger
            ledger_data = await self.unified_vc_ledger._load_ledger()
            
            # Get blockchain-specific credentials
            blockchain_creds = ledger_data['blockchain_registries'].get(blockchain, {}).get('credentials', {})
            
            return web.json_response({
                'success': True,
                'blockchain': blockchain,
                'total_credentials': len(blockchain_creds),
                'credentials': list(blockchain_creds.values())
            })
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_service_requests(self, request):
        """Get all service requests with optional status filter"""
        try:
            status = request.query.get('status', None)
            
            result = await self.service_ledger.get_service_requests(status)
            
            return web.json_response(result)
            
        except Exception as e:
            print(f"❌ Error fetching service requests: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def get_service_request(self, request):
        """Get a specific service request by ID"""
        try:
            request_id = request.match_info['request_id']
            
            result = await self.service_ledger.get_service_request(request_id)
            
            return web.json_response(result)
            
        except Exception as e:
            print(f"❌ Error fetching service request: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def approve_service_request(self, request):
        """Approve a service request and create grant"""
        try:
            request_id = request.match_info['request_id']
            
            try:
                data = await request.json()
                approved_by = data.get('approved_by', 'Government Official')
            except:
                approved_by = 'Government Official'
            
            # Approve service request
            result = await self.service_ledger.approve_service_request(request_id, approved_by)
            
            if result.get('success'):
                service_grant = result.get('service_grant')
                
                # Create revocation record for the grant (for tracking purposes)
                # This is actually an approval, but we record it in the service ledger
                grant_record = {
                    'grant_id': service_grant.get('grant_id'),
                    'request_id': request_id,
                    'service_id': service_grant.get('service_id'),
                    'citizen_did': service_grant.get('citizen_did'),
                    'identity_token': service_grant.get('identity_token'),
                    'vc_credential': service_grant.get('vc_credential'),
                    'granted_at': service_grant.get('granted_at'),
                    'status': 'ACTIVE'
                }
                
                return web.json_response({
                    'success': True,
                    'message': 'Service request approved and grant created',
                    'request_id': request_id,
                    'grant_id': result.get('grant_id'),
                    'service_grant': grant_record
                })
            else:
                return web.json_response({
                    'success': False,
                    'error': result.get('error', 'Failed to approve service request')
                }, status=400)
                
        except Exception as e:
            print(f"❌ Error approving service request: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def reject_service_request(self, request):
        """Reject a service request with revocation criteria"""
        try:
            request_id = request.match_info['request_id']
            
            try:
                data = await request.json()
                reason_code = data.get('reason_code', 'GRANT_ADMINISTRATIVE')
                rejection_reason = data.get('rejection_reason', 'Service request rejected')
                rejected_by = data.get('rejected_by', 'Government Official')
                additional_details = data.get('additional_details')
            except:
                reason_code = 'GRANT_ADMINISTRATIVE'
                rejection_reason = 'Service request rejected'
                rejected_by = 'Government Official'
                additional_details = None
            
            # Create revocation record for the service grant rejection
            revocation_record = RevocationCriteria.create_revocation_record(
                entity_type='SERVICE_GRANT',
                entity_id=request_id,
                reason_code=reason_code,
                revoked_by=rejected_by,
                additional_details=additional_details or rejection_reason
            )
            
            # Get detailed explanation from revocation criteria
            if revocation_record.get('success'):
                detailed_reason = revocation_record['revocation_record'].get('explanation', rejection_reason)
            else:
                detailed_reason = rejection_reason
            
            # Reject service request with detailed reason
            result = await self.service_ledger.reject_service_request(
                request_id,
                detailed_reason,
                rejected_by
            )
            
            if result.get('success'):
                # Store revocation details in the service request record
                service_request = result.get('service_request', {})
                service_request['revocation_record'] = revocation_record.get('revocation_record')
                service_request['reason_code'] = reason_code
                
                return web.json_response({
                    'success': True,
                    'message': 'Service request rejected',
                    'request_id': request_id,
                    'service_request': service_request,
                    'revocation_details': revocation_record.get('revocation_record')
                })
            else:
                return web.json_response({
                    'success': False,
                    'error': result.get('error', 'Failed to reject service request')
                }, status=400)
                
        except Exception as e:
            print(f"❌ Error rejecting service request: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def get_cross_chain_mappings(self, request):
        """Get all cross-chain mappings"""
        try:
            ledger_data = await self.unified_vc_ledger._load_ledger()
            mappings = list(ledger_data.get('cross_chain_mappings', {}).values())
            
            return web.json_response({
                'success': True,
                'total_mappings': len(mappings),
                'mappings': mappings
            })
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

def create_app():
    """Create and return the web application"""
    server = GovernmentPortalServer()
    return server.app

if __name__ == '__main__':
    async def start_server():
        server = GovernmentPortalServer()
        await server.initialize()
        return server.app
    
    def main():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app = loop.run_until_complete(start_server())
        web.run_app(app, host='0.0.0.0', port=8081)
    
    if __name__ == "__main__":
        main()
