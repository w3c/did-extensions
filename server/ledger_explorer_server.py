#!/usr/bin/env python3
"""
Indy Ledger Explorer Server
Provides a unified interface to view all ledger entries from citizen and government portals
"""

import os
import sys
import json
import asyncio
import secrets
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.hybrid_sdis_implementation import HybridIndyBlockchainManager
from pathlib import Path   
from aiohttp import web, ClientSession
from typing import Dict, List, Any

class LedgerExplorerServer:
    """Indy Ledger Explorer Server"""
    
    def __init__(self):
        self.app = web.Application()
        self.citizen_portal_url = "http://localhost:8082"
        self.government_portal_url = "http://localhost:8081"
        
        # Initialize blockchain manager
        self.blockchain_manager = HybridIndyBlockchainManager()
        print("🔗 Ledger Explorer initialized with Hybrid Indy Blockchain Manager")
        
        # Setup routes
        self.setup_routes()
        
    def setup_routes(self):
        """Setup all routes"""
        
        # Ledger explorer routes
        self.app.router.add_get('/api/ledger/entries', self.get_all_ledger_entries)
        self.app.router.add_get('/api/ledger/citizens', self.get_citizen_ledger_entries)
        self.app.router.add_get('/api/ledger/aadhaar', self.get_aadhaar_ledger_entries)
        self.app.router.add_get('/api/ledger/did/{did}', self.get_did_details)
        self.app.router.add_get('/api/ledger/search', self.search_ledger_entries)
        self.app.router.add_get('/api/ledger/stats', self.get_ledger_stats)
        self.app.router.add_get('/api/ledger/rust-indy', self.get_rust_indy_ledger_data)
        
        # Blockchain integration routes
        self.app.router.add_get('/api/blockchain/status', self.get_blockchain_status)
        self.app.router.add_get('/api/blockchain/dids', self.get_blockchain_dids)
        self.app.router.add_post('/api/blockchain/verify-did', self.verify_blockchain_did)
        
        # Static files
        self.app.router.add_static('/static', Path(__file__).parent.parent / 'static', name='static')
        
        # Add route for root to serve ledger explorer
        self.app.router.add_get('/', self.serve_ledger_explorer)
        
        # Add CORS headers
        @web.middleware
        async def cors_middleware(request, handler):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Session-ID'
            return response
        
        self.app.middlewares.append(cors_middleware)
    
    async def serve_ledger_explorer(self, request):
        """Serve the ledger explorer page"""
        try:
            file_path = Path(__file__).parent.parent / 'static' / 'ledger_explorer.html'
            if file_path.exists():
                return web.FileResponse(file_path)
            else:
                return web.Response(text="Ledger Explorer HTML file not found", status=404)
        except Exception as e:
            print(f"❌ Error serving ledger explorer: {e}")
            return web.Response(text=f"Error: {e}", status=500)
    
    async def get_all_ledger_entries(self, request):
        """Get all ledger entries from both portals with pagination"""
        try:
            # Get pagination parameters
            page = int(request.query.get('page', 1))
            limit = int(request.query.get('limit', 50))  # Default 50 entries per page
            search = request.query.get('search', '')
            entry_type = request.query.get('type', '')  # Filter by type
            
            # Fetch data from both portals concurrently
            citizen_data = await self.fetch_citizen_data()
            aadhaar_data = await self.fetch_aadhaar_data()
            credentials_data = await self.fetch_credentials_data()
            
            # Combine and format ledger entries
            ledger_entries = []
            
            # Add citizen DID entries
            for citizen_id, citizen_info in citizen_data.items():
                entry = {
                    'type': 'CITIZEN_DID',
                    'id': citizen_id,
                    'did': citizen_info.get('did'),
                    'citizen_name': citizen_info.get('personal_details', {}).get('name'),
                    'status': citizen_info.get('status'),
                    'created_at': citizen_info.get('created_at'),
                    'ipfs_link': citizen_info.get('ipfs_link'),
                    'ledger_source': 'Citizen Portal'
                }
                
                # Apply search filter
                if search and search.lower() not in str(entry).lower():
                    continue
                    
                # Apply type filter
                if entry_type and entry['type'] != entry_type:
                    continue
                    
                ledger_entries.append(entry)
            
            # Add credential entries
            for citizen_did, citizen_credentials in credentials_data.items():
                for cred_id, cred_info in citizen_credentials.items():
                    entry = {
                        'type': 'VERIFIABLE_CREDENTIAL',
                        'id': cred_id,
                        'did': citizen_did,
                        'credential_type': cred_info.get('credential_type'),
                        'issuer': cred_info.get('issuer'),
                        'citizen_name': cred_info.get('citizen_name'),
                        'status': cred_info.get('status'),
                        'issued_at': cred_info.get('issued_at'),
                        'expires_at': cred_info.get('expires_at'),
                        'ledger_transaction': cred_info.get('ledger_transaction'),
                        'ipfs_cid': cred_info.get('ipfs_cid'),
                        'ledger_source': 'Citizen Portal'
                    }
                    
                    # Apply search filter
                    if search and search.lower() not in str(entry).lower():
                        continue
                        
                    # Apply type filter
                    if entry_type and entry['type'] != entry_type:
                        continue
                        
                    ledger_entries.append(entry)
            
            # Add Aadhaar KYC entries
            for request_id, aadhaar_info in aadhaar_data.items():
                entry = {
                    'type': 'AADHAAR_KYC',
                    'id': request_id,
                    'did': aadhaar_info.get('citizen_did'),
                    'citizen_name': aadhaar_info.get('citizen_name'),
                    'aadhaar_number': aadhaar_info.get('aadhaar_number'),
                    'status': aadhaar_info.get('status'),
                    'created_at': aadhaar_info.get('requested_at'),
                    'ledger_source': 'Government Portal'
                }
                
                # Apply search filter
                if search and search.lower() not in str(entry).lower():
                    continue
                    
                # Apply type filter
                if entry_type and entry['type'] != entry_type:
                    continue
                    
                ledger_entries.append(entry)
            
            # Sort by creation date (newest first)
            ledger_entries.sort(key=lambda x: x.get('created_at') or x.get('requested_at') or x.get('approved_at') or '', reverse=True)
            
            # Calculate pagination
            total_entries = len(ledger_entries)
            start_index = (page - 1) * limit
            end_index = start_index + limit
            paginated_entries = ledger_entries[start_index:end_index]
            
            # Calculate pagination info
            total_pages = (total_entries + limit - 1) // limit
            has_next = page < total_pages
            has_prev = page > 1
            
            return web.json_response({
                'success': True,
                'total_entries': total_entries,
                'entries': paginated_entries,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'limit': limit,
                    'has_next': has_next,
                    'has_prev': has_prev,
                    'start_index': start_index + 1,
                    'end_index': min(end_index, total_entries)
                },
                'filters': {
                    'search': search,
                    'type': entry_type
                },
                'summary': {
                    'citizen_dids': len([e for e in ledger_entries if e['type'] == 'CITIZEN_DID']),
                    'aadhaar_kycs': len([e for e in ledger_entries if e['type'] == 'AADHAAR_KYC']),
                    'total_citizens': len(set(e['did'] for e in ledger_entries if e['did']))
                }
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Failed to fetch ledger entries: {str(e)}'
            }, status=500)
    
    async def get_citizen_ledger_entries(self, request):
        """Get only citizen DID ledger entries"""
        try:
            citizen_data = await self.fetch_citizen_data()
            
            citizen_entries = []
            for citizen_id, citizen_info in citizen_data.items():
                citizen_entries.append({
                    'citizen_id': citizen_id,
                    'did': citizen_info.get('did'),
                    'citizen_name': citizen_info.get('personal_details', {}).get('name'),
                    'email': citizen_info.get('personal_details', {}).get('email'),
                    'phone': citizen_info.get('personal_details', {}).get('phone'),
                    'status': citizen_info.get('status'),
                    'created_at': citizen_info.get('created_at'),
                    'ipfs_link': citizen_info.get('ipfs_link')
                })
            
            citizen_entries.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return web.json_response({
                'success': True,
                'total_citizens': len(citizen_entries),
                'citizens': citizen_entries
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Failed to fetch citizen entries: {str(e)}'
            }, status=500)
    
    async def get_aadhaar_ledger_entries(self, request):
        """Get only Aadhaar KYC ledger entries"""
        try:
            aadhaar_data = await self.fetch_aadhaar_data()
            
            aadhaar_entries = []
            for request_id, aadhaar_info in aadhaar_data.items():
                aadhaar_entries.append({
                    'request_id': request_id,
                    'citizen_did': aadhaar_info.get('citizen_did'),
                    'citizen_name': aadhaar_info.get('citizen_name'),
                    'aadhaar_number': aadhaar_info.get('aadhaar_number'),
                    'status': aadhaar_info.get('status'),
                    'requested_at': aadhaar_info.get('requested_at'),
                    'approved_at': aadhaar_info.get('approved_at'),
                    'rejected_at': aadhaar_info.get('rejected_at')
                })
            
            aadhaar_entries.sort(key=lambda x: x.get('requested_at', ''), reverse=True)
            
            return web.json_response({
                'success': True,
                'total_requests': len(aadhaar_entries),
                'requests': aadhaar_entries
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Failed to fetch Aadhaar entries: {str(e)}'
            }, status=500)
    
    async def get_did_details(self, request):
        """Get detailed information for a specific DID"""
        try:
            did = request.match_info['did']
            
            # Search in citizen data
            citizen_data = await self.fetch_citizen_data()
            citizen_info = None
            
            for citizen_id, info in citizen_data.items():
                if info.get('did') == did:
                    citizen_info = info
                    break
            
            if not citizen_info:
                return web.json_response({
                    'error': 'DID not found'
                }, status=404)
            
            # Get Aadhaar data for this citizen
            aadhaar_data = await self.fetch_aadhaar_data()
            aadhaar_requests = [
                req for req in aadhaar_data.values() 
                if req.get('citizen_did') == did
            ]
            
            return web.json_response({
                'success': True,
                'did': did,
                'citizen_info': citizen_info,
                'aadhaar_requests': aadhaar_requests,
                'total_aadhaar_requests': len(aadhaar_requests)
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Failed to fetch DID details: {str(e)}'
            }, status=500)
    
    async def search_ledger_entries(self, request):
        """Search ledger entries by various criteria"""
        try:
            query = request.query.get('q', '').lower()
            entry_type = request.query.get('type', '')
            status = request.query.get('status', '')
            
            if not query and not entry_type and not status:
                return web.json_response({
                    'error': 'At least one search parameter is required'
                }, status=400)
            
            # Get all entries
            all_entries_response = await self.get_all_ledger_entries(request)
            if all_entries_response.status != 200:
                return all_entries_response
            
            all_entries = (await all_entries_response.json())['entries']
            
            # Filter entries
            filtered_entries = []
            for entry in all_entries:
                matches = True
                
                # Text search
                if query:
                    searchable_text = f"{entry.get('citizen_name', '')} {entry.get('did', '')} {entry.get('id', '')}".lower()
                    if query not in searchable_text:
                        matches = False
                
                # Type filter
                if entry_type and entry.get('type') != entry_type:
                    matches = False
                
                # Status filter
                if status and entry.get('status') != status:
                    matches = False
                
                if matches:
                    filtered_entries.append(entry)
            
            return web.json_response({
                'success': True,
                'query': query,
                'filters': {
                    'type': entry_type,
                    'status': status
                },
                'total_results': len(filtered_entries),
                'results': filtered_entries
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Search failed: {str(e)}'
            }, status=500)
    
    async def fetch_citizen_data(self) -> Dict[str, Any]:
        """Fetch citizen data from citizen portal"""
        try:
            # Read from the local citizens.json file
            citizens_file = Path(__file__).parent.parent / 'data' / 'citizens.json'
            if citizens_file.exists():
                with open(citizens_file, 'r') as f:
                    citizens_data = json.load(f)
                    print(f"📋 Loaded {len(citizens_data)} citizens from citizens.json")
                    return citizens_data
            return {}
        except Exception as e:
            print(f"Error fetching citizen data: {e}")
            return {}
    
    async def fetch_aadhaar_data(self) -> Dict[str, Any]:
        """Fetch Aadhaar data from shared file"""
        try:
            # Read from the shared aadhaar_requests.json file
            shared_file = Path(__file__).parent.parent / 'data' / 'aadhaar_requests.json'
            if shared_file.exists():
                with open(shared_file, 'r') as f:
                    shared_data = json.load(f)
                    aadhaar_requests = shared_data.get("aadhaar_requests", {})
                    aadhaar_ledger = shared_data.get("aadhaar_ledger", {})
                    print(f"📋 Loaded {len(aadhaar_requests)} Aadhaar requests and {len(aadhaar_ledger)} ledger entries")
                    
                    # Combine requests and ledger entries
                    combined_data = {}
                    combined_data.update(aadhaar_requests)
                    combined_data.update(aadhaar_ledger)
                    return combined_data
            return {}
        except Exception as e:
            print(f"Error fetching Aadhaar data: {e}")
            return {}
    
    async def fetch_credentials_data(self) -> Dict[str, Any]:
        """Fetch credentials data from approved Aadhaar records"""
        try:
            # Read from the shared aadhaar_requests.json file to get approved records
            shared_file = Path(__file__).parent.parent / 'data' / 'aadhaar_requests.json'
            if shared_file.exists():
                with open(shared_file, 'r') as f:
                    shared_data = json.load(f)
                
                approved_aadhaar = shared_data.get("approved_aadhaar", {})
                credentials_data = {}
                
                # Create credentials from approved Aadhaar records
                for citizen_did, aadhaar_record in approved_aadhaar.items():
                    credential_id = f"AADHAAR_KYC_CRED_{citizen_did.split(':')[-1][:8]}"
                    credentials_data[citizen_did] = {
                        credential_id: {
                            'credential_id': credential_id,
                            'credential_type': 'AadhaarKYC',
                            'issuer': 'Government of India',
                            'issuer_did': 'did:sdis:gov:india',
                            'subject_did': citizen_did,
                            'citizen_name': aadhaar_record.get('citizen_name', 'N/A'),
                            'aadhaar_number': aadhaar_record.get('aadhaar_number', 'N/A'),
                            'kyc_level': aadhaar_record.get('kyc_level', 'LEVEL_1'),
                            'status': aadhaar_record.get('status', 'VERIFIED'),
                            'issued_at': aadhaar_record.get('verified_at', datetime.now().isoformat()),
                            'expires_at': (datetime.now() + timedelta(days=365)).isoformat(),
                            'verifiable_credential_hash': aadhaar_record.get('verifiable_credential_hash', ''),
                            'credential_data': aadhaar_record.get('credential_data', {}),
                            'ledger_transaction': f"AADHAAR_KYC_TXN_{citizen_did.split(':')[-1][:8]}",
                            'ipfs_cid': f"Qm{secrets.token_hex(44)}",
                            'revocation_status': 'ACTIVE'
                        }
                    }
                
                print(f"📋 Loaded {len(credentials_data)} citizens with credentials")
                return credentials_data
            
            return {}
        except Exception as e:
            print(f"Error fetching credentials data: {e}")
            return {}
    
    async def get_rust_indy_ledger_data(self, request):
        """Get Rust Indy ledger data"""
        try:
            from rust_style_indy import rust_style_ledger
            
            # Get Rust Indy ledger statistics
            stats = rust_style_ledger.get_ledger_stats()
            
            # Get all transactions
            transactions = rust_style_ledger.get_all_transactions()
            
            # Get all DIDs
            dids = rust_style_ledger.get_all_dids()
            
            # Get all credentials
            credentials = rust_style_ledger.get_all_credentials()
            
            # Get all pools
            pools = rust_style_ledger.get_all_pools()
            
            # Get all wallets
            wallets = rust_style_ledger.get_all_wallets()
            
            return web.json_response({
                'success': True,
                'ledger_type': 'rust_style_indy',
                'statistics': stats,
                'transactions': transactions,
                'dids': dids,
                'credentials': credentials,
                'pools': pools,
                'wallets': wallets
            })
            
        except Exception as e:
            print(f"❌ Error fetching Rust Indy ledger data: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def get_ledger_stats(self, request):
        """Get ledger statistics"""
        try:
            # Fetch data from both sources
            citizen_data = await self.fetch_citizen_data()
            aadhaar_data = await self.fetch_aadhaar_data()
            credentials_data = await self.fetch_credentials_data()
            
            # Count citizen registrations
            citizen_count = len(citizen_data)
            
            # Count Aadhaar requests by status
            aadhaar_requests = {k: v for k, v in aadhaar_data.items() if k.startswith('AADHAAR_REQ_')}
            aadhaar_ledger = {k: v for k, v in aadhaar_data.items() if k.startswith('AADHAAR_KYC_LEDGER_')}
            
            pending_count = sum(1 for req in aadhaar_requests.values() if req.get('status') == 'PENDING')
            approved_count = sum(1 for req in aadhaar_requests.values() if req.get('status') == 'APPROVED')
            ledger_count = len(aadhaar_ledger)
            
            # Count credentials
            total_credentials = sum(len(creds) for creds in credentials_data.values())
            
            return web.json_response({
                'success': True,
                'statistics': {
                    'total_citizens': citizen_count,
                    'total_aadhaar_requests': len(aadhaar_requests),
                    'pending_aadhaar_requests': pending_count,
                    'approved_aadhaar_requests': approved_count,
                    'total_ledger_entries': ledger_count,
                    'total_credentials': total_credentials,
                    'total_entries': citizen_count + len(aadhaar_requests) + ledger_count + total_credentials
                }
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Failed to fetch statistics: {str(e)}'
            }, status=500)
    
    async def get_blockchain_status(self, request):
        """Get blockchain status"""
        try:
            status = await self.blockchain_manager.get_ledger_status()
            return web.json_response({
                'success': True,
                'blockchain_status': status
            })
        except Exception as e:
            return web.json_response({'error': f'Failed to get blockchain status: {str(e)}'}, status=500)
    
    async def get_blockchain_dids(self, request):
        """Get all DIDs from blockchain"""
        try:
            query_result = await self.blockchain_manager.query_ledger({"test": True})
            return web.json_response({
                'success': True,
                'blockchain_dids': query_result
            })
        except Exception as e:
            return web.json_response({'error': f'Failed to get blockchain DIDs: {str(e)}'}, status=500)
    
    async def verify_blockchain_did(self, request):
        """Verify DID on blockchain"""
        try:
            data = await request.json()
            did = data.get('did')
            
            if not did:
                return web.json_response({'error': 'DID is required'}, status=400)
            
            verified = await self.blockchain_manager.verify_did(did)
            
            return web.json_response({
                'success': True,
                'did': did,
                'verified': verified,
                'blockchain': 'indy'
            })
        except Exception as e:
            return web.json_response({'error': f'Failed to verify DID: {str(e)}'}, status=500)

def create_app():
    """Create and return the web application"""
    server = LedgerExplorerServer()
    return server.app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8083)
