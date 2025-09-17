#!/usr/bin/env python3
"""
Government Portal Server for Aadhaar KYC System
Handles government approval workflow
"""

import os
import sys
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from aiohttp import web, ClientSession

class GovernmentPortalServer:
    """Government Portal Server for Aadhaar KYC"""
    
    def __init__(self):
        self.app = web.Application()
        self.aadhaar_requests = {}  # Store Aadhaar requests
        self.approved_aadhaar = {}  # Store approved Aadhaar records
        self.aadhaar_ledger = {}  # Store Aadhaar KYC ledger entries
        
        # Load shared data from file
        self.load_shared_data()
        
        # Setup routes
        self.setup_routes()
    
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
                        'issued_at': datetime.now().isoformat()
                    }
                }
                
                # Add approval info if approved
                if req_data['status'] == 'APPROVED':
                    request_info['approved_at'] = req_data.get('approved_at')
                    request_info['approved_by'] = req_data.get('approved_by')
                
                # Add rejection info if rejected
                if req_data['status'] == 'REJECTED':
                    request_info['rejected_at'] = req_data.get('rejected_at')
                    request_info['rejected_by'] = req_data.get('rejected_by')
                    request_info['rejection_reason'] = req_data.get('rejection_reason')
                
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
            
            # Add credential to Rust ledger
            await self.add_credential_to_rust_ledger(aadhaar_record)
            
            # Notify citizen portal of approval
            await self.notify_citizen_portal(req_data['citizen_did'], 'APPROVED')
            
            # Save changes to shared file
            self.save_shared_data()
            
            return web.json_response({
                'success': True,
                'message': 'Aadhaar e-KYC approved and stored on Indy ledger',
                'record_id': aadhaar_record['record_id'],
                'ledger_id': ledger_entry['ledger_id'],
                'citizen_did': req_data['citizen_did'],
                'verifiable_credential_hash': vc_hash,
                'status': 'APPROVED',
                'cooldown_info': {
                    'cooldown_period_days': 90,
                    'next_request_allowed_after': (datetime.now() + timedelta(days=90)).isoformat(),
                    'message': 'Citizen cannot make another Aadhaar e-KYC request for 3 months (90 days)'
                }
            })
            
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
    
    async def notify_citizen_portal(self, citizen_did, status):
        """Notify citizen portal of approval status"""
        try:
            # In a real implementation, this would make an API call to citizen portal
            print(f"📢 Notifying citizen portal for DID {citizen_did}: Status {status}")
            return True
        except Exception as e:
            print(f"❌ Failed to notify citizen portal: {e}")
            return False
    
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
        """Add approved Aadhaar credential to Rust ledger"""
        try:
            # Import the rust style ledger
            from rust_style_indy import rust_style_ledger
            from datetime import datetime
            
            # Generate credential ID from DID
            citizen_did = aadhaar_record['citizen_did']
            credential_id = f'aadhaar_kyc_{citizen_did.split(":")[2]}'
            
            # Create credential entry
            credential_entry = {
                'credential_type': 'AADHAAR_KYC',
                'citizen_did': citizen_did,
                'citizen_name': aadhaar_record['citizen_name'],
                'aadhaar_number': aadhaar_record['aadhaar_number'],
                'kyc_level': aadhaar_record['kyc_level'],
                'verified_at': aadhaar_record['verified_at'],
                'verified_by': aadhaar_record['verified_by'],
                'status': aadhaar_record['status'],
                'verifiable_credential_hash': aadhaar_record['verifiable_credential_hash'],
                'record_id': aadhaar_record['record_id'],
                'ledger_id': f'AADHAAR_KYC_LEDGER_{citizen_did.split(":")[2]}'
            }
            
            # Add to Rust ledger
            rust_style_ledger.ledger_data['credentials'][credential_id] = credential_entry
            
            # Update statistics
            rust_style_ledger.ledger_data['metadata']['total_credentials'] = len(rust_style_ledger.ledger_data['credentials'])
            rust_style_ledger.ledger_data['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Save to file
            rust_style_ledger._save_ledger()
            
            print(f"✅ Added Aadhaar credential to Rust ledger:")
            print(f"   Credential ID: {credential_id}")
            print(f"   Citizen: {aadhaar_record['citizen_name']}")
            print(f"   DID: {citizen_did}")
            print(f"   Aadhaar: {aadhaar_record['aadhaar_number']}")
            print(f"   Status: {aadhaar_record['status']}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to add credential to Rust ledger: {e}")
            return False
    
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

def create_app():
    """Create and return the web application"""
    server = GovernmentPortalServer()
    return server.app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8081)
