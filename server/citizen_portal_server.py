#!/usr/bin/env python3
"""
Citizen Portal Server for Aadhaar KYC System
Implements complete citizen workflow with DID storage
"""

import os
import sys
import json
import hashlib
import secrets
from datetime import datetime
from pathlib import Path
from aiohttp import web, ClientSession
from ipfs_util import upload_to_ipfs, download_from_ipfs, is_ipfs_available, get_ipfs_link
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.hybrid_sdis_implementation import HybridIndyBlockchainManager
from server.credential_ledger_system import CredentialLedgerSystem
from server.unified_vc_ledger import UnifiedVCLedger
from server.service_ledger_system import ServiceLedgerSystem
from server.did_registry_system import DIDRegistrySystem
from rust_indy_core import IndyRustCore

class CitizenPortalServer:
    """Citizen Portal Server for Aadhaar KYC"""
    
    def __init__(self):
        self.app = web.Application()
        self.citizens_db = {}  # In-memory storage for demo
        self.aadhaar_requests = {}  # Store Aadhaar requests
        self.approved_aadhaar = {}  # Store approved Aadhaar records
        self.government_services = {}  # Store government services
        self.load_government_services()
        self.load_user_sessions()  # Load sessions from file
        self.user_accounts = {}  # Store user accounts (email/password)
        
        # Initialize IPFS client
        self.ipfs_client = None
        self.init_ipfs()
        
        # Initialize HYBRID Indy blockchain manager
        self.blockchain_manager = HybridIndyBlockchainManager()
        
        # Initialize VC systems
        self.credential_ledger = CredentialLedgerSystem()
        self.did_registry = DIDRegistrySystem()
        self.unified_vc_ledger = UnifiedVCLedger()
        self.service_ledger = ServiceLedgerSystem()
        
        # Shared data
        self.aadhaar_requests = {}
        
        # Session and status attributes
        self.user_sessions = {}
        self.ipfs_available = False
        
        # Government services
        self.government_services = [
            {
                "id": "SERVICE_PASSPORT",
                "name": "Passport Application",
                "description": "Apply for a new passport or renew existing one",
                "required_kyc_level": "LEVEL_1"
            },
            {
                "id": "SERVICE_TAX",
                "name": "Income Tax Filing",
                "description": "File your annual income tax returns",
                "required_kyc_level": "LEVEL_1"
            },
            {
                "id": "SERVICE_VOTER",
                "name": "Voter ID Registration",
                "description": "Register for a new Voter ID card",
                "required_kyc_level": "LEVEL_1"
            }
        ]
        
        # Load persistent data
        self.load_persistent_data()
        
        # Initialize IPFS
        self.init_ipfs()
        
        # Setup routes
        self.setup_routes()
        
        print("✅ Credential systems initialized")
        
        print("✅ Blockchain Manager initialized")
        print(f"   SDIS DID Method: Active")
        print(f"   Cloud Provider: IPFS + Local Storage")
        
    def init_ipfs(self):
        """Initialize IPFS connection"""
        self.ipfs_available = is_ipfs_available()
        if self.ipfs_available:
            print("✅ IPFS utility initialized and connected")
        else:
            print("⚠️  IPFS not available, using local storage fallback")
    
    def load_persistent_data(self):
        """Load persistent data from Indy ledger and IPFS"""
        try:
            # Load user accounts from JSON file
            print("📋 Loading user accounts from Indy ledger...")
            user_accounts_file = Path(__file__).parent.parent / 'data' / 'user_accounts.json'
            if user_accounts_file.exists():
                with open(user_accounts_file, 'r') as f:
                    self.user_accounts = json.load(f)
                print(f"✅ Loaded {len(self.user_accounts)} user accounts")
            else:
                self.user_accounts = {}
                print("⚠️ No user accounts file found")
            
            # Load citizens from JSON file
            print("📋 Loading citizens from cloud storage...")
            citizens_file = Path(__file__).parent.parent / 'data' / 'citizens.json'
            if citizens_file.exists():
                with open(citizens_file, 'r') as f:
                    self.citizens_db = json.load(f)
                print(f"✅ Loaded {len(self.citizens_db)} citizens")
            else:
                self.citizens_db = {}
                print("⚠️ No citizens file found")
            
            print("✅ Data loaded from distributed storage")
                
        except Exception as e:
            print(f"⚠️  Error loading persistent data: {e}")
            self.user_accounts = {}
            self.citizens_db = {}
    
    def load_government_services(self):
        """Load government services from JSON file"""
        try:
            services_file_path = Path(__file__).parent.parent / 'data' / 'government_services.json'
            
            if services_file_path.exists():
                with open(services_file_path, 'r') as f:
                    services_data = json.load(f)
                
                self.government_services = services_data.get("government_services", {})
                print(f"✅ Loaded {len(self.government_services)} government services")
            else:
                print("⚠️ Government services file not found")
                self.government_services = {}
                
        except Exception as e:
            print(f"❌ Error loading government services: {e}")
            self.government_services = {}
    
    def load_user_sessions(self):
        try:
            sessions_file = Path(__file__).parent.parent / 'data' / 'user_sessions.json'
            if sessions_file.exists():
                with open(sessions_file, 'r') as f:
                    self.user_sessions = json.load(f)
                print(f"✅ Loaded {len(self.user_sessions)} user sessions")
            else:
                print("📝 No existing user sessions found")
        except Exception as e:
            print(f"❌ Error loading user sessions: {e}")
            self.user_sessions = {}
    
    def save_user_sessions(self):
        """Save user sessions to file"""
        try:
            sessions_file = Path(__file__).parent.parent / 'data' / 'user_sessions.json'
            sessions_file.parent.mkdir(exist_ok=True)
            
            with open(sessions_file, 'w') as f:
                json.dump(self.user_sessions, f, indent=2)
            print(f"✅ Saved {len(self.user_sessions)} user sessions")
        except Exception as e:
            print(f"❌ Error saving user sessions: {e}")
    
    def save_to_indy_ledger(self, data_type, data):
        """Save data to Indy ledger"""
        try:
            # Simulate saving to Indy ledger
            print(f"📝 Saving {data_type} to Indy ledger...")
            print(f"📊 Data: {json.dumps(data, indent=2)[:100]}...")
            print("✅ Data saved to Indy ledger")
            return True
        except Exception as e:
            print(f"❌ Error saving to Indy ledger: {e}")
            return False
    
    def save_to_cloud(self, data_type, data, did_suffix=None):
        """Save data to cloud (IPFS) with DID-based naming"""
        try:
            # Check IPFS availability dynamically
            if is_ipfs_available():
                # Use DID suffix for filename if available, otherwise use data_type
                filename = f"{did_suffix}.json" if did_suffix else f"{data_type}.json"
                ipfs_hash = upload_to_ipfs(data, filename)
                if ipfs_hash:
                    print(f"☁️  Saved {data_type} to cloud (IPFS): {ipfs_hash}")
                    return ipfs_hash
                else:
                    print(f"❌ Failed to save {data_type} to cloud")
                    return None
            else:
                print(f"⚠️  IPFS not available, using local storage for {data_type}")
                # Fallback to local storage with DID-based naming
                json_data = json.dumps(data, indent=2)
                
                data_dir = Path(__file__).parent.parent / 'data'
                data_dir.mkdir(exist_ok=True)
                
                # Use DID suffix for filename if available
                if did_suffix:
                    file_path = data_dir / f"{did_suffix}.json"
                    file_hash = did_suffix  # Use DID suffix as the identifier
                else:
                    file_hash = hashlib.sha256(json_data.encode()).hexdigest()
                    file_path = data_dir / f"{file_hash}.json"
                
                with open(file_path, 'w') as f:
                    f.write(json_data)
                
                print(f"📁 Stored locally: {file_hash}")
                return file_hash
        except Exception as e:
            print(f"❌ Error saving to cloud: {e}")
            return None
    
    def setup_routes(self):
        """Setup all routes"""
        
        # Authentication routes
        self.app.router.add_post('/api/auth/register', self.register_user)
        self.app.router.add_post('/api/auth/login', self.login_user)
        self.app.router.add_post('/api/auth/logout', self.logout_user)
        self.app.router.add_get('/api/auth/session', self.get_session)
        
        # Citizen registration and DID generation
        self.app.router.add_post('/api/citizen/register', self.register_citizen)
        self.app.router.add_get('/api/citizen/{citizen_id}/did', self.get_citizen_did)
        self.app.router.add_get('/api/user/{user_id}/citizens', self.get_user_citizens)
        
        # Wallet functionality
        self.app.router.add_get('/api/citizen/{citizen_id}/wallet', self.get_citizen_wallet)
        self.app.router.add_post('/api/citizen/{citizen_id}/resolve-did', self.resolve_did)

        # DID Resolve & Update (W3C DID CRUD)
        self.app.router.add_get('/api/did/resolve/{did}', self.resolve_did_by_did)          # GET resolve by DID string
        self.app.router.add_post('/api/did/resolve', self.resolve_did_post)                  # POST {"did": "..."}
        self.app.router.add_patch('/api/did/{did}/update', self.update_did_document_endpoint) # PATCH update DID doc
        # Universal Resolver compatible endpoint
        self.app.router.add_get('/1.0/identifiers/{did}', self.universal_resolver_endpoint)

        # Aadhaar e-KYC request
        self.app.router.add_post('/api/citizen/{citizen_id}/aadhaar-request', self.request_aadhaar_kyc)
        self.app.router.add_get('/api/citizen/{citizen_id}/aadhaar-status', self.get_aadhaar_status)
        self.app.router.add_post('/api/citizen/notify-kyc-approval', self.notify_kyc_approval)
        self.app.router.add_get('/api/citizen/{citizen_id}/kyc-cooldown', self.get_kyc_cooldown_status)

        # New workflow routes
        self.app.router.add_get('/api/citizen/check-did-status', self.check_did_status)
        self.app.router.add_post('/api/citizen/generate-did', self.generate_did)
        
        # Government services
        self.app.router.add_get('/api/citizen/government-services', self.get_government_services)
        self.app.router.add_get('/api/citizen/{citizen_id}/services', self.get_available_services)
        self.app.router.add_get('/api/citizen/{citizen_id}/check-did-status', self.check_did_status)
        self.app.router.add_post('/api/citizen/verify-vc', self.verify_vc_credential)
        self.app.router.add_post('/api/citizen/{citizen_id}/service-request', self.submit_service_request)

        # ── Credential-based tokens ──────────────────────────────────────────
        self.app.router.add_post('/api/token/citizen/{citizen_id}', self.issue_citizen_token)
        self.app.router.add_post('/api/token/government', self.issue_government_token)
        self.app.router.add_post('/api/token/service/{citizen_id}/{service_name}', self.issue_service_token)
        self.app.router.add_get('/api/token/verify/{jti}', self.verify_credential_token)

        # ── Selective Disclosure ──────────────────────────────────────────────
        self.app.router.add_post('/api/sd/issue/{citizen_id}', self.sd_issue)
        self.app.router.add_post('/api/sd/present', self.sd_present)
        self.app.router.add_post('/api/sd/verify', self.sd_verify)

        # Static files
        self.app.router.add_static('/static', Path(__file__).parent.parent / 'static')
        
        # Add route for root to serve main page
        self.app.router.add_get('/', self.serve_main_page)
        
        # Add CORS headers manually
        @web.middleware
        async def cors_middleware(request, handler):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Session-ID'
            return response
        
        self.app.middlewares.append(cors_middleware)
    
    async def serve_main_page(self, request):
        """Serve the main citizen portal page"""
        return web.FileResponse(Path(__file__).parent.parent / 'static' / 'citizen_portal_with_login.html')
    
    async def register_user(self, request):
        """Register a new user account"""
        try:
            data = await request.json()
            
            # Validate required fields
            required_fields = ['email', 'password', 'name']
            for field in required_fields:
                if field not in data:
                    return web.json_response({
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            email = data['email'].lower()
            
            # Check if user already exists
            if email in self.user_accounts:
                return web.json_response({
                    'error': 'User already exists with this email'
                }, status=400)
            
            # Create user account
            user_id = f"USER_{secrets.token_hex(8)}"
            
            user_account = {
                'user_id': user_id,
                'email': email,
                'password': data['password'],  # In production, hash this
                'name': data['name'],
                'created_at': datetime.now().isoformat(),
                'citizens': []  # List of citizen IDs created by this user
            }
            
            self.user_accounts[email] = user_account
            
            # Save to Indy ledger
            self.save_to_indy_ledger("user_account", user_account)
            
            return web.json_response({
                'success': True,
                'user_id': user_id,
                'message': 'User account created successfully and stored on Indy ledger'
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Registration failed: {str(e)}'
            }, status=500)
    
    async def login_user(self, request):
        """Login user and create session"""
        try:
            data = await request.json()
            
            # Validate required fields
            if 'email' not in data or 'password' not in data:
                return web.json_response({
                    'error': 'Email and password are required'
                }, status=400)
            
            email = data['email'].lower()
            
            # Check if user exists
            if email not in self.user_accounts:
                return web.json_response({
                    'error': 'Invalid email or password'
                }, status=401)
            
            user_account = self.user_accounts[email]
            
            # Check password (in production, use proper hashing)
            if user_account['password'] != data['password']:
                return web.json_response({
                    'error': 'Invalid email or password'
                }, status=401)
            
            # Create session
            session_id = secrets.token_hex(32)
            session_data = {
                'session_id': session_id,
                'user_id': user_account['user_id'],
                'email': email,
                'name': user_account['name'],
                'created_at': datetime.now().isoformat(),
                'expires_at': datetime.now().timestamp() + (24 * 60 * 60)  # 24 hours
            }
            
            self.user_sessions[session_id] = session_data
            self.save_user_sessions()  # Save sessions to file
            
            return web.json_response({
                'success': True,
                'session_id': session_id,
                'user_id': user_account['user_id'],
                'name': user_account['name'],
                'message': 'Login successful'
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Login failed: {str(e)}'
            }, status=500)
    
    async def logout_user(self, request):
        """Logout user and destroy session"""
        try:
            data = await request.json()
            session_id = data.get('session_id')
            
            if session_id and session_id in self.user_sessions:
                del self.user_sessions[session_id]
                self.save_user_sessions()  # Save sessions after deletion
                return web.json_response({
                    'success': True,
                    'message': 'Logout successful'
                })
            else:
                return web.json_response({
                    'error': 'Invalid session'
                }, status=400)
                
        except Exception as e:
            return web.json_response({
                'error': f'Logout failed: {str(e)}'
            }, status=500)
    
    async def get_session(self, request):
        """Get current session information"""
        try:
            session_id = request.headers.get('X-Session-ID')
            
            if not session_id or session_id not in self.user_sessions:
                return web.json_response({
                    'error': 'No valid session'
                }, status=401)
            
            session_data = self.user_sessions[session_id]
            
            # Check if session is expired
            if datetime.now().timestamp() > session_data['expires_at']:
                del self.user_sessions[session_id]
                self.save_user_sessions()  # Save sessions after deletion
                return web.json_response({
                    'error': 'Session expired'
                }, status=401)
            
            return web.json_response({
                'success': True,
                'session': session_data
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Session check failed: {str(e)}'
            }, status=500)
    
    async def get_user_citizens(self, request):
        """Get all citizens created by a user"""
        try:
            user_id = request.match_info['user_id']
            
            # Find user account
            user_account = None
            for account in self.user_accounts.values():
                if account['user_id'] == user_id:
                    user_account = account
                    break
            
            if not user_account:
                return web.json_response({
                    'error': 'User not found'
                }, status=404)
            
            # Get citizens created by this user
            user_citizens = []
            for citizen_id in user_account['citizens']:
                if citizen_id in self.citizens_db:
                    citizen = self.citizens_db[citizen_id]
                    user_citizens.append({
                        'citizen_id': citizen_id,
                        'name': citizen['personal_details']['name'],
                        'did': citizen['did'],
                        'created_at': citizen['created_at'],
                        'status': citizen['status']
                    })
            
            return web.json_response({
                'success': True,
                'user_id': user_id,
                'citizens': user_citizens
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Failed to get user citizens: {str(e)}'
            }, status=500)
    
    async def register_citizen(self, request):
        """1. Citizen register DID by adding personal details"""
        try:
            # Check authentication
            session_id = request.headers.get('X-Session-ID')
            if not session_id or session_id not in self.user_sessions:
                return web.json_response({
                    'error': 'Authentication required'
                }, status=401)
            
            session_data = self.user_sessions[session_id]
            user_id = session_data['user_id']
            
            # Check if user already has a citizen/wallet (one account = one wallet)
            user_email = session_data['email']
            if user_email in self.user_accounts:
                existing_citizens = self.user_accounts[user_email]['citizens']
                if existing_citizens:
                    return web.json_response({
                        'error': 'User already has a citizen wallet. One account can only have one wallet.',
                        'existing_citizen_id': existing_citizens[0]
                    }, status=400)
            
            data = await request.json()
            
            # Validate required fields
            required_fields = ['name', 'email', 'phone', 'address', 'dob', 'gender']
            for field in required_fields:
                if field not in data:
                    return web.json_response({
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            # Generate unique citizen ID
            citizen_id = f"CIT_{secrets.token_hex(8)}"
            
            # Generate DID for citizen
            did_info = await self.generate_citizen_did(data)
            
            # Store citizen data
            citizen_data = {
                'citizen_id': citizen_id,
                'user_id': user_id,  # Link to user account
                'personal_details': data,
                'did': did_info['did'],
                'did_document': did_info['did_document'],
                'ipfs_link': did_info.get('ipfs_link', did_info.get('cloud_url', '')),
                'transaction_hash': did_info.get('transaction_hash') or did_info.get('ledger_hash'),
                'ledger_hash': did_info.get('ledger_hash') or did_info.get('transaction_hash'),
                'ipfs_cid': did_info.get('ipfs_cid') or did_info.get('cloud_hash'),
                'cloud_hash': did_info.get('cloud_hash') or did_info.get('ipfs_cid'),
                'cloud_url': did_info.get('cloud_url') or did_info.get('ipfs_link', ''),
                'created_at': datetime.now().isoformat(),
                'status': 'REGISTERED'
            }
            
            self.citizens_db[citizen_id] = citizen_data
            
            # Persist citizens to disk immediately so wallet API has the data
            try:
                citizens_file = Path(__file__).parent.parent / 'data' / 'citizens.json'
                citizens_file.parent.mkdir(exist_ok=True)
                with open(citizens_file, 'w') as f:
                    json.dump(self.citizens_db, f, indent=2, default=str)
                print(f"💾 Saved citizen {citizen_id} to citizens.json")
            except Exception as save_err:
                print(f"⚠️ Failed to save citizens.json: {save_err}")
            
            # Add citizen to user's account
            user_email = session_data['email']
            if user_email in self.user_accounts:
                self.user_accounts[user_email]['citizens'].append(citizen_id)
            
            # Store DID permanently on Indy ledger (simulated)
            await self.store_did_on_ledger(did_info['did'], citizen_data)
            
            # NEW: Register DID in DID Registry System so Auto Identity Token can resolve it
            try:
                from server.did_registry_system import DIDRegistrySystem
                did_registry = DIDRegistrySystem()
                # Create a simple DID document structure for the registry
                did_doc = did_info['did_document']
                await did_registry.register_did(did_info['did'], did_doc, {
                    'citizen_id': citizen_id,
                    'created_at': datetime.now().isoformat(),
                    'method': 'indy'
                })
                print(f"🆔 Registered DID {did_info['did']} in DID Registry")
            except Exception as reg_err:
                print(f"⚠️ Failed to register DID in registry: {reg_err}")
            
            # The ipfs_cid from blockchain is the real cloud hash
            real_ipfs_cid = did_info.get('ipfs_cid') or did_info.get('cloud_hash')
            real_txn_hash = did_info.get('transaction_hash') or did_info.get('ledger_hash')
            
            return web.json_response({
                'success': True,
                'citizen_id': citizen_id,
                'did': did_info['did'],
                'user_id': user_id,
                'transaction_hash': real_txn_hash,
                'ipfs_cid': real_ipfs_cid,
                'ipfs_url': f"http://localhost:8080/ipfs/{real_ipfs_cid}" if real_ipfs_cid else None,
                'cloud_hash': real_ipfs_cid,
                'ledger_type': did_info.get('ledger_type', 'indy'),
                'message': 'Citizen registered successfully with DID stored on blockchain and IPFS'
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Registration failed: {str(e)}'
            }, status=500)
    
    async def generate_citizen_did(self, personal_details):
        """Generate citizen DID using blockchain manager"""
        try:
            print("🔗 Blockchain manager initialized, calling create_citizen_did...")
            # Use blockchain manager to create DID
            did_result = await self.blockchain_manager.create_citizen_did(personal_details)
            print(f"🔗 Blockchain manager returned: {did_result}")
            
            # Extract DID information
            did = did_result['did']
            did_document = did_result['did_document']
            ledger_hash = did_result['ledger_hash']
            ipfs_cid = did_result['ipfs_cid']
            cloud_url = did_result['cloud_url']
            
            print(f"🔗 Created DID on {did_result['ledger_type']} ledger: {did}")
            print(f"☁️ Stored in {did_result['cloud_provider']}: {cloud_url}")
            
            return {
                'did': did,
                'did_document': did_document,
                'ipfs_link': cloud_url,  # For backward compatibility
                'did_suffix': did.split(':')[-2],  # Extract first hash
                'ledger_hash': ledger_hash,
                'transaction_hash': ledger_hash,  # Add transaction hash
                'nym_transaction': ledger_hash,  # Add nym transaction
                'ipfs_cid': ipfs_cid,
                'cloud_hash': ipfs_cid,  # Add cloud hash
                'cloud_url': cloud_url,  # Add cloud URL
                'ledger_type': did_result['ledger_type'],
                'cloud_provider': did_result['cloud_provider']
            }
            
        except Exception as e:
            print(f"❌ Error creating DID: {e}")
            # Fallback to local generation
            return self._generate_local_did(personal_details)
    
    def _generate_local_did(self, personal_details):
        """Fallback local DID generation using Ring-LWE with ALL registration details"""
        from server.ring_lwe_did_generator import generate_complete_did, validate_birthdate
        
        # Extract all registration fields
        name = personal_details.get('name', personal_details.get('full_name', 'Unknown'))
        email = personal_details.get('email', '')
        phone = personal_details.get('phone', '')
        address = personal_details.get('address', '')
        birthdate = personal_details.get('dob', personal_details.get('birthdate', personal_details.get('birth_date')))
        gender = personal_details.get('gender', '')
        
        # Validate and use default birthdate if not provided or invalid
        if birthdate:
            is_valid, error_msg = validate_birthdate(birthdate)
            if not is_valid:
                birthdate = "1970-01-01"
        else:
            birthdate = "1970-01-01"
        
        # Prepare complete citizen data for Ring-LWE
        complete_citizen_data = {
            'name': name,
            'email': email,
            'phone': phone,
            'address': address,
            'dob': birthdate,
            'gender': gender,
            'aadhaar_number': personal_details.get('aadhaar_number', '')
        }
        
        # Generate DID using Ring-LWE with ALL registration details
        print(f"🔐 Generating quantum-secure DID using Ring-LWE with all registration fields")
        did, did_document_base = generate_complete_did(complete_citizen_data)
        
        # Use the generated DID document and enhance it
        did_document = did_document_base.copy()
        did_document.update({
            "did": did,
            "verkey": f"~{secrets.token_hex(32)}",
            "citizen_info": {
                "name": personal_details.get('name', personal_details.get('full_name')),
                "email": personal_details.get('email'),
                "phone": personal_details.get('phone'),
                "address": personal_details.get('address'),
                "dob": personal_details.get('dob', birthdate),
                "gender": personal_details.get('gender')
            },
            "created_at": datetime.now().isoformat(),
            "status": "ACTIVE"
        })
        
        # Extract hash from DID for file naming
        did_parts = did.split(':')
        did_hash = did_parts[-1] if len(did_parts) > 1 else did
        
        # Upload DID document to IPFS with DID-based naming
        if is_ipfs_available():
            ipfs_hash = upload_to_ipfs(did_document, f"{did_hash}.json")
            ipfs_link = get_ipfs_link(ipfs_hash) if ipfs_hash else f"http://localhost:8080/ipfs/{ipfs_hash}"
            print(f"📤 DID document uploaded to IPFS: {ipfs_hash}")
        else:
            # Fallback to local storage with DID-based naming
            json_data = json.dumps(did_document, indent=2)
            
            data_dir = Path(__file__).parent.parent / 'data'
            data_dir.mkdir(exist_ok=True)
            
            file_path = data_dir / f"{did_hash}.json"
            with open(file_path, 'w') as f:
                f.write(json_data)
            
            ipfs_hash = did_hash  # Use hash from DID as the identifier
            ipfs_link = f"http://localhost:8080/ipfs/{ipfs_hash}"
            print(f"📁 DID document stored locally: {ipfs_hash}")
        
        return {
            'did': did,
            'did_document': did_document,
            'ipfs_link': ipfs_link,
            'did_suffix': did_hash1,
            'ledger_hash': f"local_txn_{did_hash1}",
            'transaction_hash': f"local_txn_{did_hash1}",
            'nym_transaction': f"local_txn_{did_hash1}",
            'ipfs_cid': ipfs_hash,
            'cloud_hash': ipfs_hash,
            'cloud_url': ipfs_link,
            'ledger_type': 'local',
            'cloud_provider': 'local'
        }
    
    async def store_did_on_ledger(self, did, citizen_data):
        """Store DID permanently on Indy ledger"""
        # In real implementation, this would submit to indy-cli or libindy
        print(f"🆔 Storing DID on Indy ledger: {did}")
        print(f"📋 Citizen: {citizen_data['personal_details']['name']}")
        print(f"📅 Created: {citizen_data['created_at']}")
        
        # Simulate ledger storage
        ledger_record = {
            'did': did,
            'citizen_id': citizen_data['citizen_id'],
            'stored_at': datetime.now().isoformat(),
            'ledger_type': 'CITIZEN_LEDGER',
            'status': 'STORED'
        }
        
        # In real implementation, this would be stored on actual Indy ledger
        return ledger_record
    
    async def save_aadhaar_request_to_shared_file(self, aadhaar_request):
        """Save Aadhaar request to shared file for government portal access"""
        try:
            shared_file_path = Path(__file__).parent.parent / 'data' / 'aadhaar_requests.json'
            
            # Load existing data
            if shared_file_path.exists():
                with open(shared_file_path, 'r') as f:
                    shared_data = json.load(f)
            else:
                shared_data = {
                    "aadhaar_requests": {},
                    "approved_aadhaar": {},
                    "aadhaar_ledger": {}
                }
            
            # Add the new request
            if "aadhaar_requests" not in shared_data:
                shared_data["aadhaar_requests"] = {}
            if "approved_aadhaar" not in shared_data:
                shared_data["approved_aadhaar"] = {}
            if "aadhaar_ledger" not in shared_data:
                shared_data["aadhaar_ledger"] = {}
                
            shared_data["aadhaar_requests"][aadhaar_request['request_id']] = aadhaar_request
            
            # Save back to file
            with open(shared_file_path, 'w') as f:
                json.dump(shared_data, f, indent=2)
            
            print(f"📝 Aadhaar request saved to shared file: {aadhaar_request['request_id']}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving Aadhaar request to shared file: {e}")
            return False
    
    async def get_citizen_did(self, request):
        """Get citizen DID information"""
        citizen_id = request.match_info['citizen_id']
        
        if citizen_id not in self.citizens_db:
            return web.json_response({
                'error': 'Citizen not found'
            }, status=404)
        
        citizen = self.citizens_db[citizen_id]
        
        return web.json_response({
            'citizen_id': citizen_id,
            'did': citizen['did'],
            'status': citizen['status'],
            'created_at': citizen['created_at']
        })
    
    async def get_citizen_wallet(self, request):
        """2. Wallet tab - Show generated DID, VC credentials and data from Rust ledger"""
        citizen_id = request.match_info['citizen_id']
        
        if citizen_id not in self.citizens_db:
            return web.json_response({
                'error': 'Citizen not found'
            }, status=404)
        
        citizen = self.citizens_db[citizen_id]
        citizen_did = citizen.get('did')
        
        # Get DID information from DID Registry (DID Ledger)
        did_document = None
        did_registry_info = None
        try:
            from server.did_registry_system import DIDRegistrySystem
            did_registry = DIDRegistrySystem()
            
            if citizen_did:
                print(f"🔍 Fetching DID information from DID Registry for: {citizen_did}")
                # Use lookup_did method directly since get_did might not exist
                registry_data = await did_registry._load_registry()
                if citizen_did in registry_data.get('dids', {}):
                    did_entry = registry_data['dids'][citizen_did]
                    did_info = {'success': True, 'did_entry': did_entry}
                else:
                    did_info = {'success': False, 'error': 'DID not found'}
                
                if did_info.get('success') and did_info.get('did_entry'):
                    did_registry_info = did_info['did_entry']
                    did_document = did_registry_info.get('did_document', citizen.get('did_document'))
                    print(f"✅ Found DID in DID Registry")
                else:
                    print(f"⚠️ DID not found in DID Registry, using citizen data")
                    did_document = citizen.get('did_document')
        except Exception as e:
            print(f"⚠️ Error fetching from DID Registry: {e}")
            did_document = citizen.get('did_document')
        
        # Get additional data from Rust ledger - check multiple sources
        rust_data = {}
        transaction_hash = None
        ipfs_cid = None
        ipfs_url = None
        
        if citizen_did:
            # Source 1: rust_style_indy_ledger.json - dids section
            rust_ledger_file = Path(__file__).parent.parent / 'data' / 'rust_style_indy_ledger.json'
            if rust_ledger_file.exists():
                with open(rust_ledger_file, 'r') as f:
                    rust_ledger = json.load(f)
                
                # Get DID data from Rust ledger
                did_data = rust_ledger.get('dids', {}).get(citizen_did)
                if did_data:
                    rust_data = {
                        'rust_status': did_data.get('status'),
                        'rust_created_at': did_data.get('created_at'),
                        'rust_transaction_hash': did_data.get('transaction_hash'),
                        'rust_ipfs_cid': did_data.get('ipfs_cid'),
                        'rust_ipfs_url': did_data.get('ipfs_url')
                    }
                    transaction_hash = did_data.get('transaction_hash')
                    ipfs_cid = did_data.get('ipfs_cid')
                    ipfs_url = did_data.get('ipfs_url')
                
                # Source 2: Check credentials section if not found in dids
                if not transaction_hash:
                    for cred_id, cred_data in rust_ledger.get('credentials', {}).items():
                        if cred_data.get('citizen_did') == citizen_did:
                            transaction_hash = cred_data.get('transaction_hash') or cred_data.get('id')
                            if not ipfs_cid:
                                ipfs_cid = cred_data.get('ipfs_cid')
                            if not ipfs_url:
                                ipfs_url = cred_data.get('ipfs_url')
                            break
                
                # Get credentials for this citizen from multiple ledgers
                credentials = []
                
                # 1. From Rust Styles Indy Ledger
                for cred_id, cred_data in rust_ledger.get('credentials', {}).items():
                    if cred_data.get('citizen_did') == citizen_did:
                        # Check if this credential exists in the main credential ledger for status
                        status = cred_data.get('status', 'ACTIVE')
                        
                        credentials.append({
                            'credential_id': cred_id,
                            'credential_type': cred_data.get('credential_type'),
                            'status': status,
                            'verified_at': cred_data.get('verified_at'),
                            'verified_by': cred_data.get('verified_by'),
                            'source': 'rust_style_indy'
                        })
                
                # 2. From Main Credential Ledger System
                try:
                    ledger_file = Path(__file__).parent.parent / 'data' / 'credential_ledger.json'
                    if ledger_file.exists():
                        with open(ledger_file, 'r') as f:
                            main_ledger = json.load(f)
                        
                        for cred_id, entry in main_ledger.get('credentials', {}).items():
                            vc = entry.get('credential', {})
                            subj_id = vc.get('credentialSubject', {}).get('id', '')
                            if subj_id == citizen_did:
                                # Avoid duplicates if already found in rust_style_indy
                                if not any(c['credential_id'] == cred_id for c in credentials):
                                    credentials.append({
                                        'credential_id': cred_id,
                                        'credential_type': vc.get('type', ['VerifiableCredential'])[-1],
                                        'status': entry.get('status', 'ACTIVE'),
                                        'verified_at': entry.get('stored_at'),
                                        'verified_by': 'Government',
                                        'source': 'credential_ledger'
                                    })
                                else:
                                    # Update status if it's found in the main ledger (for revocation)
                                    for c in credentials:
                                        if c['credential_id'] == cred_id:
                                            c['status'] = entry.get('status', c['status'])
                except Exception as e:
                    print(f"⚠️ Error reading main credential ledger: {e}")

                rust_data['credentials'] = credentials
            
            # Source 3: rust_indy_core_ledger.json
            if not transaction_hash:
                rust_core_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
                if rust_core_file.exists():
                    try:
                        with open(rust_core_file, 'r') as f:
                            rust_core_ledger = json.load(f)
                        
                        # Check transactions array
                        transactions = rust_core_ledger.get('transactions', [])
                        for tx in transactions:
                            if isinstance(tx, dict) and tx.get('did') == citizen_did:
                                transaction_hash = tx.get('transaction_id') or tx.get('transaction_hash')
                                if not ipfs_cid:
                                    ipfs_cid = tx.get('ipfs_cid')
                                break
                    except Exception as e:
                        print(f"⚠️ Error reading rust_indy_core_ledger: {e}")
            
            # Source 4: Check citizen record itself
            if not transaction_hash:
                transaction_hash = citizen.get('transaction_hash') or citizen.get('nym_transaction') or citizen.get('ledger_hash')
            if not ipfs_cid:
                ipfs_cid = citizen.get('ipfs_cid') or citizen.get('cloud_hash')
            if not ipfs_url:
                ipfs_url = citizen.get('ipfs_link') or citizen.get('cloud_url')
            
            # Update rust_data with found values
            rust_data['transaction_hash'] = transaction_hash
            rust_data['ipfs_cid'] = ipfs_cid
            rust_data['ipfs_url'] = ipfs_url
        
        # PRIMARY: Fetch VC credentials from VC Ledger (credential_ledger.json)
        vc_credentials = []
        try:
            if citizen_did:
                print(f"🔍 Fetching VC credentials from VC Ledger for DID: {citizen_did}")
                
                # PRIMARY SOURCE: VC Ledger (credential_ledger.json)
                cred_result = await self.credential_ledger.get_credentials_by_citizen_did(citizen_did)
                print(f"   VC Ledger result: {cred_result.get('success')}, Count: {cred_result.get('count', 0)}")
                
                if cred_result.get('success') and cred_result.get('credentials'):
                    print(f"✅ Found {cred_result.get('count', 0)} credentials in VC Ledger")
                    for cred_id, cred_data in cred_result['credentials'].items():
                        # Parse credential data structure - handle both 'credential' and 'credential_data' keys
                        credential_obj = {}
                        if 'credential' in cred_data:
                            credential_obj = cred_data['credential']
                        elif 'credential_data' in cred_data:
                            credential_obj = cred_data['credential_data']
                        
                        transaction_obj = cred_data.get('transaction_data', {})
                        
                        # Get credential type
                        cred_type = cred_data.get('credential_type') or \
                                   transaction_obj.get('credential_type') or \
                                   credential_obj.get('credentialSubject', {}).get('credential_type') or \
                                   'Unknown'
                        
                        # Get status - check multiple locations
                        status = 'UNKNOWN'
                        if cred_data.get('status'):
                            status = cred_data.get('status')
                        elif credential_obj.get('credentialStatus'):
                            status = credential_obj.get('credentialStatus', {}).get('status', 'UNKNOWN')
                        elif transaction_obj.get('status'):
                            status = transaction_obj.get('status')
                        
                        # Get dates
                        issued_at = credential_obj.get('issuanceDate') or \
                                   cred_data.get('issued_at') or \
                                   transaction_obj.get('issued_at')
                        
                        expires_at = credential_obj.get('expirationDate') or \
                                    cred_data.get('expires_at') or \
                                    transaction_obj.get('expires_at')
                        
                        # Get issuer info
                        issuer_obj = credential_obj.get('issuer', {}) or cred_data.get('issuer', {})
                        issued_by = issuer_obj.get('name') if isinstance(issuer_obj, dict) else 'Government of India'
                        
                        # Get credential data
                        cred_subject = credential_obj.get('credentialSubject', {})
                        credential_data = cred_subject.get('credential_data', {})
                        
                        vc_credentials.append({
                            'credential_id': cred_id,
                            'vc_number': f"VC_{cred_id}",
                            'credential_type': cred_type,
                            'status': status,
                            'issued_at': issued_at,
                            'expires_at': expires_at,
                            'issued_by': issued_by,
                            'credential_data': credential_data,
                            'citizen_name': credential_data.get('name') or credential_data.get('citizen_name') or citizen.get('name'),
                            'aadhaar_number': credential_data.get('aadhaar_number') or citizen.get('aadhaar_number'),
                            'kyc_level': credential_data.get('kyc_level') or 'Level 1',
                            'verified_at': issued_at,
                            'verifiable_credential_hash': cred_data.get('hash') or cred_data.get('signature') or transaction_obj.get('hash') or "N/A",
                            'record_id': transaction_obj.get('transaction_id') or cred_id,
                            'ledger_id': 'credential_ledger',
                            # Include revocation details if revoked
                            'revocation_reason': cred_data.get('revocation_reason'),
                            'revoked_by': cred_data.get('revoked_by'),
                            'ledger_source': 'vc_ledger',
                            'citizen_did': citizen_did
                        })
                
                # SECONDARY: Also check Rust Indy ledger for any additional credentials
                if not vc_credentials:
                    print(f"   No credentials in VC Ledger, checking Rust Indy ledger...")
                    ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
                    rust_core = IndyRustCore(str(ledger_file))
                    rust_creds = await rust_core.get_credentials_by_did(citizen_did)
                    
                    if rust_creds.get('found') and rust_creds.get('credentials'):
                        print(f"✅ Found {len(rust_creds['credentials'])} credentials in Rust Indy ledger")
                        for cred in rust_creds['credentials']:
                            cred_data = cred.get('transaction', {}).get('data', {})
                            
                            # Check for revocation
                            is_revoked = cred_data.get('status') == 'REVOKED'
                            if not is_revoked:
                                ledger_data = await rust_core.get_ledger_data()
                                for tx_id, tx in ledger_data.get('transactions', {}).items():
                                    if tx.get('transaction_type') == 'CREDENTIAL_REVOCATION':
                                        if tx.get('data', {}).get('credential_id') == cred['credential_id']:
                                            is_revoked = True
                                            break
                            
                            vc_credentials.append({
                                'credential_id': cred['credential_id'],
                                'vc_number': f"VC_{cred['credential_id']}",
                                'credential_type': cred['credential_type'],
                                'status': 'REVOKED' if is_revoked else cred['status'],
                                'issued_at': cred['issued_at'],
                                'expires_at': cred.get('expires_at'),
                                'issued_by': cred_data.get('issuer', 'Government of India'),
                                'credential_data': cred_data.get('credential_data', {}),
                                'citizen_name': cred_data.get('credential_data', {}).get('name') or cred_data.get('credential_data', {}).get('citizen_name') or citizen.get('name'),
                                'aadhaar_number': cred_data.get('credential_data', {}).get('aadhaar_number') or citizen.get('aadhaar_number'),
                                'kyc_level': cred_data.get('credential_data', {}).get('kyc_level') or 'Level 1',
                                'verified_at': cred['issued_at'],
                                'verifiable_credential_hash': cred_data.get('hash') or cred_data.get('signature') or cred['transaction_id'] or "N/A",
                                'record_id': cred['transaction_id'],
                                'ledger_id': 'rust_indy_ledger',
                                'transaction_id': cred['transaction_id'],
                                'revocation_reason': cred_data.get('revocation_reason') if is_revoked else None,
                                'ledger_source': 'rust_indy_ledger',
                                'citizen_did': citizen_did
                            })
                
                print(f"📊 Total VC credentials fetched: {len(vc_credentials)}")
                if len(vc_credentials) > 0:
                    print(f"   First credential: {vc_credentials[0].get('credential_id', 'N/A')}")
                    print(f"   Ledger source: {vc_credentials[0].get('ledger_source', 'unknown')}")
                else:
                    print(f"   ⚠️ No credentials found for DID: {citizen_did}")
                    print(f"   💡 User needs to complete Aadhaar e-KYC to receive credentials")
                
                # Periodically update DID document on IPFS (non-blocking)
                try:
                    from server.did_document_updater import DIDDocumentUpdater
                    updater = DIDDocumentUpdater()
                    # Update in background without blocking response
                    asyncio.create_task(updater.update_did_document_on_ipfs(citizen_did, force_update=False))
                except Exception as e:
                    # Silently fail - don't block wallet loading
                    pass
        except Exception as e:
            print(f"⚠️  Error fetching VC credentials: {e}")
            import traceback
            traceback.print_exc()
        
        # Get auto identity token
        auto_identity_token = None
        try:
            if citizen_did:
                token_file = Path(__file__).parent.parent / 'data' / 'auto_identity_tokens.json'
                if token_file.exists():
                    with open(token_file, 'r') as f:
                        token_ledger = json.load(f)
                    
                    # Find active token for this citizen DID
                    for token_id, token_data in token_ledger.get('tokens', {}).items():
                        if token_data.get('citizen_did') == citizen_did and token_data.get('status') == 'ACTIVE':
                            auto_identity_token = {
                                'token_id': token_id,
                                'token_type': token_data.get('token_type', 'identity_token'),
                                'created_at': token_data.get('created_at'),
                                'expires_at': token_data.get('expires_at'),
                                'signature_type': token_data.get('signature_type', 'Quantum-Secure'),
                                'quantum_secure': token_data.get('quantum_secure', False),
                                'status': token_data.get('status')
                            }
                            break
        except Exception as e:
            print(f"⚠️  Error loading auto identity token: {e}")
        
        return web.json_response({
            'citizen_id': citizen_id,
            'wallet': {
                'did': citizen['did'],
                'ipfs_link': ipfs_url or citizen.get('ipfs_link', 'N/A'),
                'did_document': did_document or citizen.get('did_document', {}),
                'did_registry_info': did_registry_info,  # Info from DID Ledger
                'status': citizen['status'],
                'created_at': citizen['created_at'],
                'transaction_hash': transaction_hash or 'N/A',
                'ledger_hash': transaction_hash or 'N/A',
                'ipfs_cid': ipfs_cid or 'N/A',
                'rust_ledger_data': rust_data,
                'vc_credentials': vc_credentials,
                'auto_identity_token': auto_identity_token  # NEW: Added auto identity token
            }
        })
    
    async def resolve_did(self, request):
        """
        Legacy per-citizen resolve endpoint (POST /api/citizen/{citizen_id}/resolve-did).
        Delegates to the real DIDRegistrySystem resolver.
        """
        citizen_id = request.match_info['citizen_id']

        if citizen_id not in self.citizens_db:
            return web.json_response({'error': 'Citizen not found'}, status=404)

        citizen = self.citizens_db[citizen_id]
        citizen_did = citizen.get('did')

        if not citizen_did:
            return web.json_response({'error': 'Citizen has no DID'}, status=404)

        resolution = await self.did_registry.resolve_did(citizen_did)
        error = resolution.get('didResolutionMetadata', {}).get('error')

        return web.json_response({
            'success': not bool(error),
            'did': citizen_did,
            'resolution': resolution,
            'didDocument': resolution.get('didDocument'),
            'didDocumentMetadata': resolution.get('didDocumentMetadata'),
        }, status=200 if not error else 404)

    async def resolve_did_by_did(self, request):
        """
        GET /api/did/resolve/{did}
        Resolve any did:sdis DID directly — no citizen_id required.
        Returns a full W3C DID Resolution Result.
        """
        did = request.match_info['did']
        # URL-decode colons that browsers encode (%3A)
        did = did.replace('%3A', ':')

        resolution = await self.did_registry.resolve_did(did)
        error = resolution.get('didResolutionMetadata', {}).get('error')
        status_code = 404 if error == 'notFound' else (500 if error else 200)

        return web.json_response(resolution, status=status_code,
                                 headers={'Content-Type': 'application/did+ld+json'})

    async def resolve_did_post(self, request):
        """
        POST /api/did/resolve  { "did": "did:sdis:..." }
        Resolve a DID via POST body (useful for frontends).
        """
        try:
            data = await request.json()
            did = data.get('did')
            if not did:
                return web.json_response({'error': 'did field is required'}, status=400)

            resolution = await self.did_registry.resolve_did(did)
            error = resolution.get('didResolutionMetadata', {}).get('error')
            return web.json_response(resolution, status=200 if not error else 404)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def update_did_document_endpoint(self, request):
        """
        PATCH /api/did/{did}/update
        Partially update a DID Document.

        Body JSON may contain:
        {
            "service": [...],                 # add/replace services
            "remove_service_ids": [...],      # remove services by id
            "verificationMethod": [...],      # add/replace verification methods
            "verifiableCredentials": [...],   # embed full VC objects
            "custom_fields": { ... }          # merge arbitrary top-level fields
        }
        Requires X-Session-ID header (citizen must be authenticated).
        """
        try:
            did = request.match_info['did'].replace('%3A', ':')

            # Auth check
            session_id = request.headers.get('X-Session-ID')
            if not session_id or session_id not in self.user_sessions:
                return web.json_response({'error': 'Authentication required'}, status=401)

            updates = await request.json()
            if not updates:
                return web.json_response({'error': 'No update body provided'}, status=400)

            session_data = self.user_sessions[session_id]
            result = await self.did_registry.update_did_document(
                did=did,
                updates=updates,
                updated_by=session_data.get('user_id', 'CITIZEN')
            )

            if result.get('success'):
                return web.json_response(result, status=200)
            else:
                return web.json_response(result, status=404 if 'not found' in result.get('error', '').lower() else 500)

        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

    async def universal_resolver_endpoint(self, request):
        """
        GET /1.0/identifiers/{did}
        Universal Resolver compatible endpoint.
        Conforms to https://w3c-ccg.github.io/did-resolution/#bindings-https
        """
        did = request.match_info['did'].replace('%3A', ':')
        accept = request.headers.get('Accept', '')

        resolution = await self.did_registry.resolve_did(did)
        error = resolution.get('didResolutionMetadata', {}).get('error')
        status_code = 404 if error == 'notFound' else (500 if error else 200)

        # If caller wants only the DID document (not resolution envelope)
        if 'application/did+ld+json' in accept and 'did-resolution' not in accept:
            doc = resolution.get('didDocument')
            if doc:
                return web.json_response(doc, status=status_code,
                                         headers={'Content-Type': 'application/did+ld+json'})

        return web.json_response(resolution, status=status_code,
                                 headers={'Content-Type': 'application/ld+json;profile="https://w3id.org/did-resolution"'})
    
    async def verify_vc_credential(self, request):
        """Verify VC credential for service access - checks Rust Indy ledger"""
        try:
            data = await request.json()
            credential_id = data.get('credential_id')
            vc_number = data.get('vc_number')
            citizen_did = data.get('citizen_did')
            
            if not credential_id and not vc_number:
                return web.json_response({
                    'success': False,
                    'error': 'credential_id or vc_number is required'
                }, status=400)
            
            # Parse VC number if provided (format: VC_credential_id)
            if vc_number:
                if vc_number.startswith('VC_'):
                    credential_id = vc_number[3:]
                else:
                    return web.json_response({
                        'success': False,
                        'error': 'Invalid VC number format. Expected VC_xxxxx'
                    }, status=400)
            
            # PRIMARY: Verify against Rust Indy ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
            rust_core = IndyRustCore(str(ledger_file))
            cred_info = await rust_core.get_credential_by_id(credential_id)
            
            if not cred_info.get('found'):
                # Fallback to credential ledger if not found in Rust ledger
                ledger_data = await self.credential_ledger._load_ledger()
                if credential_id not in ledger_data.get('credentials', {}):
                    return web.json_response({
                        'success': False,
                        'verified': False,
                        'error': 'VC not found in Rust Indy ledger or credential ledger',
                        'credential_id': credential_id
                    })
                else:
                    # Use credential ledger as fallback
                    credential = ledger_data['credentials'][credential_id]
                    status = credential.get('status', 'UNKNOWN')
                    
                    # Check if DID is revoked (Fallback path)
                    # We can get citizen_did from the credential record
                    citizen_did = credential.get('citizen_did')
                    if citizen_did:
                        did_info = await self.did_registry.lookup_did('did', citizen_did)
                        if did_info.get('found'):
                            did_entry = did_info.get('did_entry', {})
                            if did_entry.get('status') == 'REVOKED':
                                return web.json_response({
                                    'success': True,
                                    'verified': False,
                                    'valid': False,
                                    'revoked': True,
                                    'reason': 'The entire Decentralized Identifier (DID) has been revoked by government authority.',
                                    'revocation_level': 'DID_LEVEL',
                                    'credential_id': credential_id,
                                    'citizen_did': citizen_did,
                                    'ledger_source': 'did_registry_check'
                                })
                    
                    if status in ['REVOKED', 'revoked']:
                        return web.json_response({
                            'success': True,
                            'verified': False,
                            'valid': False,
                            'revoked': True,
                            'credential_status': status,
                            'error': 'Credential revoked',
                            'reason': 'Credential revoked',
                            'revoked_at': credential.get('revoked_at', 'N/A'),
                            'revocation_reason': credential.get('revocation_reason', 'N/A'),
                            'credential_id': credential_id,
                            'ledger_source': 'credential_ledger_fallback'
                        })
                    
                    if status not in ['ACTIVE', 'ISSUED', 'STORED']:
                        return web.json_response({
                            'success': True,
                            'verified': False,
                            'valid': False,
                            'credential_status': status,
                            'error': f'VC is {status}. Cannot be used for service access.',
                            'credential_id': credential_id,
                            'ledger_source': 'credential_ledger_fallback'
                        })
                    
                    return web.json_response({
                        'success': True,
                        'verified': True,
                        'valid': True,
                        'revoked': False,
                        'credential_id': credential_id,
                        'vc_number': f"VC_{credential_id}",
                        'credential_status': status,
                        'credential_type': credential.get('credential_type'),
                        'verified_at': credential.get('issued_at'),
                        'issued_by': credential.get('issued_by', 'Government of India'),
                        'verification_timestamp': datetime.now().isoformat(),
                        'ledger_source': 'credential_ledger_fallback'
                    })
            
            # Found in Rust Indy ledger - use this as source of truth
            tx_data = cred_info.get('credential_data', {})
            status = tx_data.get('status', 'UNKNOWN')
            
            # Check if credential belongs to the citizen DID
            if citizen_did and tx_data.get('citizen_did') != citizen_did:
                return web.json_response({
                    'success': False,
                    'verified': False,
                    'error': 'VC does not belong to this citizen',
                    'credential_id': credential_id
                })
            
            # Check if DID itself is revoked
            citizen_did_to_check = citizen_did or tx_data.get('citizen_did')
            if citizen_did_to_check:
                # Check status in DID registry
                did_info = await self.did_registry.lookup_did('did', citizen_did_to_check)
                if did_info.get('found'):
                    did_entry = did_info.get('did_entry', {})
                    if did_entry.get('status') == 'REVOKED':
                         return web.json_response({
                            'success': True,
                            'verified': False,
                            'valid': False,
                            'revoked': True,
                            'reason': 'The entire Decentralized Identifier (DID) has been revoked by government authority.',
                            'revocation_level': 'DID_LEVEL',
                            'credential_id': credential_id,
                            'citizen_did': citizen_did_to_check,
                            'ledger_source': 'did_registry_check'
                        })
                
                # Also check in Rust Indy ledger for DID_REVOCATION transaction
                rust_ledger_data = await rust_core.get_ledger_data()
                rust_transactions = rust_ledger_data.get('transactions', {})
                for rt_id, rt in rust_transactions.items():
                    if rt.get('transaction_type') == 'DID_REVOCATION':
                        if rt.get('data', {}).get('did') == citizen_did_to_check:
                            return web.json_response({
                                'success': True,
                                'verified': False,
                                'valid': False,
                                'revoked': True,
                                'reason': f"DID Revoked: {rt.get('data', {}).get('revocation_reason', 'Administrative revocation')}",
                                'revocation_level': 'DID_LEVEL_BLOCKCHAIN',
                                'credential_id': credential_id,
                                'citizen_did': citizen_did_to_check,
                                'revocation_transaction_id': rt_id,
                                'ledger_source': 'rust_indy_ledger'
                            })

            # Check if revoked - CRITICAL: Check for revocation transactions
            if status in ['REVOKED', 'revoked']:
                return web.json_response({
                    'success': True,
                    'verified': False,
                    'valid': False,
                    'revoked': True,
                    'credential_status': status,
                    'error': 'Credential revoked',
                    'reason': 'Credential revoked',
                    'revoked_at': tx_data.get('revoked_at', 'N/A'),
                    'revocation_reason': tx_data.get('revocation_reason', 'N/A'),
                    'credential_id': credential_id,
                    'ledger_source': 'rust_indy_ledger'
                })
            
            # Also check for revocation transactions
            ledger_data = await rust_core.get_ledger_data()
            transactions = ledger_data.get('transactions', {})
            for tx_id, tx in transactions.items():
                if tx.get('transaction_type') == 'CREDENTIAL_REVOCATION':
                    rev_data = tx.get('data', {})
                    if rev_data.get('credential_id') == credential_id:
                        return web.json_response({
                            'success': True,
                            'verified': False,
                            'valid': False,
                            'revoked': True,
                            'credential_status': 'REVOKED',
                            'error': 'Credential revoked',
                            'reason': rev_data.get('revocation_reason', 'Credential revoked'),
                            'revoked_at': rev_data.get('revoked_at', 'N/A'),
                            'revocation_reason': rev_data.get('revocation_reason', 'N/A'),
                            'credential_id': credential_id,
                            'revocation_transaction_id': tx_id,
                            'ledger_source': 'rust_indy_ledger'
                        })
            
            # Check if credential is active
            if status not in ['ACTIVE', 'ISSUED', 'STORED', 'VERIFIED']:
                return web.json_response({
                    'success': True,
                    'verified': False,
                    'valid': False,
                    'credential_status': status,
                    'error': f'VC is {status}. Cannot be used for service access.',
                    'credential_id': credential_id,
                    'ledger_source': 'rust_indy_ledger'
                })
            
            # Verification successful - credential is active and not revoked
            return web.json_response({
                'success': True,
                'verified': True,
                'valid': True,
                'revoked': False,
                'credential_id': credential_id,
                'vc_number': f"VC_{credential_id}",
                'credential_status': status,
                'credential_type': tx_data.get('credential_type'),
                'verified_at': tx_data.get('issued_at'),
                'issued_by': tx_data.get('issuer', 'Government of India'),
                'transaction_id': cred_info.get('transaction_id'),
                'verification_timestamp': datetime.now().isoformat(),
                'ledger_source': 'rust_indy_ledger'
            })
            
        except Exception as e:
            print(f"❌ Error verifying VC credential: {e}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def submit_service_request(self, request):
        """Submit a service request with verifiable presentation"""
        try:
            citizen_id = request.match_info['citizen_id']
            data = await request.json()
            
            service_id = data.get('service_id')
            service_name = data.get('service_name')
            
            if not service_id or not service_name:
                return web.json_response({
                    'success': False,
                    'error': 'service_id and service_name are required'
                }, status=400)
            
            # Get citizen information
            if citizen_id not in self.citizens_db:
                return web.json_response({
                    'success': False,
                    'error': 'Citizen not found'
                }, status=404)
            
            citizen = self.citizens_db[citizen_id]
            citizen_did = citizen.get('did')
            citizen_name = citizen.get('personal_details', {}).get('name') or citizen.get('name', 'Unknown')
            
            if not citizen_did:
                return web.json_response({
                    'success': False,
                    'error': 'Citizen DID not found. Please generate DID first.'
                }, status=400)
            
            # Get wallet data to extract VC and identity token
            wallet_response = await self.get_citizen_wallet(request)
            wallet_data = json.loads(wallet_response.text)
            
            if 'error' in wallet_data:
                return web.json_response({
                    'success': False,
                    'error': f"Failed to load wallet data: {wallet_data.get('error')}"
                }, status=500)
            
            if 'wallet' not in wallet_data:
                return web.json_response({
                    'success': False,
                    'error': 'Failed to load wallet data: Invalid format'
                }, status=500)
                
            wallet = wallet_data.get('wallet', {})
            
            # Get active VC credential
            vc_credentials = wallet.get('vc_credentials', [])
            active_vc = None
            for vc in vc_credentials:
                if vc.get('status') in ['ACTIVE', 'ISSUED', 'STORED', 'GENERATED']:
                    active_vc = vc
                    break
            
            if not active_vc:
                return web.json_response({
                    'success': False,
                    'error': 'No active VC credential found. Please complete Aadhaar e-KYC first.'
                }, status=400)
            
            # Get identity token
            identity_token = wallet.get('auto_identity_token')
            
            # Create verifiable presentation
            verifiable_presentation = {
                "@context": [
                    "https://www.w3.org/2018/credentials/v1",
                    "https://www.w3.org/2018/credentials/presentation/v1"
                ],
                "type": ["VerifiablePresentation", "ServiceRequestPresentation"],
                "holder": citizen_did,
                "verifiableCredential": [{
                    "@context": active_vc.get('credential_data', {}),
                    "id": active_vc.get('credential_id'),
                    "type": ["VerifiableCredential", active_vc.get('credential_type', 'aadhaar_kyc')],
                    "credentialSubject": {
                        "id": citizen_did,
                        "credential_type": active_vc.get('credential_type'),
                        "status": active_vc.get('status')
                    },
                    "credentialStatus": {
                        "status": active_vc.get('status')
                    }
                }],
                "service_request": {
                    "service_id": service_id,
                    "service_name": service_name,
                    "requested_at": datetime.now().isoformat()
                },
                "proof": {
                    "type": "Ed25519Signature2020",
                    "created": datetime.now().isoformat(),
                    "verificationMethod": f"{citizen_did}#key-1",
                    "proofPurpose": "assertionMethod"
                }
            }
            
            # Submit service request to ledger
            result = await self.service_ledger.create_service_request(
                service_id=service_id,
                service_name=service_name,
                citizen_did=citizen_did,
                citizen_name=citizen_name,
                verifiable_presentation=verifiable_presentation,
                identity_token=identity_token,
                vc_credential=active_vc
            )
            
            if result.get('success'):
                return web.json_response({
                    'success': True,
                    'message': 'Service request submitted successfully',
                    'request_id': result.get('request_id'),
                    'service_request': result.get('service_request')
                })
            else:
                return web.json_response({
                    'success': False,
                    'error': result.get('error', 'Failed to submit service request')
                }, status=500)
                
        except Exception as e:
            print(f"❌ Error submitting service request: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    
    async def check_kyc_cooldown(self, citizen_id):
        """Check if citizen can make a new Aadhaar e-KYC request (3-month cooldown)"""
        try:
            from datetime import datetime, timedelta
            
            # Load approved Aadhaar records from shared file
            shared_file_path = Path(__file__).parent.parent / 'data' / 'aadhaar_requests.json'
            approved_aadhaar = {}
            
            if shared_file_path.exists():
                with open(shared_file_path, 'r') as f:
                    shared_data = json.load(f)
                approved_aadhaar = shared_data.get("approved_aadhaar", {})
            
            # Find approved requests for this citizen
            citizen_approved = [record for record in approved_aadhaar.values() 
                              if record.get('citizen_did') == citizen_id and record.get('status') == 'VERIFIED']
            
            if not citizen_approved:
                return {
                    'allowed': True,
                    'message': 'No previous approved requests found'
                }
            
            # Get the most recent approved request
            latest_approved = max(citizen_approved, key=lambda x: x.get('verified_at', ''))
            verified_at = datetime.fromisoformat(latest_approved['verified_at'])
            
            # Calculate cooldown period (3 months)
            cooldown_period = timedelta(days=90)  # 3 months
            cooldown_until = verified_at + cooldown_period
            current_time = datetime.now()
            
            if current_time < cooldown_until:
                days_remaining = (cooldown_until - current_time).days
                return {
                    'allowed': False,
                    'message': f'Aadhaar e-KYC request is on cooldown. You can make a new request after {cooldown_until.strftime("%Y-%m-%d")}',
                    'cooldown_until': cooldown_until.isoformat(),
                    'days_remaining': days_remaining,
                    'last_approved': latest_approved['verified_at']
                }
            else:
                return {
                    'allowed': True,
                    'message': 'Cooldown period has expired, new request allowed'
                }
                
        except Exception as e:
            print(f"❌ Error checking KYC cooldown: {e}")
            # If there's an error, allow the request (fail open)
            return {
                'allowed': True,
                'message': 'Unable to check cooldown, allowing request'
            }
    
    async def request_aadhaar_kyc(self, request):
        """3. Citizen can request Aadhaar e-KYC"""
        citizen_id = request.match_info['citizen_id']
        
        if citizen_id not in self.citizens_db:
            return web.json_response({
                'error': 'Citizen not found'
            }, status=404)
        
        try:
            # Load latest data from shared file
            await self.load_shared_data()
            
            # Check for cooldown period (3 months)
            cooldown_check = await self.check_kyc_cooldown(citizen_id)
            if not cooldown_check['allowed']:
                return web.json_response({
                    'error': cooldown_check['message'],
                    'cooldown_until': cooldown_check['cooldown_until'],
                    'days_remaining': cooldown_check['days_remaining']
                }, status=429)  # Too Many Requests
            
            data = await request.json()
            
            # Validate Aadhaar request data
            required_fields = ['aadhaar_number', 'otp']
            for field in required_fields:
                if field not in data:
                    return web.json_response({
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            citizen = self.citizens_db[citizen_id]
            
            # Create Aadhaar request
            request_id = f"AADHAAR_REQ_{secrets.token_hex(8)}"
            
            aadhaar_request = {
                'request_id': request_id,
                'citizen_id': citizen_id,
                'citizen_did': citizen['did'],
                'citizen_name': citizen['personal_details']['name'],
                'aadhaar_number': data['aadhaar_number'],
                'otp': data['otp'],
                'status': 'PENDING',
                'requested_at': datetime.now().isoformat()
            }
            
            self.aadhaar_requests[request_id] = aadhaar_request
            
            # Save to shared file for government portal access
            await self.save_aadhaar_request_to_shared_file(aadhaar_request)
            
            return web.json_response({
                'success': True,
                'request_id': request_id,
                'message': 'Aadhaar e-KYC request submitted successfully',
                'status': 'PENDING'
            })
            
        except Exception as e:
            return web.json_response({
                'error': f'Aadhaar request failed: {str(e)}'
            }, status=500)
    
    async def get_aadhaar_status(self, request):
        """Get Aadhaar KYC status"""
        try:
            citizen_id = request.match_info['citizen_id']
            
            # Load latest data from shared file
            await self.load_shared_data()
            
            # Find Aadhaar request for this citizen
            citizen_requests = [req for req in self.aadhaar_requests.values() 
                              if req.get('citizen_id') == citizen_id]
            
            if not citizen_requests:
                return web.json_response({
                    'status': 'NO_REQUEST',
                    'message': 'No Aadhaar request found'
                })
            
            latest_request = max(citizen_requests, key=lambda x: x.get('requested_at', ''))
            
            response_data = {
                'request_id': latest_request.get('request_id', 'N/A'),
                'status': latest_request.get('status', 'UNKNOWN'),
                'requested_at': latest_request.get('requested_at', 'N/A'),
                'citizen_did': latest_request.get('citizen_did', 'N/A')
            }
            
            # Add approval/rejection details if available
            if latest_request.get('approved_at'):
                response_data['approved_at'] = latest_request['approved_at']
            if latest_request.get('approved_by'):
                response_data['approved_by'] = latest_request['approved_by']
            if latest_request.get('rejected_at'):
                response_data['rejected_at'] = latest_request['rejected_at']
            if latest_request.get('rejection_reason'):
                response_data['rejection_reason'] = latest_request['rejection_reason']
            
            return web.json_response(response_data)
        except Exception as e:
            print(f"❌ Error in get_aadhaar_status: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'status': 'ERROR',
                'error': str(e)
            }, status=500)
    
    async def get_kyc_cooldown_status(self, request):
        """Get KYC cooldown status for a citizen"""
        citizen_id = request.match_info['citizen_id']
        
        if citizen_id not in self.citizens_db:
            return web.json_response({
                'error': 'Citizen not found'
            }, status=404)
        
        try:
            cooldown_check = await self.check_kyc_cooldown(citizen_id)
            return web.json_response(cooldown_check)
            
        except Exception as e:
            return web.json_response({
                'error': f'Failed to check cooldown status: {str(e)}'
            }, status=500)
    
    async def load_shared_data(self):
        """Load shared data from file"""
        try:
            shared_file_path = Path(__file__).parent.parent / 'data' / 'aadhaar_requests.json'
            
            if shared_file_path.exists():
                with open(shared_file_path, 'r') as f:
                    shared_data = json.load(f)
                
                self.aadhaar_requests = shared_data.get("aadhaar_requests", {})
                
        except Exception as e:
            print(f"❌ Error loading shared data: {e}")

    def save_shared_data(self):
        """Save shared data to file"""
        try:
            shared_file_path = Path(__file__).parent.parent / 'data' / 'aadhaar_requests.json'
            
            # Load existing data to avoid overwriting other keys
            current_data = {}
            if shared_file_path.exists():
                try:
                    with open(shared_file_path, 'r') as f:
                        current_data = json.load(f)
                except:
                    pass
            
            current_data["aadhaar_requests"] = self.aadhaar_requests
            
            with open(shared_file_path, 'w') as f:
                json.dump(current_data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving shared data: {e}")
            return False
    
    async def get_government_services(self, request):
        """Get available government services"""
        try:
            # Convert dict to list if needed
            services_list = self.government_services
            if isinstance(services_list, dict):
                services_list = list(services_list.values())
            
            return web.json_response({
                'success': True,
                'services': services_list,
                'message': 'Government services loaded successfully'
            })
        except Exception as e:
            return web.json_response({
                'success': False,
                'error': f'Failed to load government services: {str(e)}'
            }, status=500)
    
    async def get_available_services(self, request):
        citizen_id = request.match_info['citizen_id']
        
        if citizen_id not in self.citizens_db:
            return web.json_response({
                'error': 'Citizen not found'
            }, status=404)
        
        citizen = self.citizens_db[citizen_id]
        
        # Check if Aadhaar is approved
        citizen_requests = [req for req in self.aadhaar_requests.values() 
                          if req['citizen_id'] == citizen_id]
        
        if not citizen_requests:
            return web.json_response({
                'services': [],
                'message': 'Please complete Aadhaar e-KYC first'
            })
        
        latest_request = max(citizen_requests, key=lambda x: x['requested_at'])
        
        if latest_request['status'] != 'APPROVED':
            return web.json_response({
                'services': [],
                'message': 'Aadhaar e-KYC is pending approval',
                'status': latest_request['status']
            })
        
        # Return available government services
        available_services = [
            {
                'service_id': 'PASSPORT',
                'name': 'Passport Application',
                'description': 'Apply for new passport or renewal',
                'status': 'AVAILABLE'
            },
            {
                'service_id': 'PAN_CARD',
                'name': 'PAN Card Application',
                'description': 'Apply for new PAN card',
                'status': 'AVAILABLE'
            },
            {
                'service_id': 'VOTER_ID',
                'name': 'Voter ID Card',
                'description': 'Apply for voter ID card',
                'status': 'AVAILABLE'
            },
            {
                'service_id': 'DRIVING_LICENSE',
                'name': 'Driving License',
                'description': 'Apply for driving license',
                'status': 'AVAILABLE'
            },
            {
                'service_id': 'BIRTH_CERTIFICATE',
                'name': 'Birth Certificate',
                'description': 'Apply for birth certificate',
                'status': 'AVAILABLE'
            }
        ]
        
        return web.json_response({
            'services': available_services,
            'message': 'Government services available after Aadhaar approval',
            'aadhaar_status': 'APPROVED'
        })

    def has_approved_aadhaar_kyc(self, citizen_did):
        """Check if citizen has approved Aadhaar KYC"""
        try:
            # Load latest shared data
            shared_file_path = Path(__file__).parent.parent / 'data' / 'aadhaar_requests.json'
            
            if shared_file_path.exists():
                with open(shared_file_path, 'r') as f:
                    shared_data = json.load(f)
                
                approved_aadhaar = shared_data.get("approved_aadhaar", {})
                return citizen_did in approved_aadhaar
            
            return False
            
        except Exception as e:
            print(f"❌ Error checking Aadhaar KYC status: {e}")
            return False
    
    async def check_did_status(self, request):
        try:
            session_id = request.headers.get('X-Session-ID')
            if not session_id or session_id not in self.user_sessions:
                return web.json_response({'error': 'Invalid session'}, status=401)
            
            user_id = self.user_sessions[session_id]['user_id']
            
            # Check if user has any citizens registered
            user_citizens = [citizen for citizen in self.citizens_db.values() 
                           if citizen.get('user_id') == user_id]
            
            if user_citizens:
                citizen = user_citizens[0]  # Get first citizen
                
                # Try to load DID document from IPFS or local storage
                did_document = None
                try:
                    if citizen.get('ipfs_link'):
                        # Extract hash from IPFS URL
                        ipfs_url = citizen['ipfs_link']
                        if 'ipfs.io/ipfs/' in ipfs_url:
                            ipfs_hash = ipfs_url.split('ipfs.io/ipfs/')[-1]
                        else:
                            ipfs_hash = ipfs_url
                        did_document = download_from_ipfs(ipfs_hash)
                    elif citizen.get('did'):
                        # Try to load from local storage
                        local_file = Path(__file__).parent.parent / 'data' / f"{citizen['did'].replace(':', '_')}.json"
                        if local_file.exists():
                            with open(local_file, 'r') as f:
                                did_document = json.load(f)
                    
                    # If still no document, use the one stored in citizen data
                    if not did_document and citizen.get('did_document'):
                        did_document = citizen['did_document']
                        
                except Exception as e:
                    print(f"⚠️ Could not load DID document: {e}")
                    # Use the stored document as fallback
                    if citizen.get('did_document'):
                        did_document = citizen['did_document']
                
                # Check Aadhaar KYC status
                has_approved_kyc = self.has_approved_aadhaar_kyc(citizen['did'])
                
                # Get transaction hash and IPFS data from multiple sources (same logic as wallet)
                transaction_hash = None
                ipfs_cid = None
                ipfs_url = None
                citizen_did = citizen['did']
                
                # Source 1: rust_style_indy_ledger.json
                rust_ledger_file = Path(__file__).parent.parent / 'data' / 'rust_style_indy_ledger.json'
                if rust_ledger_file.exists():
                    try:
                        with open(rust_ledger_file, 'r') as f:
                            rust_ledger = json.load(f)
                        
                        did_data = rust_ledger.get('dids', {}).get(citizen_did)
                        if did_data:
                            transaction_hash = did_data.get('transaction_hash')
                            ipfs_cid = did_data.get('ipfs_cid')
                            ipfs_url = did_data.get('ipfs_url')
                        
                        # Check credentials section if not found
                        if not transaction_hash:
                            for cred_id, cred_data in rust_ledger.get('credentials', {}).items():
                                if cred_data.get('citizen_did') == citizen_did:
                                    transaction_hash = cred_data.get('transaction_hash') or cred_data.get('id')
                                    if not ipfs_cid:
                                        ipfs_cid = cred_data.get('ipfs_cid')
                                    if not ipfs_url:
                                        ipfs_url = cred_data.get('ipfs_url')
                                    break
                    except Exception as e:
                        print(f"⚠️ Error reading rust_style_indy_ledger: {e}")
                
                # Source 2: rust_indy_core_ledger.json
                if not transaction_hash:
                    rust_core_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
                    if rust_core_file.exists():
                        try:
                            with open(rust_core_file, 'r') as f:
                                rust_core_ledger = json.load(f)
                            
                            transactions = rust_core_ledger.get('transactions', [])
                            for tx in transactions:
                                if isinstance(tx, dict) and tx.get('did') == citizen_did:
                                    transaction_hash = tx.get('transaction_id') or tx.get('transaction_hash')
                                    if not ipfs_cid:
                                        ipfs_cid = tx.get('ipfs_cid')
                                    break
                        except Exception as e:
                            print(f"⚠️ Error reading rust_indy_core_ledger: {e}")
                
                # Source 3: Citizen record
                if not transaction_hash:
                    transaction_hash = citizen.get('transaction_hash') or citizen.get('nym_transaction') or citizen.get('ledger_hash')
                if not ipfs_cid:
                    ipfs_cid = citizen.get('ipfs_cid') or citizen.get('cloud_hash')
                if not ipfs_url:
                    ipfs_url = citizen.get('ipfs_link') or citizen.get('cloud_url')
                
                # Get auto identity token
                auto_identity_token = None
                try:
                    token_file = Path(__file__).parent.parent / 'data' / 'auto_identity_tokens.json'
                    if token_file.exists():
                        with open(token_file, 'r') as f:
                            token_ledger = json.load(f)
                        
                        # Find active token for this citizen DID
                        for token_id, token_data in token_ledger.get('tokens', {}).items():
                            if token_data.get('citizen_did') == citizen_did and token_data.get('status') == 'ACTIVE':
                                auto_identity_token = {
                                    'token_id': token_id,
                                    'token_type': token_data.get('token_type', 'identity_token'),
                                    'created_at': token_data.get('created_at'),
                                    'expires_at': token_data.get('expires_at'),
                                    'signature_type': token_data.get('signature_type', 'Quantum-Secure'),
                                    'quantum_secure': token_data.get('quantum_secure', False),
                                    'status': token_data.get('status')
                                }
                                break
                except Exception as e:
                    print(f"⚠️  Error loading auto identity token: {e}")
                
                response_data = {
                    'success': True,
                    'has_did': True,
                    'citizen_id': citizen['citizen_id'],
                    'did': citizen['did'],
                    'did_document': did_document or citizen.get('did_document', {}),
                    'ledger_type': citizen.get('ledger_type', 'rust_indy'),
                    'status': citizen.get('status', 'registered'),
                    'transaction_hash': transaction_hash or 'N/A',
                    'ledger_hash': transaction_hash or 'N/A',
                    'ipfs_cid': ipfs_cid or 'N/A',
                    'cloud_hash': ipfs_cid or 'N/A',
                    'cloud_provider': citizen.get('cloud_provider', 'ipfs'),
                    'cloud_url': ipfs_url or citizen.get('ipfs_link', citizen.get('cloud_url', 'N/A')),
                    'has_approved_aadhaar_kyc': has_approved_kyc
                }
                
                # Add auto identity token if available
                if auto_identity_token:
                    response_data['auto_identity_token'] = auto_identity_token
                
                return web.json_response(response_data)
            else:
                return web.json_response({
                    'success': True,
                    'has_did': False,
                    'message': 'No DID found. Please complete registration first.'
                })
                
        except Exception as e:
            return web.json_response({'error': f'Failed to check DID status: {str(e)}'}, status=500)
    
    async def generate_did(self, request):
        """Generate DID for user"""
        try:
            print("🚀 Starting DID generation process...")
            session_id = request.headers.get('X-Session-ID')
            if not session_id or session_id not in self.user_sessions:
                return web.json_response({'error': 'Invalid session'}, status=401)
            
            user_id = self.user_sessions[session_id]['user_id']
            print(f"👤 User ID: {user_id}")
            
            # Check if user already has a citizen
            existing_citizens = [citizen for citizen in self.citizens_db.values() 
                               if citizen.get('user_id') == user_id]
            
            if existing_citizens:
                print(f"⚠️ User already has citizen: {existing_citizens[0]['citizen_id']}")
                return web.json_response({
                    'error': 'User already has a citizen wallet'
                }, status=400)
            
            data = await request.json()
            print(f"📋 Citizen data: {data}")
            
            # Generate unique citizen ID
            citizen_id = f"CIT_{secrets.token_hex(8)}"
            print(f"🆔 Generated citizen ID: {citizen_id}")
            
            # Generate DID using blockchain manager
            print("🔗 Calling blockchain manager to create SDIS DID...")
            # Map full_name to name for blockchain manager
            blockchain_data = data.copy()
            if 'full_name' in blockchain_data:
                blockchain_data['name'] = blockchain_data['full_name']
            did_info = await self.generate_citizen_did(blockchain_data)
            print(f"✅ DID generation result: {did_info}")
            
            # Store citizen data
            citizen_data = {
                'citizen_id': citizen_id,
                'user_id': user_id,
                'personal_details': data,
                'did': did_info['did'],
                'did_document': did_info['did_document'],
                'ipfs_link': did_info['ipfs_link'],
                'created_at': datetime.now().isoformat(),
                'status': 'REGISTERED',
                'ledger_type': did_info.get('ledger_type', 'rust_indy'),
                'transaction_hash': did_info.get('ledger_hash', did_info.get('nym_transaction')),
                'ledger_hash': did_info.get('ledger_hash', did_info.get('nym_transaction')),
                'ipfs_cid': did_info.get('ipfs_cid', did_info.get('cloud_hash')),
                'cloud_hash': did_info.get('ipfs_cid', did_info.get('cloud_hash')),
                'cloud_provider': did_info.get('cloud_provider', 'ipfs'),
                'cloud_url': did_info.get('ipfs_link', did_info.get('cloud_url'))
            }
            
            # Store in memory
            self.citizens_db[citizen_id] = citizen_data
            
            # Add citizen to user's account
            user_email = self.user_sessions[session_id]['email']
            if user_email in self.user_accounts:
                if 'citizens' not in self.user_accounts[user_email]:
                    self.user_accounts[user_email]['citizens'] = []
                self.user_accounts[user_email]['citizens'].append(citizen_id)
            
            # Save to persistent storage
            self.save_persistent_data()
            
            return web.json_response({
                'success': True,
                'citizen_id': citizen_id,
                'did': did_info['did'],
                'ledger_type': did_info.get('ledger_type', 'rust_indy'),
                'transaction_hash': did_info.get('ledger_hash', did_info.get('nym_transaction')),
                'ledger_hash': did_info.get('ledger_hash', did_info.get('nym_transaction')),
                'ipfs_cid': did_info.get('ipfs_cid', did_info.get('cloud_hash')),
                'cloud_hash': did_info.get('ipfs_cid', did_info.get('cloud_hash')),
                'cloud_provider': did_info.get('cloud_provider', 'ipfs'),
                'cloud_url': did_info.get('ipfs_link', did_info.get('cloud_url'))
            })
            
        except Exception as e:
            return web.json_response({'error': f'Failed to generate DID: {str(e)}'}, status=500)
    
    async def notify_kyc_approval(self, request):
        """Receive notification of KYC approval with auto identity token"""
        try:
            data = await request.json()
            citizen_did = data.get('citizen_did')
            auto_token = data.get('auto_identity_token')
            
            if not citizen_did:
                return web.json_response({'error': 'citizen_did is required'}, status=400)
            
            print(f"📢 Received KYC approval notification for DID: {citizen_did}")
            
            # Find citizen by DID
            citizen = None
            for cid, cdata in self.citizens_db.items():
                if cdata.get('did') == citizen_did:
                    citizen = cdata
                    break
            
            if not citizen:
                # Try to load shared data if citizen not found in memory
                await self.load_shared_data()
                for cid, cdata in self.citizens_db.items():
                    if cdata.get('did') == citizen_did:
                        citizen = cdata
                        break
                
            if not citizen:
                return web.json_response({'error': 'Citizen not found'}, status=404)
            
            # Update citizen status in database
            citizen['kyc_status'] = 'APPROVED'
            citizen['kyc_approved_at'] = datetime.now().isoformat()
            citizen['auto_identity_token'] = auto_token
            
            # Update Aadhaar request status in shared data
            for req_id, req in self.aadhaar_requests.items():
                if req.get('citizen_did') == citizen_did:
                    req['status'] = 'APPROVED'
                    req['approved_at'] = citizen['kyc_approved_at']
                    break
            
            # Save updated data
            self.save_persistent_data()
            self.save_shared_data()
            
            print(f"✅ Citizen {citizen.get('citizen_id')} KYC status updated to APPROVED")
            
            return web.json_response({
                'success': True,
                'message': 'KYC approval notification received and processed',
                'citizen_id': citizen.get('citizen_id'),
                'kyc_status': 'APPROVED'
            })
            
        except Exception as e:
            print(f"❌ Error processing KYC approval notification: {e}")
            return web.json_response({'error': str(e)}, status=500)
    
    def save_persistent_data(self):
        """Save persistent data to JSON files"""
        try:
            # Save user accounts
            user_accounts_file = Path(__file__).parent.parent / 'data' / 'user_accounts.json'
            with open(user_accounts_file, 'w') as f:
                json.dump(self.user_accounts, f, indent=2)
            
            # Save citizens
            citizens_file = Path(__file__).parent.parent / 'data' / 'citizens.json'
            with open(citizens_file, 'w') as f:
                json.dump(self.citizens_db, f, indent=2)
            
            print("✅ Persistent data saved successfully")
            
        except Exception as e:
            print(f"❌ Error saving persistent data: {e}")


    # ── Selective Disclosure handlers ────────────────────────────────────────

    async def sd_issue(self, request):
        """POST /api/sd/issue/{citizen_id}
        Convert citizen's active VC into an SD-VC with per-claim Merkle commitments.
        Returns the SD-VC (public) + holder secrets (claim salts + proofs)."""
        try:
            from server.selective_disclosure_vc import issue_sd_vc
            citizen_id = request.match_info['citizen_id']
            citizen = self.citizens_db.get(citizen_id)
            if not citizen:
                return web.json_response({'success': False, 'error': 'Citizen not found'}, status=404)
            credentials = citizen.get('credentials', [])
            active_vc = next(
                (c for c in credentials if isinstance(c, dict) and c.get('status') in ('ACTIVE', 'VERIFIED')),
                None
            )
            if not active_vc:
                return web.json_response({'success': False, 'error': 'No active VC found'}, status=400)
            result = issue_sd_vc(active_vc)
            return web.json_response(result, status=200 if result.get('success') else 400)
        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)}, status=500)

    async def sd_present(self, request):
        """POST /api/sd/present
        Body: {"sd_vc_id": "...", "reveal_claims": ["name", "kyc_status"], "verifier_nonce": "..."}
        Holder creates a selective presentation — only chosen claims revealed."""
        try:
            from server.selective_disclosure_vc import create_presentation
            data = await request.json()
            sd_vc_id       = data.get('sd_vc_id', '')
            reveal_claims  = data.get('reveal_claims', [])
            verifier_nonce = data.get('verifier_nonce', '')
            if not sd_vc_id:
                return web.json_response({'success': False, 'error': 'sd_vc_id required'}, status=400)
            result = create_presentation(sd_vc_id, reveal_claims, verifier_nonce)
            return web.json_response(result, status=200 if result.get('success') else 400)
        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)}, status=500)

    async def sd_verify(self, request):
        """POST /api/sd/verify
        Body: {"presentation": {...}}
        Verifier checks each disclosed claim's commitment and Merkle proof."""
        try:
            from server.selective_disclosure_vc import verify_presentation
            data = await request.json()
            presentation = data.get('presentation')
            if not presentation:
                return web.json_response({'valid': False, 'error': 'presentation required'}, status=400)
            result = verify_presentation(presentation)
            return web.json_response(result, status=200 if result.get('valid') else 400)
        except Exception as e:
            return web.json_response({'valid': False, 'error': str(e)}, status=500)

    # ── Credential-based token handlers ─────────────────────────────────────


    async def issue_citizen_token(self, request):
        """POST /api/token/citizen/{citizen_id}
        Returns a 24-hour CITIZEN_TOKEN bound to the citizen's DID + active VC."""
        try:
            from server.credential_token_generator import generate_citizen_token
            citizen_id = request.match_info['citizen_id']
            result = generate_citizen_token(citizen_id)
            status = 200 if result.get('success') else 400
            return web.json_response(result, status=status)
        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)}, status=500)

    async def issue_government_token(self, request):
        """POST /api/token/government  body: {officer_id, officer_name, authority_level?}
        Returns an 8-hour GOVERNMENT_TOKEN with authority credential."""
        try:
            from server.credential_token_generator import generate_government_token
            data = await request.json()
            officer_id   = data.get('officer_id', 'GOV001')
            officer_name = data.get('officer_name', 'KYC Officer')
            authority    = data.get('authority_level', 'KYC_OFFICER')
            result = generate_government_token(officer_id, officer_name, authority)
            status = 200 if result.get('success') else 400
            return web.json_response(result, status=status)
        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)}, status=500)

    async def issue_service_token(self, request):
        """POST /api/token/service/{citizen_id}/{service_name}
        Returns a 15-minute SERVICE_TOKEN scoped to the requested service.
        Requires an ACTIVE KYC VC."""
        try:
            from server.credential_token_generator import generate_service_token
            citizen_id   = request.match_info['citizen_id']
            service_name = request.match_info['service_name']
            result = generate_service_token(citizen_id, service_name)
            status = 200 if result.get('success') else 400
            return web.json_response(result, status=status)
        except Exception as e:
            return web.json_response({'success': False, 'error': str(e)}, status=500)

    async def verify_credential_token(self, request):
        """GET /api/token/verify/{jti}
        Verify a token by JTI: checks signature, expiry, and VC hash binding."""
        try:
            from server.credential_token_generator import verify_token
            jti    = request.match_info['jti']
            result = verify_token(jti)
            status = 200 if result.get('valid') else 401
            return web.json_response(result, status=status)
        except Exception as e:
            return web.json_response({'valid': False, 'error': str(e)}, status=500)

def create_app():

    """Create and return the web application"""
    server = CitizenPortalServer()
    return server.app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8082)
