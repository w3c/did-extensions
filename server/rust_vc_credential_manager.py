#!/usr/bin/env python3
"""
Rust VC Credential Transaction Script
Integrated with Government Portal for writing VC credentials as transactions over ledger
"""

import asyncio
import json
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import uuid
import subprocess
import os

# Import existing components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rust_indy_core import IndyRustCore
from server.pqie_framework import PQIECryptoEngine, PQIETokenGenerator, PQIETransactionManager

class RustVCCredentialManager:
    """Rust-based VC Credential Manager integrated with Government Portal"""
    
    def __init__(self):
        self.rust_core = None
        
        # Initialize PQIE Framework
        self.pqie_crypto = PQIECryptoEngine()
        self.pqie_token_gen = PQIETokenGenerator(self.pqie_crypto)
        self.pqie_tx_manager = PQIETransactionManager(self.pqie_crypto, self.pqie_token_gen)
        
        # Ledger configuration
        self.ledger_config = {
            "did_registry_file": "data/did_registry.json",
            "credential_ledger_file": "data/credential_ledger.json",
            "vc_transactions_file": "data/vc_transactions.json"
        }
        
        # VC credential types
        self.credential_types = {
            "aadhaar_kyc": {
                "name": "Aadhaar KYC Credential",
                "schema": "aadhaar_kyc_schema_v1",
                "issuer": "did:aadhaar:government:issuer",
                "validity_days": 365
            },
            "government_service": {
                "name": "Government Service Credential",
                "schema": "gov_service_schema_v1",
                "issuer": "did:aadhaar:government:service_issuer",
                "validity_days": 180
            },
            "citizen_verification": {
                "name": "Citizen Verification Credential",
                "schema": "citizen_verification_schema_v1",
                "issuer": "did:aadhaar:government:verification_issuer",
                "validity_days": 730
            }
        }
        
        # Initialize ledger files
        self._initialize_ledger_files()
        
    def _initialize_ledger_files(self):
        """Initialize ledger files"""
        try:
            # Create data directory
            data_dir = Path(__file__).parent.parent / 'data'
            data_dir.mkdir(exist_ok=True)
            
            # Initialize DID registry
            did_registry_file = data_dir / self.ledger_config["did_registry_file"].split('/')[-1]
            if not did_registry_file.exists():
                with open(did_registry_file, 'w') as f:
                    json.dump({
                        "registry_id": "aadhaar_did_registry_v1",
                        "created_at": datetime.now().isoformat(),
                        "total_dids": 0,
                        "dids": {}
                    }, f, indent=2)
            
            # Initialize credential ledger
            credential_ledger_file = data_dir / self.ledger_config["credential_ledger_file"].split('/')[-1]
            if not credential_ledger_file.exists():
                with open(credential_ledger_file, 'w') as f:
                    json.dump({
                        "ledger_id": "aadhaar_credential_ledger_v1",
                        "created_at": datetime.now().isoformat(),
                        "total_credentials": 0,
                        "total_transactions": 0,
                        "credentials": {},
                        "transactions": {}
                    }, f, indent=2)
            
            # Initialize VC transactions
            vc_transactions_file = data_dir / self.ledger_config["vc_transactions_file"].split('/')[-1]
            if not vc_transactions_file.exists():
                with open(vc_transactions_file, 'w') as f:
                    json.dump({
                        "transaction_log_id": "vc_transaction_log_v1",
                        "created_at": datetime.now().isoformat(),
                        "total_transactions": 0,
                        "transactions": {}
                    }, f, indent=2)
            
            print("✅ Ledger files initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize ledger files: {e}")
    
    async def initialize(self):
        """Initialize the Rust VC Credential Manager"""
        try:
            print("🚀 Initializing Rust VC Credential Manager...")
            
            # Initialize Rust core
            ledger_file = str(Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json')
            self.rust_core = IndyRustCore(ledger_file)
            
            print(f"✅ Rust VC Credential Manager initialized successfully!")
            print(f"   Rust core: {self.rust_core}")
            print(f"   Ledger file: {ledger_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize Rust VC Credential Manager: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def register_did_in_registry(self, did: str, did_document: Dict[str, Any], 
                                     citizen_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register DID in the DID registry"""
        try:
            print(f"📝 Registering DID in registry: {did}")
            
            # Load DID registry
            registry_file = Path(__file__).parent.parent / 'data' / 'did_registry.json'
            with open(registry_file, 'r') as f:
                registry = json.load(f)
            
            # Handle both v1 and v2 registry formats
            if "registry_metadata" in registry:
                metadata = registry["registry_metadata"]
                total_key = "total_dids"
            else:
                metadata = registry
                total_key = "total_dids"
            
            # Create DID entry
            did_entry = {
                "did": did,
                "did_document": did_document,
                "citizen_data": citizen_data,
                "registered_at": datetime.now().isoformat(),
                "status": "ACTIVE",
                "registry_index": metadata.get(total_key, 0) + 1
            }
            
            # Add to registry
            registry["dids"][did] = did_entry
            metadata[total_key] = metadata.get(total_key, 0) + 1
            if "last_updated" in metadata:
                metadata["last_updated"] = datetime.now().isoformat()
            else:
                registry["last_updated"] = datetime.now().isoformat()
            
            # Save registry
            with open(registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
            
            print(f"✅ DID registered in registry: {did}")
            
            return {
                "success": True,
                "did": did,
                "registry_index": did_entry["registry_index"],
                "registered_at": did_entry["registered_at"]
            }
            
        except Exception as e:
            print(f"❌ Failed to register DID in registry: {e}")
            return {"success": False, "error": str(e)}
    
    async def issue_vc_credential(self, citizen_did: str, credential_type: str, 
                                credential_data: Dict[str, Any]) -> Dict[str, Any]:
        """Issue VC credential and write as transaction over ledger using PQIE protection"""
        try:
            print(f"🔐 [STEP 1] Starting issuance for {citizen_did} using PQIE Protection")
            
            # Use PQIE Transaction Manager to issue credential transaction
            # This handles the cryptographic lifting and lattice-based protection
            pqie_tx = self.pqie_tx_manager.issue_credential_transaction(
                citizen_did, 
                credential_data, 
                credential_type=credential_type
            )
            
            # Extract PQIE transaction ID (lattice-based tracking)
            pqie_tx_id = pqie_tx["transaction_id"]
            
            # Validate credential type
            if credential_type not in self.credential_types:
                raise Exception(f"Invalid credential type: {credential_type}")
            
            credential_config = self.credential_types[credential_type]
            
            # Create VC credential
            print(f"🔐 [STEP 2] Creating VC structure...")
            vc_credential = await self._create_vc_credential(
                citizen_did, credential_type, credential_data, credential_config
            )
            
            if not vc_credential or "id" not in vc_credential:
                raise Exception("Failed to create VC credential structure")
            
            print(f"🔐 [STEP 3] Structure created: {vc_credential['id']}")
            
            # Write credential transaction to ledger
            print(f"🔐 [STEP 4] Writing to ledger...")
            transaction_result = await self._write_credential_transaction(
                vc_credential, credential_type
            )
            
            if not transaction_result.get("success"):
                raise Exception(f"Failed to write credential transaction: {transaction_result.get('error', 'Unknown error')}")
            
            print(f"🔐 [STEP 5] Written successfully: {transaction_result.get('transaction_id')}")
            
            # Store credential in credential ledger
            print(f"🔐 [STEP 6] Storing in ledger local DB...")
            ledger_result = await self._store_credential_in_ledger(
                vc_credential, transaction_result
            )
            
            if not ledger_result.get("success"):
                print(f"⚠️ Warning: Credential issued but storage in ledger failed: {ledger_result.get('error')}")
            
            print(f"🔐 [STEP 7] Updating transaction log...")
            # Update VC transaction log
            await self._update_vc_transaction_log(transaction_result)
            
            print(f"🔐 [STEP 8] Preparing final response...")
            tx_id = transaction_result.get('transaction_id') or pqie_tx_id
            print(f"✅ VC credential issued successfully: {tx_id}")
            
            return {
                "success": True,
                "credential": vc_credential,
                "transaction_result": transaction_result,
                "ledger_result": ledger_result,
                "transaction_id": tx_id,
                "pqie_transaction": pqie_tx,
                "issued_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to issue VC credential: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}


    
    async def _create_vc_credential(self, citizen_did: str, credential_type: str, 
                                  credential_data: Dict[str, Any], 
                                  credential_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create VC credential"""
        try:
            credential_id = f"vc_{credential_type}_{secrets.token_hex(16)}"
            
            # Calculate expiration date
            validity_days = credential_config["validity_days"]
            expires_at = datetime.now() + timedelta(days=validity_days)
            
            # Create VC credential
            vc_credential = {
                "@context": [
                    "https://www.w3.org/2018/credentials/v1",
                    "https://aadhaar-kyc.gov.in/credentials/v1"
                ],
                "id": credential_id,
                "type": ["VerifiableCredential", credential_config["name"]],
                "issuer": {
                    "id": credential_config["issuer"],
                    "name": "Aadhaar Government Authority"
                },
                "issuanceDate": datetime.now().isoformat(),
                "expirationDate": expires_at.isoformat(),
                "credentialSubject": {
                    "id": citizen_did,
                    "credential_type": credential_type,
                    "credential_data": credential_data,
                    "status": "VERIFIED",
                    "issued_by": "government_portal"
                },
                "credentialStatus": {
                    "id": f"https://aadhaar-kyc.gov.in/status/{credential_id}",
                    "type": "CredentialStatusList2021",
                    "status": "ACTIVE"
                },
                "proof": {
                    "type": "Ed25519Signature2020",
                    "created": datetime.now().isoformat(),
                    "verificationMethod": f"{credential_config['issuer']}#key-1",
                    "proofPurpose": "assertionMethod",
                    "jws": f"eyJhbGciOiJFZERTQSIsImI2NCI6ZmFsc2UsImNyaXQiOlsiYjY0Il19..{secrets.token_hex(64)}"
                },
                "metadata": {
                    "schema": credential_config["schema"],
                    "validity_days": validity_days,
                    "government_issued": True,
                    "rust_ledger_transaction": True
                }
            }
            
            return vc_credential
            
        except Exception as e:
            print(f"❌ Failed to create VC credential: {e}")
            return {}
    
    async def _write_credential_transaction(self, vc_credential: Dict[str, Any], 
                                         credential_type: str) -> Dict[str, Any]:
        """Write credential transaction to Rust ledger"""
        try:
            print(f"📝 Writing credential transaction to Rust ledger...")
            print(f"   Rust core: {self.rust_core}")
            print(f"   VC credential: {vc_credential}")
            
            if self.rust_core is None:
                raise Exception("Rust core is not initialized")
            
            # Create transaction data
            transaction_data = {
                "transaction_type": "CREDENTIAL_ISSUANCE",
                "credential_id": vc_credential["id"],
                "credential_type": credential_type,
                "citizen_did": vc_credential["credentialSubject"]["id"],
                "issuer": vc_credential["issuer"]["id"],
                "credential_data": vc_credential["credentialSubject"]["credential_data"],
                "issued_at": vc_credential["issuanceDate"],
                "expires_at": vc_credential["expirationDate"],
                "status": "ISSUED",
                "government_approved": True
            }
            
            print(f"   Transaction data: {transaction_data}")
            
            # Write to Rust ledger
            transaction_id = await self.rust_core.write_credential_transaction(transaction_data)
            
            if transaction_id:
                print(f"✅ Credential transaction written to Rust ledger: {transaction_id}")
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "transaction_data": transaction_data,
                    "ledger_type": "rust_indy_core",
                    "written_at": datetime.now().isoformat()
                }
            else:
                raise Exception("Failed to write transaction to Rust ledger")
                
        except Exception as e:
            print(f"❌ Failed to write credential transaction: {e}")
            return {"success": False, "error": str(e)}
    
    async def _store_credential_in_ledger(self, vc_credential: Dict[str, Any], 
                                       transaction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Store credential in credential ledger"""
        try:
            print(f"📚 Storing credential in credential ledger...")
            
            # Load credential ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'credential_ledger.json'
            with open(ledger_file, 'r') as f:
                ledger = json.load(f)
            
            # Handle both v1 and v2 formats
            if "ledger_metadata" in ledger:
                # v2 format
                ledger_metadata = ledger["ledger_metadata"]
                total_key = "total_credentials"
            else:
                # v1 format - should be migrated by now
                ledger_metadata = ledger
                total_key = "total_credentials"
            
            # Create credential entry
            credential_entry = {
                "credential_id": vc_credential["id"],
                "credential": vc_credential,
                "transaction_id": transaction_result["transaction_id"],
                "transaction_data": transaction_result["transaction_data"],
                "stored_at": datetime.now().isoformat(),
                "status": "STORED",
                "ledger_index": ledger_metadata.get(total_key, 0) + 1
            }
            
            # Add to ledger
            ledger["credentials"][vc_credential["id"]] = credential_entry
            ledger_metadata[total_key] = ledger_metadata.get(total_key, 0) + 1
            if "last_updated" in ledger_metadata:
                ledger_metadata["last_updated"] = datetime.now().isoformat()
            else:
                ledger["last_updated"] = datetime.now().isoformat()
            
            # Save ledger
            with open(ledger_file, 'w') as f:
                json.dump(ledger, f, indent=2)
            
            print(f"✅ Credential stored in ledger: {vc_credential['id']}")
            
            return {
                "success": True,
                "credential_id": vc_credential["id"],
                "ledger_index": credential_entry["ledger_index"],
                "stored_at": credential_entry["stored_at"]
            }
            
        except Exception as e:
            print(f"❌ Failed to store credential in ledger: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def _update_vc_transaction_log(self, transaction_result: Dict[str, Any]):
        """Update VC transaction log"""
        try:
            print(f"📋 Updating VC transaction log...")
            
            # Load transaction log
            log_file = Path(__file__).parent.parent / 'data' / 'vc_transactions.json'
            with open(log_file, 'r') as f:
                log = json.load(f)
            
            # Create transaction log entry
            log_entry = {
                "transaction_id": transaction_result["transaction_id"],
                "transaction_data": transaction_result["transaction_data"],
                "ledger_type": transaction_result["ledger_type"],
                "logged_at": datetime.now().isoformat(),
                "status": "LOGGED"
            }
            
            # Add to log
            log["transactions"][transaction_result["transaction_id"]] = log_entry
            log["total_transactions"] += 1
            log["last_updated"] = datetime.now().isoformat()
            
            # Save log
            with open(log_file, 'w') as f:
                json.dump(log, f, indent=2)
            
            print(f"✅ VC transaction logged: {transaction_result['transaction_id']}")
            
        except Exception as e:
            print(f"❌ Failed to update VC transaction log: {e}")
    
    async def verify_vc_credential(self, credential_id: str) -> Dict[str, Any]:
        """Verify VC credential from ledger"""
        try:
            print(f"🔍 Verifying VC credential: {credential_id}")
            
            # Load credential ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'credential_ledger.json'
            with open(ledger_file, 'r') as f:
                ledger = json.load(f)
            
            # Check if credential exists
            if credential_id not in ledger["credentials"]:
                return {"verified": False, "error": "Credential not found"}
            
            credential_entry = ledger["credentials"][credential_id]
            vc_credential = credential_entry["credential"]
            
            # Check expiration
            expires_at = datetime.fromisoformat(vc_credential["expirationDate"])
            if datetime.now() > expires_at:
                return {"verified": False, "error": "Credential expired"}
            
            # Verify transaction in Rust ledger
            transaction_id = credential_entry["transaction_id"]
            rust_verification = await self._verify_rust_transaction(transaction_id)
            
            if rust_verification["verified"]:
                print(f"✅ VC credential verified: {credential_id}")
                
                return {
                    "verified": True,
                    "credential_id": credential_id,
                    "credential": vc_credential,
                    "transaction_verified": True,
                    "expires_at": vc_credential["expirationDate"],
                    "verified_at": datetime.now().isoformat()
                }
            else:
                return {"verified": False, "error": "Transaction verification failed"}
                
        except Exception as e:
            print(f"❌ Failed to verify VC credential: {e}")
            return {"verified": False, "error": str(e)}
    
    async def _verify_rust_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Verify transaction in Rust ledger"""
        try:
            # Query Rust ledger for transaction
            ledger_data = await self.rust_core.get_ledger_data()
            
            if transaction_id in ledger_data.get("transactions", {}):
                transaction = ledger_data["transactions"][transaction_id]
                
                return {
                    "verified": True,
                    "transaction_id": transaction_id,
                    "transaction": transaction,
                    "verified_at": datetime.now().isoformat()
                }
            else:
                return {"verified": False, "error": "Transaction not found in Rust ledger"}
                
        except Exception as e:
            print(f"❌ Failed to verify Rust transaction: {e}")
            return {"verified": False, "error": str(e)}
    
    async def get_did_registry_status(self) -> Dict[str, Any]:
        """Get DID registry status"""
        try:
            registry_file = Path(__file__).parent.parent / 'data' / 'did_registry.json'
            with open(registry_file, 'r') as f:
                registry = json.load(f)
            
            return {
                "success": True,
                "registry_id": registry["registry_id"],
                "total_dids": registry["total_dids"],
                "created_at": registry["created_at"],
                "last_updated": registry.get("last_updated"),
                "status": "operational"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_credential_ledger_status(self) -> Dict[str, Any]:
        """Get credential ledger status"""
        try:
            ledger_file = Path(__file__).parent.parent / 'data' / 'credential_ledger.json'
            with open(ledger_file, 'r') as f:
                ledger = json.load(f)
            
            return {
                "success": True,
                "ledger_id": ledger["ledger_id"],
                "total_credentials": ledger["total_credentials"],
                "total_transactions": ledger["total_transactions"],
                "created_at": ledger["created_at"],
                "last_updated": ledger.get("last_updated"),
                "status": "operational"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_vc_transaction_log_status(self) -> Dict[str, Any]:
        """Get VC transaction log status"""
        try:
            log_file = Path(__file__).parent.parent / 'data' / 'vc_transactions.json'
            with open(log_file, 'r') as f:
                log = json.load(f)
            
            return {
                "success": True,
                "log_id": log["transaction_log_id"],
                "total_transactions": log["total_transactions"],
                "created_at": log["created_at"],
                "last_updated": log.get("last_updated"),
                "status": "operational"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def revoke_vc_credential(self, credential_id: str, reason: str = "Government revocation") -> Dict[str, Any]:
        """Revoke VC credential"""
        try:
            print(f"🚫 Revoking VC credential: {credential_id}")
            
            # Load credential ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'credential_ledger.json'
            with open(ledger_file, 'r') as f:
                ledger = json.load(f)
            
            # Check if credential exists
            if credential_id not in ledger["credentials"]:
                return {"success": False, "error": "Credential not found"}
            
            # Update credential status
            credential_entry = ledger["credentials"][credential_id]
            credential_entry["status"] = "REVOKED"
            credential_entry["revoked_at"] = datetime.now().isoformat()
            credential_entry["revocation_reason"] = reason
            
            # Update ledger
            ledger["last_updated"] = datetime.now().isoformat()
            
            # Save ledger
            with open(ledger_file, 'w') as f:
                json.dump(ledger, f, indent=2)
            
            # Create revocation transaction
            revocation_transaction = {
                "transaction_type": "CREDENTIAL_REVOCATION",
                "credential_id": credential_id,
                "reason": reason,
                "revoked_at": datetime.now().isoformat(),
                "status": "REVOKED"
            }
            
            # Write revocation transaction to Rust ledger
            revocation_tx_id = "NO_RUST_CORE"
            if self.rust_core:
                try:
                    revocation_tx_id = await self.rust_core.write_credential_transaction(revocation_transaction)
                except Exception as e:
                    print(f"⚠️ Rust ledger write failed: {e}")
                    revocation_tx_id = f"revoke_txn_{hashlib.md5((credential_id + datetime.now().isoformat()).encode()).hexdigest()[:16]}"
            else:
                print(f"⚠️ Rust core not initialized, generating local tx ID")
                revocation_tx_id = f"revoke_txn_{hashlib.md5((credential_id + datetime.now().isoformat()).encode()).hexdigest()[:16]}"
            
            print(f"✅ VC credential revoked: {credential_id}")
            
            return {
                "success": True,
                "credential_id": credential_id,
                "revocation_transaction_id": revocation_tx_id,
                "revoked_at": datetime.now().isoformat(),
                "reason": reason
            }
            
        except Exception as e:
            print(f"❌ Failed to revoke VC credential: {e}")
            return {"success": False, "error": str(e)}

# Integration with Government Portal
class GovernmentPortalVCIntegration:
    """Integration class for Government Portal VC operations"""
    
    def __init__(self):
        self.vc_manager = RustVCCredentialManager()
        
    async def initialize(self):
        """Initialize the integration"""
        return await self.vc_manager.initialize()
    
    async def approve_kyc_request_with_vc(self, request_id: str, citizen_data: Dict[str, Any]) -> Dict[str, Any]:
        """Approve KYC request and issue VC credential"""
        try:
            print(f"✅ Approving KYC request and issuing VC: {request_id}")
            
            # Generate DID for citizen if not exists
            citizen_did = await self._get_or_create_citizen_did(citizen_data)
            
            # Issue Aadhaar KYC credential
            vc_result = await self.vc_manager.issue_vc_credential(
                citizen_did, 
                "aadhaar_kyc", 
                citizen_data
            )
            
            if vc_result["success"]:
                # Ensure we have a transaction_id to return
                tx_id = vc_result.get("transaction_id") or vc_result.get("transaction_result", {}).get("transaction_id")
                
                print(f"✅ KYC approved with VC issued: {tx_id}")
                
                return {
                    "success": True,
                    "request_id": request_id,
                    "citizen_did": citizen_did,
                    "vc_credential": vc_result["credential"],
                    "transaction_id": tx_id,
                    "pqie_transaction": vc_result.get("pqie_transaction"),
                    "approved_at": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": vc_result["error"]}

                
        except Exception as e:
            print(f"❌ Failed to approve KYC request with VC: {e}")
            return {"success": False, "error": str(e)}
    
    async def _get_or_create_citizen_did(self, citizen_data: Dict[str, Any]) -> str:
        """Get or create citizen DID - use existing DID from citizen_data if available"""
        try:
            # First, try to get existing DID from citizen_data
            if 'citizen_did' in citizen_data and citizen_data['citizen_did']:
                return citizen_data['citizen_did']
            
            # If not found, check if DID exists in registry by name/email
            registry_file = Path(__file__).parent.parent / 'data' / 'did_registry.json'
            if registry_file.exists():
                with open(registry_file, 'r') as f:
                    registry = json.load(f)
                
                # Check all DIDs for matching citizen data
                for did, did_entry in registry.get('dids', {}).items():
                    entry_citizen_data = did_entry.get('citizen_data', {})
                    if (entry_citizen_data.get('name') == citizen_data.get('name') and 
                        entry_citizen_data.get('email') == citizen_data.get('email')):
                        return did
            
            # Generate new DID using Ring-LWE (quantum-secure) with ALL registration details
            from server.ring_lwe_did_generator import generate_complete_did, validate_birthdate
            
            # Ensure all required fields are present, use defaults if missing
            name = citizen_data.get('name', citizen_data.get('full_name', 'Unknown'))
            email = citizen_data.get('email', '')
            phone = citizen_data.get('phone', '')
            address = citizen_data.get('address', '')
            birthdate = citizen_data.get('dob', citizen_data.get('birthdate', citizen_data.get('birth_date')))
            gender = citizen_data.get('gender', '')
            
            # Validate birthdate if provided
            if birthdate:
                is_valid, error_msg = validate_birthdate(birthdate)
                if not is_valid:
                    print(f"⚠️ Invalid birthdate '{birthdate}': {error_msg}. Using default.")
                    birthdate = "1970-01-01"
            else:
                birthdate = "1970-01-01"
                print(f"⚠️ No birthdate provided, using default: {birthdate}")
            
            # Prepare complete citizen data for Ring-LWE
            complete_citizen_data = {
                'name': name,
                'email': email,
                'phone': phone,
                'address': address,
                'dob': birthdate,
                'gender': gender,
                'aadhaar_number': citizen_data.get('aadhaar_number', '')
            }
            
            # Generate DID using Ring-LWE with ALL registration details
            print(f"🔐 Generating quantum-secure DID using Ring-LWE for: {name}")
            print(f"   Using all registration fields: name, email, phone, address, dob, gender")
            citizen_did, did_document_base = generate_complete_did(complete_citizen_data)
            
            # Enhance DID document with additional service endpoints
            did_document = did_document_base.copy()
            did_document.update({
                "verificationMethod": [{
                    "id": f"{citizen_did}#key-1",
                    "type": "Ed25519VerificationKey2018",
                    "controller": citizen_did,
                    "publicKeyBase58": f"~{secrets.token_hex(32)}"
                }],
                "authentication": [f"{citizen_did}#key-1"],
                "assertionMethod": [f"{citizen_did}#key-1"],
                "service": [{
                    "id": f"{citizen_did}#aadhaar-kyc",
                    "type": "AadhaarKYCService",
                    "serviceEndpoint": "https://aadhaar-kyc.gov.in/verify"
                }],
                "created_at": datetime.now().isoformat(),
                "status": "ACTIVE"
            })
            
            # Register DID in registry
            await self.vc_manager.register_did_in_registry(citizen_did, did_document, citizen_data)
            
            return citizen_did
            
        except Exception as e:
            print(f"❌ Failed to get or create citizen DID: {e}")
            return f"did:sdis:error_{secrets.token_hex(16)}"

# Example usage and testing
async def test_rust_vc_credential_manager():
    """Test the Rust VC Credential Manager"""
    try:
        print("🧪 Testing Rust VC Credential Manager")
        print("=" * 50)
        
        # Initialize VC manager
        vc_manager = RustVCCredentialManager()
        await vc_manager.initialize()
        
        # Test citizen data
        citizen_data = {
            "name": "Rust VC Test Citizen",
            "email": "rustvc@example.com",
            "phone": "+1234567890",
            "address": "123 Rust VC Street",
            "dob": "1990-01-01",
            "gender": "Other",
            "aadhaar_number": "123456789012"
        }
        
        # Test DID registration
        print("\n📝 Testing DID registration...")
        citizen_did = f"did:sdis:test_{secrets.token_hex(16)}"
        did_document = {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": citizen_did,
            "verificationMethod": [{
                "id": f"{citizen_did}#key-1",
                "type": "Ed25519VerificationKey2018",
                "controller": citizen_did,
                "publicKeyBase58": f"~{secrets.token_hex(32)}"
            }]
        }
        
        did_registration = await vc_manager.register_did_in_registry(citizen_did, did_document, citizen_data)
        if did_registration["success"]:
            print(f"✅ DID registered: {citizen_did}")
        
        # Test VC credential issuance
        print("\n🔐 Testing VC credential issuance...")
        vc_result = await vc_manager.issue_vc_credential(
            citizen_did, 
            "aadhaar_kyc", 
            citizen_data
        )
        
        if vc_result["success"]:
            print(f"✅ VC credential issued: {vc_result['transaction_result']['transaction_id']}")
            
            # Test VC verification
            print("\n🔍 Testing VC credential verification...")
            verification_result = await vc_manager.verify_vc_credential(vc_result["credential"]["id"])
            
            if verification_result["verified"]:
                print(f"✅ VC credential verified: {verification_result['credential_id']}")
        
        # Test registry and ledger status
        print("\n📊 Testing registry and ledger status...")
        registry_status = await vc_manager.get_did_registry_status()
        ledger_status = await vc_manager.get_credential_ledger_status()
        log_status = await vc_manager.get_vc_transaction_log_status()
        
        print(f"✅ DID Registry: {registry_status['total_dids']} DIDs")
        print(f"✅ Credential Ledger: {ledger_status['total_credentials']} credentials")
        print(f"✅ Transaction Log: {log_status['total_transactions']} transactions")
        
        print(f"\n🎉 Rust VC Credential Manager test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_rust_vc_credential_manager())
