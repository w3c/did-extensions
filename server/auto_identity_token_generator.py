#!/usr/bin/env python3
"""
Auto Identity Token Generation System
Comprehensive system for generating auto identity tokens with DID retrieval, resolution, and VC integration
"""

import asyncio
import json
import hashlib
import secrets
import jwt
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import uuid

# Import existing systems
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rust_indy_core import IndyRustCore
from server.pqie_framework import PQIECryptoEngine, PQIETokenGenerator

# Try to import quantum secure signatures, but allow graceful failure
try:
    from quantum_secure_signature_system import QuantumSecureTokenIntegration
except ImportError:
    # Create a dummy class if not available
    class QuantumSecureTokenIntegration:
        async def generate_quantum_secure_token(self, citizen_did, token_data):
            return {"success": False, "error": "Quantum signatures not available"}

class AutoIdentityTokenGenerator:
    """Auto Identity Token Generation System"""
    
    def __init__(self):
        self.rust_core = None
        self.quantum_secure_integration = QuantumSecureTokenIntegration()
        self.token_config = {
            "issuer": "aadhaar-kyc-system",
            "audience": "government-services",
            "algorithm": "HS256",
            "secret_key": "auto_identity_token_secret_key_2024",
            "token_expiry_hours": 24,
            "refresh_token_expiry_days": 30
        }
        
        # Initialize PQIE Framework
        self.pqie_crypto = PQIECryptoEngine()
        self.pqie_token_gen = PQIETokenGenerator(self.pqie_crypto)
        
        # Token types
        self.token_types = {
            "access_token": {
                "name": "Access Token",
                "expiry_hours": 1,
                "scope": ["read", "write", "verify"]
            },
            "identity_token": {
                "name": "Identity Token",
                "expiry_hours": 24,
                "scope": ["identity", "kyc", "services"]
            },
            "service_token": {
                "name": "Service Token",
                "expiry_hours": 8,
                "scope": ["government_services", "verification"]
            },
            "refresh_token": {
                "name": "Refresh Token",
                "expiry_days": 30,
                "scope": ["refresh"]
            }
        }
        
        # Misuse protection settings
        self.misuse_protection = {
            "rate_limiting": {
                "max_tokens_per_hour": 10,
                "max_tokens_per_day": 50,
                "max_failed_attempts": 5,
                "cooldown_minutes": 30
            },
            "fraud_detection": {
                "enabled": True,
                "suspicious_pattern_threshold": 3,
                "geo_velocity_check": True,
                "device_fingerprinting": True
            },
            "anomaly_detection": {
                "unusual_ip": True,
                "rapid_generation": True,
                "multiple_devices": True
            }
        }
        
        # Track misuse attempts
        self.misuse_tracking = {}
        
        # Initialize ledger files
        self._initialize_token_ledger()
        
    def _initialize_token_ledger(self):
        """Initialize token ledger file"""
        try:
            data_dir = Path(__file__).parent.parent / 'data'
            data_dir.mkdir(exist_ok=True)
            
            token_ledger_file = data_dir / 'auto_identity_tokens.json'
            if not token_ledger_file.exists():
                with open(token_ledger_file, 'w') as f:
                    json.dump({
                        "ledger_id": "auto_identity_token_ledger_v1",
                        "created_at": datetime.now().isoformat(),
                        "total_tokens": 0,
                        "active_tokens": 0,
                        "expired_tokens": 0,
                        "revoked_tokens": 0,
                        "tokens": {},
                        "token_indexes": {
                            "by_citizen_did": {},
                            "by_token_type": {},
                            "by_status": {},
                            "by_issued_date": {}
                        }
                    }, f, indent=2)
            
            print("✅ Auto Identity Token ledger initialized!")
            
        except Exception as e:
            print(f"❌ Failed to initialize token ledger: {e}")
    
    async def initialize(self):
        """Initialize the Auto Identity Token Generator"""
        try:
            print("🚀 Initializing Auto Identity Token Generator...")
            
            # Initialize Rust core
            ledger_file = str(Path(__file__).parent.parent / 'data' / 'rust_auto_identity_ledger.json')
            self.rust_core = IndyRustCore(ledger_file)
            
            print("✅ Auto Identity Token Generator initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Auto Identity Token Generator: {e}")
            return False
    
    async def generate_auto_identity_token(self, citizen_did: str, token_type: str = "identity_token", 
                                         additional_claims: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate auto identity token with DID retrieval and PQIE protection"""
        try:
            print(f"🎫 Generating {token_type} for DID: {citizen_did} using PQIE Protection")
            
            # Step 1: DID Retrieval
            did_data = await self._retrieve_did_data(citizen_did)
            if not did_data["success"]:
                return {"success": False, "error": f"DID retrieval failed: {did_data['error']}"}
            
            # Step 2: Use PQIE Token Generator for Lattice-based protection
            citizen_personal_data = did_data.get("citizen_data", {})
            if not citizen_personal_data and "personal_details" in did_data:
                 citizen_personal_data = did_data["personal_details"]
                 
            # Prepare attributes for PQIE lifting
            pqie_attributes = {
                "did": citizen_did,
                "name": citizen_personal_data.get("name", "Unknown"),
                "email": citizen_personal_data.get("email", ""),
                "token_type": token_type,
                "nonce": secrets.token_hex(8)
            }
            
            # Generate PQIE Identity Token (Lattice-based)
            pqie_token_package = self.pqie_token_gen.generate_identity_token(pqie_attributes, user_identifier=citizen_did)
            
            # Step 3: DID Resolution (Optional/Logged)
            resolution_data = await self._resolve_did(citizen_did)
            
            # Step 4: VC Integration
            vc_data = await self._get_vc_credentials(citizen_did)
            
            # Step 5: Merge PQIE token with standard JWT for compatibility
            token_result = await self._create_identity_token(
                citizen_did, token_type, did_data, resolution_data, vc_data, 
                {**(additional_claims or {}), "pqie_token_id": pqie_token_package["token_id"]}
            )
            
            if token_result["success"]:
                # Record successful generation for misuse protection
                self._record_successful_generation(citizen_did)
                
                print(f"✅ Auto identity token generated with PQIE protection: {token_result['token_id']}")
                
                return {
                    "success": True,
                    "token_id": token_result["token_id"],
                    "token": token_result["token"],
                    "pqie_package": pqie_token_package,
                    "token_type": token_type,
                    "expires_at": token_result["expires_at"],
                    "did_data": did_data,
                    "resolution_data": resolution_data,
                    "vc_data": vc_data,
                    "ledger_result": await self._store_token_in_ledger(token_result),
                    "rust_result": await self._write_token_to_rust_ledger(token_result)
                }
            else:
                return {"success": False, "error": token_result["error"]}
                
        except Exception as e:
            print(f"❌ Failed to generate auto identity token: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def _generate_quantum_secure_token(self, citizen_did: str, token_result: Dict[str, Any], additional_claims: Dict[str, Any]) -> Dict[str, Any]:
        """Generate quantum-secure token"""
        try:
            print(f"🔐 Generating quantum-secure token for DID: {citizen_did}")
            
            # Prepare token data for quantum signing
            token_data = {
                "token_id": token_result["token_id"],
                "token_type": token_result["token_type"],
                "expires_at": token_result["expires_at"],
                "claims": additional_claims or {},
                "did_verified": True,
                "vc_verified": True
            }
            
            # Generate quantum-secure token
            quantum_result = await self.quantum_secure_integration.generate_quantum_secure_token(
                citizen_did, token_data
            )
            
            if quantum_result["success"]:
                print(f"✅ Quantum-secure token generated: {quantum_result['quantum_token']['token_id']}")
                return quantum_result
            else:
                print(f"⚠️ Quantum-secure token generation failed: {quantum_result.get('error', 'Unknown error')}")
                return {"success": False, "error": quantum_result.get('error', 'Quantum token generation failed')}
                
        except Exception as e:
            print(f"❌ Error generating quantum-secure token: {e}")
            return {"success": False, "error": str(e)}
    
    async def _retrieve_did_data(self, citizen_did: str) -> Dict[str, Any]:
        """Retrieve DID data from registry and ledger"""
        try:
            print(f"🔍 Retrieving DID data: {citizen_did}")
            
            # Load DID registry
            registry_file = Path(__file__).parent.parent / 'data' / 'did_registry.json'
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    registry = json.load(f)
                
                if citizen_did in registry.get("dids", {}):
                    did_entry = registry["dids"][citizen_did]
                    
                    return {
                        "success": True,
                        "did": citizen_did,
                        "did_document": did_entry.get("did_document", {}),
                        "citizen_data": did_entry.get("citizen_data", {}),
                        "status": did_entry.get("status", "UNKNOWN"),
                        "registered_at": did_entry.get("registered_at"),
                        "blockchain_info": did_entry.get("blockchain_info", {})
                    }
            
            # Fallback: Check citizens database
            citizens_file = Path(__file__).parent.parent / 'data' / 'citizens.json'
            if citizens_file.exists():
                with open(citizens_file, 'r') as f:
                    citizens = json.load(f)
                
                for citizen_id, citizen_data in citizens.items():
                    if citizen_data.get("did") == citizen_did:
                        return {
                            "success": True,
                            "did": citizen_did,
                            "citizen_data": citizen_data,
                            "status": "ACTIVE",
                            "source": "citizens_database"
                        }
            
            return {"success": False, "error": "DID not found in registry or database"}
            
        except Exception as e:
            print(f"❌ Failed to retrieve DID data: {e}")
            return {"success": False, "error": str(e)}
    
    async def _resolve_did(self, citizen_did: str) -> Dict[str, Any]:
        """Resolve DID using SDIS Public Resolver"""
        try:
            print(f"🔍 Resolving DID: {citizen_did}")
            
            # Try to resolve using SDIS Public Resolver
            import aiohttp
            async with aiohttp.ClientSession() as session:
                try:
                    resolver_url = f"http://localhost:8085/1.0/identifiers/{citizen_did}"
                    async with session.get(resolver_url, timeout=5) as response:
                        if response.status == 200:
                            resolution_data = await response.json()
                            
                            return {
                                "success": True,
                                "did": citizen_did,
                                "did_document": resolution_data.get("didDocument", {}),
                                "resolution_metadata": resolution_data.get("resolutionMetadata", {}),
                                "document_metadata": resolution_data.get("documentMetadata", {}),
                                "status": resolution_data.get("status", "SUCCESS"),
                                "resolved_at": datetime.now().isoformat()
                            }
                        else:
                            return {"success": False, "error": f"Resolver returned status {response.status}"}
                            
                except Exception as e:
                    print(f"⚠️ SDIS Resolver not available: {e}")
                    # Fallback to local resolution
                    return await self._local_did_resolution(citizen_did)
            
        except Exception as e:
            print(f"❌ Failed to resolve DID: {e}")
            return {"success": False, "error": str(e)}
    
    async def _local_did_resolution(self, citizen_did: str) -> Dict[str, Any]:
        """Local DID resolution fallback"""
        try:
            print(f"🔍 Local DID resolution: {citizen_did}")
            
            # First try DID registry
            registry_file = Path(__file__).parent.parent / 'data' / 'did_registry.json'
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    registry = json.load(f)
                
                if citizen_did in registry.get("dids", {}):
                    did_entry = registry["dids"][citizen_did]
                    return {
                        "success": True,
                        "did": citizen_did,
                        "did_document": did_entry.get("did_document", {}),
                        "resolution_metadata": {
                            "resolver": "local_did_registry",
                            "resolved_at": datetime.now().isoformat()
                        },
                        "status": "SUCCESS"
                    }
            
            # Check Rust Indy ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    ledger = json.load(f)
                
                for did_entry in ledger.get("dids", {}).values():
                    if did_entry.get("did") == citizen_did:
                        return {
                            "success": True,
                            "did": citizen_did,
                            "did_document": {
                                "@context": "https://www.w3.org/ns/did/v1",
                                "id": citizen_did,
                                "verificationMethod": did_entry.get("verification_methods", []),
                                "service": did_entry.get("services", [])
                            },
                            "resolution_metadata": {
                                "resolver": "local_rust_ledger",
                                "resolved_at": datetime.now().isoformat()
                            },
                            "status": "SUCCESS"
                        }
            
            return {"success": False, "error": "DID not found in local ledgers or registry"}
            
        except Exception as e:
            print(f"❌ Local DID resolution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_vc_credentials(self, citizen_did: str) -> Dict[str, Any]:
        """Get VC credentials from credential ledger"""
        try:
            print(f"🔐 Retrieving VC credentials for: {citizen_did}")
            
            # Load credential ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'credential_ledger.json'
            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    ledger = json.load(f)
                
                # Use indexes for faster lookup
                indexes = ledger.get("indexes", {})
                did_index = indexes.get("by_citizen_did", {})
                
                if citizen_did not in did_index:
                    print(f"⚠️  No credentials found for DID: {citizen_did}")
                    return {
                        "success": True,  # Still success, just no credentials
                        "citizen_did": citizen_did,
                        "credentials": [],
                        "total_credentials": 0,
                        "retrieved_at": datetime.now().isoformat()
                    }
                
                # Get credential IDs from index
                credential_ids = did_index[citizen_did]
                credentials_data = ledger.get("credentials", {})
                
                # Build credential list
                citizen_credentials = []
                for credential_id in credential_ids:
                    if credential_id in credentials_data:
                        credential_entry = credentials_data[credential_id]
                        
                        # Handle both credential and credential_data keys
                        credential_obj = {}
                        if "credential" in credential_entry:
                            credential_obj = credential_entry["credential"]
                        elif "credential_data" in credential_entry:
                            credential_obj = credential_entry["credential_data"]
                        
                        citizen_credentials.append({
                            "credential_id": credential_id,
                            "credential": credential_obj,
                            "credential_type": credential_entry.get("credential_type"),
                            "status": credential_entry.get("status"),
                            "issued_at": credential_entry.get("issued_at"),
                            "expires_at": credential_entry.get("expires_at")
                        })
                
                print(f"✅ Retrieved {len(citizen_credentials)} VC credentials")
                
                return {
                    "success": True,
                    "citizen_did": citizen_did,
                    "credentials": citizen_credentials,
                    "total_credentials": len(citizen_credentials),
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": "Credential ledger not found"}
                
        except Exception as e:
            print(f"❌ Failed to retrieve VC credentials: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def _create_identity_token(self, citizen_did: str, token_type: str, 
                                   did_data: Dict[str, Any], resolution_data: Dict[str, Any],
                                   vc_data: Dict[str, Any], additional_claims: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create the actual identity token"""
        try:
            print(f"🎫 Creating {token_type}...")
            
            # Get token configuration
            token_config = self.token_types.get(token_type, self.token_types["identity_token"])
            
            # Calculate expiry
            if token_type == "refresh_token":
                expires_at = datetime.now() + timedelta(days=token_config["expiry_days"])
            else:
                expires_at = datetime.now() + timedelta(hours=token_config["expiry_hours"])
            
            # Create token ID
            token_id = f"auto_token_{token_type}_{secrets.token_hex(16)}"
            
            # Build token claims
            claims = {
                "jti": token_id,  # JWT ID
                "iss": self.token_config["issuer"],
                "aud": self.token_config["audience"],
                "sub": citizen_did,  # Subject (DID)
                "iat": datetime.now().timestamp(),  # Issued at
                "exp": expires_at.timestamp(),  # Expires at
                "token_type": token_type,
                "scope": token_config["scope"],
                
                # DID Information
                "did": citizen_did,
                "did_status": did_data.get("status", "UNKNOWN"),
                "did_registered_at": did_data.get("registered_at"),
                
                # Resolution Information
                "resolution_status": resolution_data.get("status", "UNKNOWN"),
                "resolution_source": resolution_data.get("resolution_metadata", {}).get("resolver", "unknown"),
                
                # VC Information
                "vc_credentials_count": vc_data.get("total_credentials", 0),
                "vc_credentials": [
                    {
                        "type": cred.get("credential_type"),
                        "status": cred.get("status"),
                        "issued_at": cred.get("issued_at")
                    } for cred in vc_data.get("credentials", [])
                ],
                
                # Additional claims
                **(additional_claims or {})
            }
            
            # Add citizen data if available
            if did_data.get("citizen_data"):
                citizen_data = did_data["citizen_data"]
                claims.update({
                    "name": citizen_data.get("name"),
                    "email": citizen_data.get("email"),
                    "phone": citizen_data.get("phone"),
                    "aadhaar_number": citizen_data.get("aadhaar_number")
                })
            
            # Generate JWT token
            token = jwt.encode(claims, self.token_config["secret_key"], algorithm=self.token_config["algorithm"])
            
            return {
                "success": True,
                "token_id": token_id,
                "token": token,
                "token_type": token_type,
                "claims": claims,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to create identity token: {e}")
            return {"success": False, "error": str(e)}
    
    async def _store_token_in_ledger(self, token_result: Dict[str, Any]) -> Dict[str, Any]:
        """Store token in auto identity token ledger"""
        try:
            print(f"📚 Storing token in ledger: {token_result['token_id']}")
            
            # Load token ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'auto_identity_tokens.json'
            with open(ledger_file, 'r') as f:
                ledger = json.load(f)
            
            # Create token entry
            token_entry = {
                "token_id": token_result["token_id"],
                "token_type": token_result["token_type"],
                "citizen_did": token_result["claims"]["sub"],
                "claims": token_result["claims"],
                "status": "ACTIVE",
                "created_at": token_result["created_at"],
                "expires_at": token_result["expires_at"],
                "ledger_index": ledger["total_tokens"] + 1
            }
            
            # Add to ledger
            ledger["tokens"][token_result["token_id"]] = token_entry
            ledger["total_tokens"] += 1
            ledger["active_tokens"] += 1
            
            # Update indexes
            indexes = ledger["token_indexes"]
            citizen_did = token_result["claims"]["sub"]
            token_type = token_result["token_type"]
            created_date = token_result["created_at"][:10]
            
            # Index by citizen DID
            if citizen_did not in indexes["by_citizen_did"]:
                indexes["by_citizen_did"][citizen_did] = []
            indexes["by_citizen_did"][citizen_did].append(token_result["token_id"])
            
            # Index by token type
            if token_type not in indexes["by_token_type"]:
                indexes["by_token_type"][token_type] = []
            indexes["by_token_type"][token_type].append(token_result["token_id"])
            
            # Index by status
            if "ACTIVE" not in indexes["by_status"]:
                indexes["by_status"]["ACTIVE"] = []
            indexes["by_status"]["ACTIVE"].append(token_result["token_id"])
            
            # Index by date
            if created_date not in indexes["by_issued_date"]:
                indexes["by_issued_date"][created_date] = []
            indexes["by_issued_date"][created_date].append(token_result["token_id"])
            
            # Save ledger
            with open(ledger_file, 'w') as f:
                json.dump(ledger, f, indent=2)
            
            print(f"✅ Token stored in ledger: {token_result['token_id']}")
            
            return {
                "success": True,
                "token_id": token_result["token_id"],
                "ledger_index": token_entry["ledger_index"],
                "stored_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to store token in ledger: {e}")
            return {"success": False, "error": str(e)}
    
    async def _write_token_to_rust_ledger(self, token_result: Dict[str, Any]) -> Dict[str, Any]:
        """Write token transaction to Rust Indy ledger"""
        try:
            print(f"📝 Writing token to Rust ledger...")
            
            # Create transaction data
            transaction_data = {
                "transaction_type": "AUTO_IDENTITY_TOKEN_GENERATION",
                "token_id": token_result["token_id"],
                "token_type": token_result["token_type"],
                "citizen_did": token_result["claims"]["sub"],
                "token_claims": token_result["claims"],
                "created_at": token_result["created_at"],
                "expires_at": token_result["expires_at"],
                "status": "GENERATED"
            }
            
            # Write to Rust ledger
            transaction_id = await self.rust_core.write_credential_transaction(transaction_data)
            
            if transaction_id:
                print(f"✅ Token written to Rust ledger: {transaction_id}")
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "transaction_data": transaction_data,
                    "written_at": datetime.now().isoformat()
                }
            else:
                raise Exception("Failed to write to Rust ledger")
                
        except Exception as e:
            print(f"❌ Failed to write token to Rust ledger: {e}")
            return {"success": False, "error": str(e)}
    
    async def verify_auto_identity_token(self, token: str) -> Dict[str, Any]:
        """Verify auto identity token"""
        try:
            print(f"🔍 Verifying auto identity token...")
            
            # Decode and verify JWT
            try:
                claims = jwt.decode(token, self.token_config["secret_key"], 
                                 algorithms=[self.token_config["algorithm"]],
                                 audience=self.token_config["audience"],
                                 issuer=self.token_config["issuer"])
            except jwt.ExpiredSignatureError:
                return {"verified": False, "error": "Token has expired"}
            except jwt.InvalidTokenError as e:
                return {"verified": False, "error": f"Invalid token: {str(e)}"}
            
            # Check if token exists in ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'auto_identity_tokens.json'
            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    ledger = json.load(f)
                
                token_id = claims.get("jti")
                if token_id in ledger.get("tokens", {}):
                    token_entry = ledger["tokens"][token_id]
                    
                    if token_entry["status"] == "ACTIVE":
                        print(f"✅ Auto identity token verified: {token_id}")
                        
                        return {
                            "verified": True,
                            "token_id": token_id,
                            "claims": claims,
                            "token_entry": token_entry,
                            "verified_at": datetime.now().isoformat()
                        }
                    else:
                        return {"verified": False, "error": f"Token status: {token_entry['status']}"}
                else:
                    return {"verified": False, "error": "Token not found in ledger"}
            else:
                return {"verified": False, "error": "Token ledger not found"}
                
        except Exception as e:
            print(f"❌ Failed to verify auto identity token: {e}")
            return {"verified": False, "error": str(e)}
    
    async def revoke_auto_identity_token(self, token_id: str, reason: str = "Manual revocation") -> Dict[str, Any]:
        """Revoke auto identity token"""
        try:
            print(f"🚫 Revoking auto identity token: {token_id}")
            
            # Load token ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'auto_identity_tokens.json'
            with open(ledger_file, 'r') as f:
                ledger = json.load(f)
            
            if token_id in ledger.get("tokens", {}):
                token_entry = ledger["tokens"][token_id]
                token_entry["status"] = "REVOKED"
                token_entry["revoked_at"] = datetime.now().isoformat()
                token_entry["revocation_reason"] = reason
                
                # Update ledger metadata
                ledger["active_tokens"] -= 1
                ledger["revoked_tokens"] += 1
                
                # Update indexes
                indexes = ledger["token_indexes"]
                
                # Remove from active status index
                if "ACTIVE" in indexes["by_status"] and token_id in indexes["by_status"]["ACTIVE"]:
                    indexes["by_status"]["ACTIVE"].remove(token_id)
                
                # Add to revoked status index
                if "REVOKED" not in indexes["by_status"]:
                    indexes["by_status"]["REVOKED"] = []
                indexes["by_status"]["REVOKED"].append(token_id)
                
                # Save ledger
                with open(ledger_file, 'w') as f:
                    json.dump(ledger, f, indent=2)
                
                print(f"✅ Auto identity token revoked: {token_id}")
                
                return {
                    "success": True,
                    "token_id": token_id,
                    "revoked_at": datetime.now().isoformat(),
                    "reason": reason
                }
            else:
                return {"success": False, "error": "Token not found"}
                
        except Exception as e:
            print(f"❌ Failed to revoke auto identity token: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_token_statistics(self) -> Dict[str, Any]:
        """Get auto identity token statistics"""
        try:
            ledger_file = Path(__file__).parent.parent / 'data' / 'auto_identity_tokens.json'
            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    ledger = json.load(f)
                
                return {
                    "success": True,
                    "total_tokens": ledger.get("total_tokens", 0),
                    "active_tokens": ledger.get("active_tokens", 0),
                    "expired_tokens": ledger.get("expired_tokens", 0),
                    "revoked_tokens": ledger.get("revoked_tokens", 0),
                    "token_types": {
                        token_type: len(token_ids) 
                        for token_type, token_ids in ledger.get("token_indexes", {}).get("by_token_type", {}).items()
                    },
                    "generated_at": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": "Token ledger not found"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _check_misuse_protection(self, citizen_did: str) -> Dict[str, Any]:
        """Check misuse protection before generating token"""
        try:
            now = datetime.now()
            current_hour = now.replace(minute=0, second=0, microsecond=0)
            current_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Initialize tracking if needed
            if citizen_did not in self.misuse_tracking:
                self.misuse_tracking[citizen_did] = {
                    "hourly_count": 0,
                    "daily_count": 0,
                    "failed_attempts": 0,
                    "last_attempt": None,
                    "cooldown_until": None
                }
            
            tracking = self.misuse_tracking[citizen_did]
            
            # Check if in cooldown period
            if tracking.get("cooldown_until"):
                cooldown_until = datetime.fromisoformat(tracking["cooldown_until"])
                if now < cooldown_until:
                    return {
                        "allowed": False,
                        "reason": "Cooldown period active",
                        "cooldown_until": tracking["cooldown_until"]
                    }
                else:
                    # Cooldown expired, reset
                    tracking["cooldown_until"] = None
                    tracking["failed_attempts"] = 0
            
            # Check hourly rate limit
            if tracking.get("last_hour") == current_hour.isoformat():
                if tracking["hourly_count"] >= self.misuse_protection["rate_limiting"]["max_tokens_per_hour"]:
                    return {
                        "allowed": False,
                        "reason": "Hourly rate limit exceeded"
                    }
            else:
                # Reset hourly count for new hour
                tracking["hourly_count"] = 0
                tracking["last_hour"] = current_hour.isoformat()
            
            # Check daily rate limit
            if tracking.get("last_day") == current_day.isoformat():
                if tracking["daily_count"] >= self.misuse_protection["rate_limiting"]["max_tokens_per_day"]:
                    return {
                        "allowed": False,
                        "reason": "Daily rate limit exceeded"
                    }
            else:
                # Reset daily count for new day
                tracking["daily_count"] = 0
                tracking["last_day"] = current_day.isoformat()
            
            # Check failed attempts
            if tracking["failed_attempts"] >= self.misuse_protection["rate_limiting"]["max_failed_attempts"]:
                # Impose cooldown
                cooldown_until = now + timedelta(
                    minutes=self.misuse_protection["rate_limiting"]["cooldown_minutes"]
                )
                tracking["cooldown_until"] = cooldown_until.isoformat()
                return {
                    "allowed": False,
                    "reason": "Too many failed attempts",
                    "cooldown_until": tracking["cooldown_until"]
                }
            
            # All checks passed
            return {"allowed": True}
            
        except Exception as e:
            print(f"❌ Misuse protection check failed: {e}")
            return {"allowed": True}  # Allow on error to not block legitimate users
    
    async def _record_failed_attempt(self, citizen_did: str):
        """Record a failed token generation attempt"""
        try:
            if citizen_did not in self.misuse_tracking:
                self.misuse_tracking[citizen_did] = {
                    "hourly_count": 0,
                    "daily_count": 0,
                    "failed_attempts": 0,
                    "last_attempt": None,
                    "cooldown_until": None
                }
            
            self.misuse_tracking[citizen_did]["failed_attempts"] += 1
            self.misuse_tracking[citizen_did]["last_attempt"] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"❌ Failed to record failed attempt: {e}")
    
    def _record_successful_generation(self, citizen_did: str):
        """Record a successful token generation"""
        try:
            if citizen_did not in self.misuse_tracking:
                self.misuse_tracking[citizen_did] = {
                    "hourly_count": 0,
                    "daily_count": 0,
                    "failed_attempts": 0,
                    "last_attempt": None,
                    "cooldown_until": None
                }
            
            self.misuse_tracking[citizen_did]["hourly_count"] += 1
            self.misuse_tracking[citizen_did]["daily_count"] += 1
            self.misuse_tracking[citizen_did]["failed_attempts"] = 0  # Reset on success
            
        except Exception as e:
            print(f"❌ Failed to record successful generation: {e}")

# Example usage and testing
async def test_auto_identity_token_generator():
    """Test the Auto Identity Token Generator"""
    try:
        print("🧪 Testing Auto Identity Token Generator")
        print("=" * 50)
        
        # Initialize generator
        generator = AutoIdentityTokenGenerator()
        await generator.initialize()
        
        # Test with a sample DID
        test_did = "did:sdis:945e39422c35f4b4:5ca9bc8107acf8e9"  # From previous test
        
        # Test 1: Generate Identity Token
        print("\n🎫 Test 1: Generate Identity Token")
        print("-" * 30)
        
        identity_token_result = await generator.generate_auto_identity_token(
            test_did, 
            "identity_token",
            {"purpose": "government_services_access"}
        )
        
        if identity_token_result["success"]:
            print(f"✅ Identity token generated: {identity_token_result['token_id']}")
            print(f"   Token type: {identity_token_result['token_type']}")
            print(f"   Expires at: {identity_token_result['expires_at']}")
            print(f"   DID data: {identity_token_result['did_data']['success']}")
            print(f"   Resolution: {identity_token_result['resolution_data']['success']}")
            print(f"   VC credentials: {identity_token_result['vc_data']['total_credentials']}")
            
            token = identity_token_result["token"]
        else:
            print(f"❌ Identity token generation failed: {identity_token_result['error']}")
            return
        
        # Test 2: Generate Access Token
        print("\n🎫 Test 2: Generate Access Token")
        print("-" * 30)
        
        access_token_result = await generator.generate_auto_identity_token(
            test_did, 
            "access_token",
            {"service": "ledger_explorer"}
        )
        
        if access_token_result["success"]:
            print(f"✅ Access token generated: {access_token_result['token_id']}")
        
        # Test 3: Generate Service Token
        print("\n🎫 Test 3: Generate Service Token")
        print("-" * 30)
        
        service_token_result = await generator.generate_auto_identity_token(
            test_did, 
            "service_token",
            {"service": "aadhaar_verification"}
        )
        
        if service_token_result["success"]:
            print(f"✅ Service token generated: {service_token_result['token_id']}")
        
        # Test 4: Token Verification
        print("\n🔍 Test 4: Token Verification")
        print("-" * 30)
        
        verification_result = await generator.verify_auto_identity_token(token)
        
        if verification_result["verified"]:
            print(f"✅ Token verified: {verification_result['token_id']}")
            print(f"   Citizen DID: {verification_result['claims']['sub']}")
            print(f"   Token type: {verification_result['claims']['token_type']}")
            print(f"   VC count: {verification_result['claims']['vc_credentials_count']}")
        else:
            print(f"❌ Token verification failed: {verification_result['error']}")
        
        # Test 5: Token Statistics
        print("\n📊 Test 5: Token Statistics")
        print("-" * 30)
        
        stats = await generator.get_token_statistics()
        if stats["success"]:
            print(f"✅ Token statistics:")
            print(f"   Total tokens: {stats['total_tokens']}")
            print(f"   Active tokens: {stats['active_tokens']}")
            print(f"   Token types: {stats['token_types']}")
        
        print(f"\n🎉 Auto Identity Token Generator test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_auto_identity_token_generator())
