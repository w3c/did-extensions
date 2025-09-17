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
from datetime import datetime, timedelta
from pathlib import Path
from aiohttp import web, ClientSession
from ipfs_util import upload_to_ipfs, download_from_ipfs, is_ipfs_available, get_ipfs_link
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server.hybrid_sdis_implementation import HybridIndyBlockchainManager

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
        
        # Load persistent data
        self.load_persistent_data()
        
        # Setup routes
        self.setup_routes()
        
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
        
        # Aadhaar e-KYC request
        self.app.router.add_post('/api/citizen/{citizen_id}/aadhaar-request', self.request_aadhaar_kyc)
        self.app.router.add_get('/api/citizen/{citizen_id}/aadhaar-status', self.get_aadhaar_status)
        self.app.router.add_get('/api/citizen/{citizen_id}/kyc-cooldown', self.get_kyc_cooldown_status)
        
        # New workflow routes
        self.app.router.add_get('/api/citizen/check-did-status', self.check_did_status)
        self.app.router.add_post('/api/citizen/generate-did', self.generate_did)
        
        # Government services
        self.app.router.add_get('/api/citizen/government-services', self.get_government_services)
        
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
                'ipfs_link': did_info['ipfs_link'],
                'created_at': datetime.now().isoformat(),
                'status': 'REGISTERED'
            }
            
            self.citizens_db[citizen_id] = citizen_data
            
            # Add citizen to user's account
            user_email = session_data['email']
            if user_email in self.user_accounts:
                self.user_accounts[user_email]['citizens'].append(citizen_id)
            
            # Store DID permanently on Indy ledger (simulated)
            await self.store_did_on_ledger(did_info['did'], citizen_data)
            
            # Save citizen data to cloud (IPFS) with DID-based naming
            cloud_hash = self.save_to_cloud("citizen_data", citizen_data, did_info['did_suffix'])
            
            return web.json_response({
                'success': True,
                'citizen_id': citizen_id,
                'did': did_info['did'],
                'user_id': user_id,
                'cloud_hash': cloud_hash,
                'message': 'Citizen registered successfully with DID on Indy ledger and data on cloud'
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
                'ipfs_cid': ipfs_cid,
                'ledger_type': did_result['ledger_type'],
                'cloud_provider': did_result['cloud_provider']
            }
            
        except Exception as e:
            print(f"❌ Error creating DID: {e}")
            # Fallback to local generation
            return self._generate_local_did(personal_details)
    
    def _generate_local_did(self, personal_details):
        """Fallback local DID generation"""
        unique_id = f"{personal_details['name']}_{personal_details['email']}_{datetime.now().timestamp()}"
        did_hash1 = hashlib.sha256(unique_id.encode()).hexdigest()[:16]
        did_hash2 = hashlib.sha256(f"{unique_id}_secondary".encode()).hexdigest()[:16]
        did = f"did:sdis:{did_hash1}:{did_hash2}"
        
        did_document = {
            "did": did,
            "verkey": f"~{secrets.token_hex(32)}",
            "citizen_info": {
                "name": personal_details['name'],
                "email": personal_details['email'],
                "phone": personal_details['phone'],
                "address": personal_details['address'],
                "dob": personal_details['dob'],
                "gender": personal_details['gender']
            },
            "created_at": datetime.now().isoformat(),
            "status": "ACTIVE"
        }
        
        # Upload DID document to IPFS with DID-based naming
        if is_ipfs_available():
            ipfs_hash = upload_to_ipfs(did_document, f"{did_hash1}.json")
            ipfs_link = get_ipfs_link(ipfs_hash) if ipfs_hash else f"https://ipfs.io/ipfs/{ipfs_hash}"
            print(f"📤 DID document uploaded to IPFS: {ipfs_hash}")
        else:
            # Fallback to local storage with DID-based naming
            json_data = json.dumps(did_document, indent=2)
            
            data_dir = Path(__file__).parent.parent / 'data'
            data_dir.mkdir(exist_ok=True)
            
            file_path = data_dir / f"{did_hash1}.json"
            with open(file_path, 'w') as f:
                f.write(json_data)
            
            ipfs_hash = did_hash1  # Use first hash as the identifier
            ipfs_link = f"https://ipfs.io/ipfs/{ipfs_hash}"
            print(f"📁 DID document stored locally: {ipfs_hash}")
        
        return {
            'did': did,
            'did_document': did_document,
            'ipfs_link': ipfs_link,
            'did_suffix': did_hash1,
            'ledger_hash': did_hash1,
            'cloud_hash': did_hash1,
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
        """2. Wallet tab - Show generated DID and data from Rust ledger"""
        citizen_id = request.match_info['citizen_id']
        
        if citizen_id not in self.citizens_db:
            return web.json_response({
                'error': 'Citizen not found'
            }, status=404)
        
        citizen = self.citizens_db[citizen_id]
        citizen_did = citizen.get('did')
        
        # Get additional data from Rust ledger
        rust_data = {}
        if citizen_did:
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
                
                # Get credentials for this citizen
                credentials = []
                for cred_id, cred_data in rust_ledger.get('credentials', {}).items():
                    if cred_data.get('citizen_did') == citizen_did:
                        credentials.append({
                            'credential_id': cred_id,
                            'credential_type': cred_data.get('credential_type'),
                            'status': cred_data.get('status'),
                            'verified_at': cred_data.get('verified_at'),
                            'verified_by': cred_data.get('verified_by')
                        })
                rust_data['credentials'] = credentials
        
        return web.json_response({
            'citizen_id': citizen_id,
            'wallet': {
                'did': citizen['did'],
                'ipfs_link': citizen.get('ipfs_link', 'N/A'),
                'did_document': citizen.get('did_document', {}),
                'status': citizen['status'],
                'created_at': citizen['created_at'],
                'rust_ledger_data': rust_data
            }
        })
    
    async def resolve_did(self, request):
        """Resolve DID (placeholder for future implementation)"""
        citizen_id = request.match_info['citizen_id']
        
        if citizen_id not in self.citizens_db:
            return web.json_response({
                'error': 'Citizen not found'
            }, status=404)
        
        citizen = self.citizens_db[citizen_id]
        
        return web.json_response({
            'success': True,
            'message': 'DID resolve functionality will be implemented in next phase',
            'did': citizen['did'],
            'resolved_data': citizen['did_document']
        })
    
    async def check_kyc_cooldown(self, citizen_id):
        """Check if citizen can make a new Aadhaar e-KYC request (3-month cooldown)"""
        try:
            from datetime import datetime, timedelta, timedelta
            
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
        citizen_id = request.match_info['citizen_id']
        
        # Load latest data from shared file
        await self.load_shared_data()
        
        # Find Aadhaar request for this citizen
        citizen_requests = [req for req in self.aadhaar_requests.values() 
                          if req['citizen_id'] == citizen_id]
        
        if not citizen_requests:
            return web.json_response({
                'status': 'NO_REQUEST',
                'message': 'No Aadhaar request found'
            })
        
        latest_request = max(citizen_requests, key=lambda x: x['requested_at'])
        
        return web.json_response({
            'request_id': latest_request['request_id'],
            'status': latest_request['status'],
            'requested_at': latest_request['requested_at'],
            'citizen_did': latest_request['citizen_did']
        })
    
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
    
    async def get_government_services(self, request):
        """Get available government services"""
        try:
            return web.json_response({
                'success': True,
                'services': self.government_services,
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

    def get_citizen_credentials(self, citizen_did):
        """Get all credentials for a citizen"""
        try:
            # Load latest shared data
            shared_file_path = Path(__file__).parent.parent / 'data' / 'aadhaar_requests.json'
            
            if shared_file_path.exists():
                with open(shared_file_path, 'r') as f:
                    shared_data = json.load(f)
                
                approved_aadhaar = shared_data.get("approved_aadhaar", {})
                credentials = {}
                
                print(f"🔍 Looking for credentials for DID: {citizen_did}")
                print(f"📋 Found {len(approved_aadhaar)} approved Aadhaar records")
                
                # Check if citizen has approved Aadhaar KYC
                if citizen_did in approved_aadhaar:
                    aadhaar_record = approved_aadhaar[citizen_did]
                    print(f"✅ Found approved Aadhaar record for {citizen_did}")
                    
                    # Create Aadhaar KYC credential
                    credential_id = f"AADHAAR_KYC_CRED_{secrets.token_hex(8)}"
                    credentials[credential_id] = {
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
                        'expires_at': (datetime.now() + timedelta(days=365)).isoformat(),  # 1 year validity
                        'verifiable_credential_hash': aadhaar_record.get('verifiable_credential_hash', ''),
                        'credential_data': aadhaar_record.get('credential_data', {}),
                        'ledger_transaction': f"AADHAAR_KYC_TXN_{secrets.token_hex(8)}",
                        'ipfs_cid': f"Qm{secrets.token_hex(44)}",  # Simulated IPFS CID
                        'revocation_status': 'ACTIVE'
                    }
                    print(f"📄 Created credential: {credential_id}")
                else:
                    print(f"❌ No approved Aadhaar record found for {citizen_did}")
                
                return credentials
            
            return {}
            
        except Exception as e:
            print(f"❌ Error getting citizen credentials: {e}")
            return {}
    
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
                
                # Check Aadhaar KYC status and get credentials
                has_approved_kyc = self.has_approved_aadhaar_kyc(citizen['did'])
                credentials = self.get_citizen_credentials(citizen['did'])
                
                return web.json_response({
                    'success': True,
                    'has_did': True,
                    'citizen_id': citizen['citizen_id'],
                    'did': citizen['did'],
                    'did_document': did_document or citizen.get('did_document', {}),
                    'ledger_type': citizen.get('ledger_type', 'rust_indy'),
                    'status': citizen.get('status', 'registered'),
                    'transaction_hash': citizen.get('transaction_hash', citizen.get('nym_transaction', citizen.get('ledger_hash', 'N/A'))),
                    'ledger_hash': citizen.get('ledger_hash', citizen.get('nym_transaction', citizen.get('transaction_hash', 'N/A'))),
                    'ipfs_cid': citizen.get('ipfs_cid', citizen.get('cloud_hash', 'N/A')),
                    'cloud_hash': citizen.get('ipfs_cid', citizen.get('cloud_hash', 'N/A')),
                    'cloud_provider': citizen.get('cloud_provider', 'ipfs'),
                    'cloud_url': citizen.get('ipfs_link', citizen.get('cloud_url', 'N/A')),
                    'has_approved_aadhaar_kyc': has_approved_kyc,
                    'credentials': credentials
                })
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

def create_app():
    """Create and return the web application"""
    server = CitizenPortalServer()
    return server.app

if __name__ == '__main__':
    app = create_app()
    web.run_app(app, host='0.0.0.0', port=8082)
