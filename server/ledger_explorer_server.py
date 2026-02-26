#!/usr/bin/env python3
"""
Indy Ledger Explorer Server
Provides a unified interface to view all ledger entries from citizen and government portals
"""

import os
import sys
import json
import asyncio
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.hybrid_sdis_implementation import HybridIndyBlockchainManager
from server.unified_vc_ledger import UnifiedVCLedger
from server.revocation_criteria_system import RevocationCriteria, RevocationReason
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
        self.unified_vc_ledger = UnifiedVCLedger()
        print("🔗 Ledger Explorer initialized with Hybrid Indy Blockchain Manager")
        print("🌐 Unified VC Ledger initialized for cross-blockchain credentials")
        
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
        self.app.router.add_get('/api/ledger/rust-indy/vc', self.get_rust_indy_vc_ledger_data)
        
        # Unified VC Ledger routes
        self.app.router.add_get('/api/ledger/unified-vc', self.get_unified_vc_ledger_data)
        self.app.router.add_get('/api/ledger/unified-vc/stats', self.get_unified_vc_stats)
        self.app.router.add_get('/api/ledger/unified-vc/performance', self.get_unified_vc_performance)
        self.app.router.add_get('/api/ledger/unified-vc/blockchain/{blockchain}', self.get_unified_vc_blockchain)
        self.app.router.add_get('/api/ledger/unified-vc/mappings', self.get_unified_vc_mappings)
        
        # Revocation routes
        self.app.router.add_get('/api/ledger/revocations', self.get_all_revocations)
        self.app.router.add_get('/api/ledger/revocations/{entity_type}', self.get_revocations_by_type)
        self.app.router.add_get('/api/ledger/revocation-details/{entity_id}', self.get_revocation_details)
        self.app.router.add_get('/api/ledger/revocation-criteria', self.get_revocation_criteria)
        
        # VC Viewer page
        self.app.router.add_get('/vc-viewer', self.serve_vc_viewer)
        
        # Blockchain integration routes
        self.app.router.add_get('/api/blockchain/status', self.get_blockchain_status)
        self.app.router.add_get('/api/blockchain/dids', self.get_blockchain_dids)
        self.app.router.add_post('/api/blockchain/verify-did', self.verify_blockchain_did)
        
        # Static files
        self.app.router.add_static('/static', Path(__file__).parent.parent / 'static', name='static')
        
        # Add route for root to serve ledger explorer
        self.app.router.add_get('/', self.serve_ledger_explorer)
        
        # New explorer pages
        self.app.router.add_get('/explorer/wallet', self.serve_wallet_explorer)
        self.app.router.add_get('/explorer/did', self.serve_did_explorer)
        self.app.router.add_get('/explorer/credentials', self.serve_credentials_explorer)
        self.app.router.add_get('/explorer/transactions', self.serve_transactions_explorer)
        
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
    
    async def serve_vc_viewer(self, request):
        """Serve the VC viewer page"""
        try:
            file_path = Path(__file__).parent.parent / 'static' / 'vc_credential_viewer.html'
            if file_path.exists():
                return web.FileResponse(file_path)
            else:
                return web.Response(text="VC Viewer HTML file not found", status=404)
        except Exception as e:
            print(f"❌ Error serving VC viewer: {e}")
            return web.Response(text=f"Error: {e}", status=500)
            
    async def serve_wallet_explorer(self, request):
        file_path = Path(__file__).parent.parent / 'static' / 'wallet_explorer.html'
        return web.FileResponse(file_path) if file_path.exists() else web.Response(status=404)
        
    async def serve_did_explorer(self, request):
        file_path = Path(__file__).parent.parent / 'static' / 'did_explorer.html'
        return web.FileResponse(file_path) if file_path.exists() else web.Response(status=404)
        
    async def serve_credentials_explorer(self, request):
        file_path = Path(__file__).parent.parent / 'static' / 'credentials_explorer.html'
        return web.FileResponse(file_path) if file_path.exists() else web.Response(status=404)
        
    async def serve_transactions_explorer(self, request):
        file_path = Path(__file__).parent.parent / 'static' / 'transactions_explorer.html'
        return web.FileResponse(file_path) if file_path.exists() else web.Response(status=404)
    
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
            
            # Also load approved_aadhaar from shared data for full credential info
            approved_aadhaar = {}
            try:
                shared_file2 = Path(__file__).parent.parent / 'data' / 'shared_data.json'
                if shared_file2.exists():
                    with open(shared_file2, 'r') as f2:
                        sd = json.load(f2)
                        approved_aadhaar = sd.get('approved_aadhaar', {})
            except Exception:
                pass
            
            return web.json_response({
                'success': True,
                'total_requests': len(aadhaar_entries),
                'requests': aadhaar_entries,
                'approved_aadhaar': approved_aadhaar
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
    
    async def get_rust_indy_vc_ledger_data(self, request):
        """Get raw data from the Rust Indy VC ledger"""
        try:
            # Check for the local file fallback first
            ledger_file = Path(__file__).parent.parent / 'data' / 'rust_vc_ledger.json'
            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    data = json.load(f)
                return web.json_response({
                    "success": True,
                    "ledger_data": data
                })
            else:
                return web.json_response({
                    "success": False,
                    "error": "Failed to find Rust Indy VC ledger"
                }, status=404)
        except Exception as e:
            print(f"❌ Error getting Rust Indy VC ledger data: {e}")
            return web.json_response({
                "success": False,
                "error": str(e)
            }, status=500)

    async def get_rust_indy_ledger_data(self, request):
        """Get Rust Indy ledger data - PRIMARY source for all credential operations"""
        try:
            from rust_indy_core import IndyRustCore
            
            ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
            rust_core = IndyRustCore(str(ledger_file))
            ledger_data = await rust_core.get_ledger_data()
            
            # Extract transactions and credentials
            transactions = ledger_data.get('transactions', {})
            metadata = ledger_data.get('metadata', {})
            
            # Format transactions for display
            formatted_transactions = {}
            credentials_dict = {}
            revocations_dict = {}
            dids_dict = {}
            
            for tx_id, tx in transactions.items():
                tx_type = tx.get('transaction_type', 'UNKNOWN')
                tx_data = tx.get('data', {})
                
                if tx_type == 'CREDENTIAL':
                    # Extract citizen_name from nested credential_data structure
                    credential_data = tx_data.get('credential_data', {})
                    citizen_name = (
                        tx_data.get('citizen_name') or  # Try top level first
                        tx_data.get('name') or  # Try name at top level
                        credential_data.get('name') or  # Try in credential_data
                        'N/A'
                    )
                    
                    # Extract kyc_level - check multiple locations
                    kyc_level = (
                        tx_data.get('kyc_level') or  # Try top level
                        credential_data.get('kyc_level') or  # Try in credential_data
                        None  # Not found yet
                    )
                    
                    # If credential type is aadhaar_kyc and no kyc_level found, use LEVEL_1
                    if not kyc_level:
                        if tx_data.get('credential_type') == 'aadhaar_kyc':
                            kyc_level = 'LEVEL_1'
                        else:
                            kyc_level = 'BASIC'
                    
                    cred_data = {
                        'transaction_id': tx_id,
                        'credential_id': tx_data.get('credential_id'),
                        'citizen_did': tx_data.get('citizen_did'),
                        'citizen_name': citizen_name,
                        'credential_type': tx_data.get('credential_type'),
                        'status': tx_data.get('status', 'ACTIVE'),
                        'kyc_level': kyc_level,
                        'issued_at': tx_data.get('issued_at'),
                        'expires_at': tx_data.get('expires_at'),
                        'timestamp': tx.get('timestamp'),
                        'verified_at': tx_data.get('issued_at'),
                        'transaction': tx
                    }
                    credentials_dict[tx_data.get('credential_id', tx_id)] = cred_data
                elif tx_type == 'CREDENTIAL_REVOCATION':
                    rev_data = {
                        'transaction_id': tx_id,
                        'credential_id': tx_data.get('credential_id'),
                        'revoked_at': tx_data.get('revoked_at'),
                        'revocation_reason': tx_data.get('revocation_reason'),
                        'transaction': tx
                    }
                    revocations_dict[tx_id] = rev_data
                elif tx_type == 'NYM':
                    # Extract DID information from NYM transactions
                    did = tx_data.get('dest') or tx_data.get('did')
                    verkey = tx_data.get('verkey') or tx.get('verkey')
                    role = tx_data.get('role') or tx.get('role', 'CITIZEN')
                    if did:
                        dids_dict[did] = {
                            'did': did,
                            'verkey': verkey,
                            'role': role,
                            'status': tx_data.get('status', 'ACTIVE'),
                            'ipfs_cid': tx_data.get('ipfs_cid'),
                            'created_at': tx.get('timestamp'),
                            'transaction': tx
                        }
                
                formatted_transactions[tx_id] = {
                    'transaction_id': tx_id,
                    'transaction_type': tx_type,
                    'type': tx_type,
                    'did': tx_data.get('dest') or tx_data.get('did') or tx_data.get('citizen_did'),
                    'verkey': tx_data.get('verkey') or tx.get('verkey'),
                    'role': tx_data.get('role') or tx.get('role', 'CITIZEN'),
                    'credential_type': tx_data.get('credential_type'),
                    'citizen_did': tx_data.get('citizen_did'),
                    'status': tx_data.get('status', tx.get('status', 'COMMITTED')),
                    'timestamp': tx.get('timestamp'),
                    'hash': tx.get('hash') or tx.get('transaction_hash'),
                    'transaction_hash': tx.get('hash') or tx.get('transaction_hash'),
                    'seq_no': tx.get('seq_no'),
                    'data': tx_data
                }
            
            # Create statistics object matching frontend expectations
            total_transactions = len(formatted_transactions)
            total_credentials = len(credentials_dict)
            total_dids = len(dids_dict)
            total_pools = len(ledger_data.get('pools', {})) if isinstance(ledger_data.get('pools'), dict) else 0
            total_wallets = len(ledger_data.get('wallets', {})) if isinstance(ledger_data.get('wallets'), dict) else 0
            
            statistics = {
                'total_transactions': total_transactions,
                'total_dids': total_dids,
                'total_credentials': total_credentials,
                'total_pools': total_pools,
                'total_wallets': total_wallets,
                'active_credentials': len([c for c in credentials_dict.values() if c.get('status') not in ['REVOKED', 'revoked']]),
                'revoked_credentials': len(revocations_dict)
            }
            
            return web.json_response({
                'success': True,
                'metadata': metadata,
                'statistics': statistics,  # Frontend expects this
                'transactions': formatted_transactions,  # Changed to dict for consistency
                'dids': dids_dict,  # Added DIDs dictionary
                'credentials': credentials_dict,  # Changed to dict for consistency
                'revocations': revocations_dict,
                'summary': {
                    'total_transactions': total_transactions,
                    'total_credentials': total_credentials,
                    'total_revocations': len(revocations_dict),
                    'active_credentials': statistics['active_credentials']
                }
            })
        except Exception as e:
            print(f"❌ Error fetching Rust Indy ledger data: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def get_all_revocations(self, request):
        """Get all revocations from Rust Indy ledger with detailed information"""
        try:
            from rust_indy_core import IndyRustCore
            
            ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
            rust_core = IndyRustCore(str(ledger_file))
            ledger_data = await rust_core.get_ledger_data()
            
            transactions = ledger_data.get('transactions', {})
            revocations = []
            
            for tx_id, tx in transactions.items():
                if tx.get('transaction_type') == 'CREDENTIAL_REVOCATION':
                    tx_data = tx.get('data', {})
                    credential_id = tx_data.get('credential_id')
                    reason_code = tx_data.get('reason_code') or tx_data.get('revocation_reason', 'VC_ADMINISTRATIVE')
                    # Ensure reason_code is a string
                    if not isinstance(reason_code, str):
                        reason_code = 'VC_ADMINISTRATIVE'
                    
                    # Get revocation details from criteria system
                    revocation_details = RevocationCriteria.get_revocation_details(reason_code, 'VC')
                    
                    # Get the original credential to understand context
                    original_cred = None
                    for orig_tx_id, orig_tx in transactions.items():
                        if orig_tx.get('transaction_type') == 'CREDENTIAL':
                            orig_tx_data = orig_tx.get('data', {})
                            if orig_tx_data.get('credential_id') == credential_id:
                                original_cred = orig_tx_data
                                break
                    
                    revocation_record = {
                        'transaction_id': tx_id,
                        'entity_type': 'VC',
                        'entity_id': credential_id,
                        'reason_code': reason_code if isinstance(reason_code, str) else 'VC_ADMINISTRATIVE',
                        'revoked_at': tx_data.get('revoked_at') or tx.get('timestamp'),
                        'revoked_by': tx_data.get('revoked_by', 'System'),
                        'additional_details': tx_data.get('additional_details'),
                        'original_credential': original_cred,
                        'revocation_details': revocation_details.get('details', {}) if revocation_details.get('success') else None,
                        'severity_color': revocation_details.get('severity_color') if revocation_details.get('success') else '#6c757d'
                    }
                    revocations.append(revocation_record)
            
            # Also check service ledger for service grant revocations
            service_ledger_file = Path(__file__).parent.parent / 'data' / 'service_ledger.json'
            if service_ledger_file.exists():
                with open(service_ledger_file, 'r') as f:
                    service_ledger = json.load(f)
                
                service_requests = service_ledger.get('service_requests', {})
                for req_id, req_data in service_requests.items():
                    if req_data.get('status') == 'REJECTED':
                        reason_code = req_data.get('rejection_reason', 'GRANT_ADMINISTRATIVE')
                        if isinstance(reason_code, dict):
                            reason_code = reason_code.get('code', 'GRANT_ADMINISTRATIVE')
                        
                        revocation_details = RevocationCriteria.get_revocation_details(reason_code, 'SERVICE_GRANT')
                        
                        revocation_record = {
                            'transaction_id': req_id,
                            'entity_type': 'SERVICE_GRANT',
                            'entity_id': req_data.get('grant_id', req_id),
                            'reason_code': reason_code,
                            'revoked_at': req_data.get('rejected_at'),
                            'revoked_by': req_data.get('rejected_by', 'Government Official'),
                            'additional_details': req_data.get('rejection_reason') if isinstance(req_data.get('rejection_reason'), str) else None,
                            'service_id': req_data.get('service_id'),
                            'service_name': req_data.get('service_name'),
                            'citizen_did': req_data.get('citizen_did'),
                            'revocation_details': revocation_details.get('details', {}) if revocation_details.get('success') else None,
                            'severity_color': revocation_details.get('severity_color') if revocation_details.get('success') else '#6c757d'
                        }
                        revocations.append(revocation_record)
            
            # Sort by revoked_at (newest first)
            revocations.sort(key=lambda x: x.get('revoked_at', ''), reverse=True)
            
            return web.json_response({
                'success': True,
                'revocations': revocations,
                'total': len(revocations)
            })
            
        except Exception as e:
            print(f"❌ Error fetching revocations: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def get_revocations_by_type(self, request):
        """Get revocations filtered by entity type (VC, DID, SERVICE_GRANT)"""
        try:
            entity_type = request.match_info['entity_type'].upper()
            
            # Call the revocation logic directly instead of calling get_all_revocations
            from rust_indy_core import IndyRustCore
            
            ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
            rust_core = IndyRustCore(str(ledger_file))
            ledger_data = await rust_core.get_ledger_data()
            
            transactions = ledger_data.get('transactions', {})
            revocations = []
            
            for tx_id, tx in transactions.items():
                if tx.get('transaction_type') == 'CREDENTIAL_REVOCATION':
                    tx_data = tx.get('data', {})
                    credential_id = tx_data.get('credential_id')
                    reason_code = tx_data.get('reason_code') or tx_data.get('revocation_reason', 'VC_ADMINISTRATIVE')
                    
                    # Get revocation details from criteria system
                    revocation_details = RevocationCriteria.get_revocation_details(reason_code, 'VC')
                    
                    revocation_record = {
                        'transaction_id': tx_id,
                        'entity_type': 'VC',
                        'entity_id': credential_id,
                        'reason_code': reason_code if isinstance(reason_code, str) else 'VC_ADMINISTRATIVE',
                        'revoked_at': tx_data.get('revoked_at') or tx.get('timestamp'),
                        'revoked_by': tx_data.get('revoked_by', 'System'),
                        'additional_details': tx_data.get('additional_details'),
                        'revocation_details': revocation_details.get('details', {}) if revocation_details.get('success') else None,
                        'severity_color': revocation_details.get('severity_color') if revocation_details.get('success') else '#6c757d'
                    }
                    revocations.append(revocation_record)
            
            # Also check service ledger for service grant revocations
            service_ledger_file = Path(__file__).parent.parent / 'data' / 'service_ledger.json'
            if service_ledger_file.exists():
                with open(service_ledger_file, 'r') as f:
                    service_ledger = json.load(f)
                
                service_requests = service_ledger.get('service_requests', {})
                for req_id, req_data in service_requests.items():
                    if req_data.get('status') == 'REJECTED':
                        reason_code = req_data.get('rejection_reason', 'GRANT_ADMINISTRATIVE')
                        if isinstance(reason_code, dict):
                            reason_code = reason_code.get('code', 'GRANT_ADMINISTRATIVE')
                        
                        revocation_details = RevocationCriteria.get_revocation_details(reason_code, 'SERVICE_GRANT')
                        
                        revocation_record = {
                            'transaction_id': req_id,
                            'entity_type': 'SERVICE_GRANT',
                            'entity_id': req_data.get('grant_id', req_id),
                            'reason_code': reason_code,
                            'revoked_at': req_data.get('rejected_at'),
                            'revoked_by': req_data.get('rejected_by', 'Government Official'),
                            'additional_details': req_data.get('rejection_reason') if isinstance(req_data.get('rejection_reason'), str) else None,
                            'service_id': req_data.get('service_id'),
                            'service_name': req_data.get('service_name'),
                            'citizen_did': req_data.get('citizen_did'),
                            'revocation_details': revocation_details.get('details', {}) if revocation_details.get('success') else None,
                            'severity_color': revocation_details.get('severity_color') if revocation_details.get('success') else '#6c757d'
                        }
                        revocations.append(revocation_record)
            
            # Filter by entity type
            filtered_revocations = [
                rev for rev in revocations
                if rev.get('entity_type') == entity_type
            ]
            
            # Sort by revoked_at (newest first)
            filtered_revocations.sort(key=lambda x: x.get('revoked_at', ''), reverse=True)
            
            return web.json_response({
                'success': True,
                'entity_type': entity_type,
                'revocations': filtered_revocations,
                'total': len(filtered_revocations)
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def get_revocation_details(self, request):
        """Get detailed revocation information for a specific entity"""
        try:
            entity_id = request.match_info['entity_id']
            
            # Call the revocation logic directly
            from rust_indy_core import IndyRustCore
            
            ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
            rust_core = IndyRustCore(str(ledger_file))
            ledger_data = await rust_core.get_ledger_data()
            
            transactions = ledger_data.get('transactions', {})
            revocation = None
            
            # Search in credential revocations
            for tx_id, tx in transactions.items():
                if tx.get('transaction_type') == 'CREDENTIAL_REVOCATION':
                    tx_data = tx.get('data', {})
                    credential_id = tx_data.get('credential_id')
                    
                    if credential_id == entity_id:
                        reason_code = tx_data.get('reason_code') or tx_data.get('revocation_reason', 'VC_ADMINISTRATIVE')
                        revocation_details = RevocationCriteria.get_revocation_details(reason_code, 'VC')
                        
                        revocation = {
                            'transaction_id': tx_id,
                            'entity_type': 'VC',
                            'entity_id': credential_id,
                            'reason_code': reason_code if isinstance(reason_code, str) else 'VC_ADMINISTRATIVE',
                            'revoked_at': tx_data.get('revoked_at') or tx.get('timestamp'),
                            'revoked_by': tx_data.get('revoked_by', 'System'),
                            'additional_details': tx_data.get('additional_details'),
                            'revocation_details': revocation_details.get('details', {}) if revocation_details.get('success') else None,
                            'severity_color': revocation_details.get('severity_color') if revocation_details.get('success') else '#6c757d'
                        }
                        break
            
            # Search in service ledger if not found
            if not revocation:
                service_ledger_file = Path(__file__).parent.parent / 'data' / 'service_ledger.json'
                if service_ledger_file.exists():
                    with open(service_ledger_file, 'r') as f:
                        service_ledger = json.load(f)
                    
                    service_requests = service_ledger.get('service_requests', {})
                    for req_id, req_data in service_requests.items():
                        grant_id = req_data.get('grant_id', req_id)
                        if grant_id == entity_id and req_data.get('status') == 'REJECTED':
                            reason_code = req_data.get('rejection_reason', 'GRANT_ADMINISTRATIVE')
                            if isinstance(reason_code, dict):
                                reason_code = reason_code.get('code', 'GRANT_ADMINISTRATIVE')
                            
                            revocation_details = RevocationCriteria.get_revocation_details(reason_code, 'SERVICE_GRANT')
                            
                            revocation = {
                                'transaction_id': req_id,
                                'entity_type': 'SERVICE_GRANT',
                                'entity_id': grant_id,
                                'reason_code': reason_code,
                                'revoked_at': req_data.get('rejected_at'),
                                'revoked_by': req_data.get('rejected_by', 'Government Official'),
                                'additional_details': req_data.get('rejection_reason') if isinstance(req_data.get('rejection_reason'), str) else None,
                                'service_id': req_data.get('service_id'),
                                'service_name': req_data.get('service_name'),
                                'citizen_did': req_data.get('citizen_did'),
                                'revocation_details': revocation_details.get('details', {}) if revocation_details.get('success') else None,
                                'severity_color': revocation_details.get('severity_color') if revocation_details.get('success') else '#6c757d'
                            }
                            break
            
            if not revocation:
                return web.json_response({
                    'success': False,
                    'error': f'Revocation not found for entity: {entity_id}'
                }, status=404)
            
            return web.json_response({
                'success': True,
                'revocation': revocation
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def get_revocation_criteria(self, request):
        """Get all available revocation criteria"""
        try:
            entity_type = request.query.get('entity_type', 'VC')
            
            criteria = RevocationCriteria.get_all_revocation_reasons(entity_type.upper())
            
            return web.json_response({
                'success': True,
                'entity_type': entity_type,
                'criteria': criteria,
                'total': len(criteria)
            })
            
        except Exception as e:
            print(f"❌ Error fetching revocation criteria: {e}")
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
            
            # Count citizen registrations
            citizen_count = len(citizen_data)
            
            # Count Aadhaar requests by status
            aadhaar_requests = {k: v for k, v in aadhaar_data.items() if k.startswith('AADHAAR_REQ_')}
            aadhaar_ledger = {k: v for k, v in aadhaar_data.items() if k.startswith('AADHAAR_KYC_LEDGER_')}
            
            pending_count = sum(1 for req in aadhaar_requests.values() if req.get('status') == 'PENDING')
            approved_count = sum(1 for req in aadhaar_requests.values() if req.get('status') == 'APPROVED')
            ledger_count = len(aadhaar_ledger)
            
            return web.json_response({
                'success': True,
                'statistics': {
                    'total_citizens': citizen_count,
                    'total_aadhaar_requests': len(aadhaar_requests),
                    'pending_aadhaar_requests': pending_count,
                    'approved_aadhaar_requests': approved_count,
                    'total_ledger_entries': ledger_count,
                    'total_entries': citizen_count + len(aadhaar_requests) + ledger_count
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
    
    async def get_unified_vc_ledger_data(self, request):
        """Get complete unified VC ledger data"""
        try:
            ledger_data = await self.unified_vc_ledger._load_ledger()
            stats = await self.unified_vc_ledger.get_ledger_statistics()
            
            return web.json_response({
                'success': True,
                'ledger_metadata': stats.get('ledger_metadata', {}),
                'credentials': list(ledger_data.get('credentials', {}).values()),
                'transactions': list(ledger_data.get('transactions', {}).values()),
                'blockchain_registries': ledger_data.get('blockchain_registries', {}),
                'cross_chain_mappings': list(ledger_data.get('cross_chain_mappings', {}).values()),
                'performance_metrics': stats.get('performance_metrics', {})
            })
        except Exception as e:
            return web.json_response({'error': f'Failed to get unified VC ledger: {str(e)}'}, status=500)
    
    async def get_unified_vc_stats(self, request):
        """Get unified VC ledger statistics"""
        try:
            stats = await self.unified_vc_ledger.get_ledger_statistics()
            return web.json_response(stats)
        except Exception as e:
            return web.json_response({'error': f'Failed to get stats: {str(e)}'}, status=500)
    
    async def get_unified_vc_performance(self, request):
        """Get unified VC performance metrics"""
        try:
            metrics = await self.unified_vc_ledger.get_performance_metrics()
            return web.json_response({
                'success': True,
                'performance_metrics': metrics
            })
        except Exception as e:
            return web.json_response({'error': f'Failed to get performance: {str(e)}'}, status=500)
    
    async def get_unified_vc_blockchain(self, request):
        """Get credentials for a specific blockchain"""
        try:
            blockchain = request.match_info['blockchain']
            ledger_data = await self.unified_vc_ledger._load_ledger()
            
            blockchain_creds = ledger_data['blockchain_registries'].get(blockchain, {}).get('credentials', {})
            blockchain_dids = ledger_data['blockchain_registries'].get(blockchain, {}).get('dids', {})
            
            return web.json_response({
                'success': True,
                'blockchain': blockchain,
                'total_credentials': len(blockchain_creds),
                'total_dids': len(blockchain_dids),
                'credentials': list(blockchain_creds.values()),
                'dids': list(blockchain_dids.keys())
            })
        except Exception as e:
            return web.json_response({'error': f'Failed to get blockchain data: {str(e)}'}, status=500)
    
    async def get_unified_vc_mappings(self, request):
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
            return web.json_response({'error': f'Failed to get mappings: {str(e)}'}, status=500)

def create_app():
    """Create and return the web application"""
    server = LedgerExplorerServer()
    return server.app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8083)
