#!/usr/bin/env python3
"""
Credential Ledger System
Centralized ledger for all credential-related transactions with comprehensive tracking
"""

import asyncio
import json
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import uuid

class CredentialLedgerSystem:
    """Centralized Credential Ledger System"""
    
    def __init__(self):
        self.ledger_file = Path(__file__).parent.parent / 'data' / 'credential_ledger.json'
        self.ledger_config = {
            "ledger_id": "aadhaar_credential_ledger_v2",
            "version": "2.0.0",
            "max_credentials": 1000000,
            "backup_enabled": True,
            "transaction_logging": True,
            "immutable_ledger": True
        }
        
        # Credential indexing for fast lookup
        self.credential_indexes = {
            "by_citizen_did": {},
            "by_credential_type": {},
            "by_issuer": {},
            "by_status": {},
            "by_issued_date": {},
            "by_expiry_date": {},
            "by_transaction_id": {}
        }
        
        # Initialize ledger
        self._initialize_ledger()
        
    def _initialize_ledger(self):
        """Initialize the credential ledger"""
        try:
            # Create data directory
            self.ledger_file.parent.mkdir(exist_ok=True)
            
            # Initialize ledger if not exists or migrate from v1
            if not self.ledger_file.exists():
                ledger_data = {
                    "ledger_metadata": {
                        "ledger_id": self.ledger_config["ledger_id"],
                        "version": self.ledger_config["version"],
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "total_credentials": 0,
                        "total_transactions": 0,
                        "active_credentials": 0,
                        "expired_credentials": 0,
                        "revoked_credentials": 0,
                        "max_credentials": self.ledger_config["max_credentials"]
                    },
                    "ledger_settings": {
                        "backup_enabled": self.ledger_config["backup_enabled"],
                        "transaction_logging": self.ledger_config["transaction_logging"],
                        "immutable_ledger": self.ledger_config["immutable_ledger"],
                        "auto_cleanup": True,
                        "retention_days": 3650  # 10 years
                    },
                    "credentials": {},
                    "transactions": {},
                    "indexes": {
                        "by_citizen_did": {},
                        "by_credential_type": {},
                        "by_issuer": {},
                        "by_status": {},
                        "by_issued_date": {},
                        "by_expiry_date": {},
                        "by_transaction_id": {}
                    },
                    "statistics": {
                        "daily_issuances": {},
                        "monthly_issuances": {},
                        "credential_type_distribution": {},
                        "issuer_distribution": {},
                        "status_distribution": {}
                    }
                }
                
                with open(self.ledger_file, 'w') as f:
                    json.dump(ledger_data, f, indent=2)
                
                print("✅ Credential Ledger initialized successfully!")
            else:
                # Check if migration is needed
                ledger_data = self._load_ledger_sync()
                if "ledger_metadata" not in ledger_data:
                    # Migrate from v1
                    print("🔄 Migrating credential ledger from v1 to v2...")
                    migrated_data = {
                        "ledger_metadata": {
                            "ledger_id": self.ledger_config["ledger_id"],
                            "version": self.ledger_config["version"],
                            "created_at": ledger_data.get("created_at", datetime.now().isoformat()),
                            "last_updated": datetime.now().isoformat(),
                            "total_credentials": ledger_data.get("total_credentials", 0),
                            "total_transactions": ledger_data.get("total_transactions", 0),
                            "active_credentials": 0,
                            "expired_credentials": 0,
                            "revoked_credentials": 0,
                            "max_credentials": self.ledger_config["max_credentials"]
                        },
                        "ledger_settings": {
                            "backup_enabled": self.ledger_config["backup_enabled"],
                            "transaction_logging": self.ledger_config["transaction_logging"],
                            "immutable_ledger": self.ledger_config["immutable_ledger"],
                            "auto_cleanup": True,
                            "retention_days": 3650
                        },
                        "credentials": ledger_data.get("credentials", {}),
                        "transactions": ledger_data.get("transactions", {}),
                        "indexes": {
                            "by_citizen_did": {},
                            "by_credential_type": {},
                            "by_issuer": {},
                            "by_status": {},
                            "by_issued_date": {},
                            "by_expiry_date": {},
                            "by_transaction_id": {}
                        },
                        "statistics": {
                            "daily_issuances": {},
                            "monthly_issuances": {},
                            "credential_type_distribution": {},
                            "issuer_distribution": {},
                            "status_distribution": {}
                        }
                    }
                    
                    # Count statuses
                    for cred in migrated_data["credentials"].values():
                        status = cred.get("status", "ACTIVE")
                        if status == "REVOKED":
                            migrated_data["ledger_metadata"]["revoked_credentials"] += 1
                        else:
                            migrated_data["ledger_metadata"]["active_credentials"] += 1
                    
                    with open(self.ledger_file, 'w') as f:
                        json.dump(migrated_data, f, indent=2)
                    
                    print("✅ Credential Ledger migrated to v2 successfully!")
                else:
                    print("✅ Credential Ledger loaded from existing file")
        except Exception as e:
            print(f"❌ Failed to initialize credential ledger: {e}")
            import traceback
            traceback.print_exc()
    
    def _load_ledger_sync(self) -> Dict[str, Any]:
        """Load ledger synchronously for initialization"""
        try:
            with open(self.ledger_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load ledger: {e}")
            return {}
    
    async def _load_ledger(self) -> Dict[str, Any]:
        """Load the credential ledger"""
        try:
            with open(self.ledger_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load ledger: {e}")
            return {}
    
    async def _save_ledger(self, ledger_data: Dict[str, Any]):
        """Save the credential ledger"""
        try:
            with open(self.ledger_file, 'w') as f:
                json.dump(ledger_data, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save ledger: {e}")
    
    async def store_credential_transaction(self, credential_data: Dict[str, Any], 
                                         transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store credential transaction in the ledger"""
        try:
            print(f"📝 Storing credential transaction in ledger...")
            
            # Load ledger
            ledger_data = await self._load_ledger()
            
            # Check ledger capacity
            if ledger_data["ledger_metadata"]["total_credentials"] >= self.ledger_config["max_credentials"]:
                return {"success": False, "error": "Ledger capacity exceeded"}
            
            # Create credential entry
            credential_entry = await self._create_credential_entry(credential_data, transaction_data)
            
            # Create transaction entry
            transaction_entry = await self._create_transaction_entry(transaction_data, credential_entry)
            
            # Add to ledger
            ledger_data["credentials"][credential_entry["credential_id"]] = credential_entry
            ledger_data["transactions"][transaction_entry["transaction_id"]] = transaction_entry
            
            # Update metadata
            ledger_data["ledger_metadata"]["total_credentials"] += 1
            ledger_data["ledger_metadata"]["total_transactions"] += 1
            ledger_data["ledger_metadata"]["active_credentials"] += 1
            ledger_data["ledger_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Update indexes
            await self._update_credential_indexes(ledger_data, credential_entry)
            await self._update_transaction_indexes(ledger_data, transaction_entry)
            
            # Update statistics
            await self._update_credential_statistics(ledger_data, credential_entry)
            
            # Save ledger
            await self._save_ledger(ledger_data)
            
            print(f"✅ Credential transaction stored: {credential_entry['credential_id']}")
            
            return {
                "success": True,
                "credential_id": credential_entry["credential_id"],
                "transaction_id": transaction_entry["transaction_id"],
                "ledger_index": credential_entry["ledger_index"],
                "stored_at": credential_entry["stored_at"]
            }
            
        except Exception as e:
            print(f"❌ Failed to store credential transaction: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_credential_entry(self, credential_data: Dict[str, Any], 
                                     transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive credential entry"""
        try:
            ledger_data = await self._load_ledger()
            ledger_index = ledger_data["ledger_metadata"]["total_credentials"] + 1
            
            # Extract credential information
            credential_id = credential_data.get("id", f"cred_{secrets.token_hex(16)}")
            # Get citizen_did from credential data, with fallback to transaction data
            citizen_did = credential_data.get("credentialSubject", {}).get("id", "") or transaction_data.get("citizen_did", "")
            credential_type = credential_data.get("type", [])
            issuer = credential_data.get("issuer", {})
            
            # Determine credential type string
            credential_type_str = "unknown"
            if isinstance(credential_type, list) and len(credential_type) > 1:
                credential_type_str = credential_type[1].lower().replace(" ", "_")
            elif isinstance(credential_type, str):
                credential_type_str = credential_type.lower().replace(" ", "_")
            
            # Create comprehensive credential entry
            credential_entry = {
                "credential_id": credential_id,
                "ledger_index": ledger_index,
                "credential_data": credential_data,
                "citizen_did": citizen_did,
                "credential_type": credential_type_str,
                "issuer": {
                    "id": issuer.get("id", ""),
                    "name": issuer.get("name", "")
                },
                "issued_at": credential_data.get("issuanceDate", datetime.now().isoformat()),
                "expires_at": credential_data.get("expirationDate", ""),
                "status": "ACTIVE",
                "stored_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "transaction_references": [],
                "metadata": {
                    "created_by": "credential_ledger_system",
                    "version": "2.0.0",
                    "immutable": True,
                    "backup_enabled": True,
                    "indexed": True
                }
            }
            
            return credential_entry
            
        except Exception as e:
            print(f"❌ Failed to create credential entry: {e}")
            return {}
    
    async def _create_transaction_entry(self, transaction_data: Dict[str, Any], 
                                      credential_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Create a comprehensive transaction entry"""
        try:
            ledger_data = await self._load_ledger()
            transaction_index = ledger_data["ledger_metadata"]["total_transactions"] + 1
            
            # Generate transaction ID if not provided
            transaction_id = transaction_data.get("transaction_id", f"tx_{secrets.token_hex(16)}")
            
            # Create comprehensive transaction entry
            transaction_entry = {
                "transaction_id": transaction_id,
                "transaction_index": transaction_index,
                "transaction_type": transaction_data.get("transaction_type", "CREDENTIAL_ISSUANCE"),
                "credential_id": credential_entry["credential_id"],
                "citizen_did": credential_entry["citizen_did"],
                "credential_type": credential_entry["credential_type"],
                "issuer": credential_entry["issuer"],
                "transaction_data": transaction_data,
                "status": "COMMITTED",
                "created_at": datetime.now().isoformat(),
                "committed_at": datetime.now().isoformat(),
                "blockchain_info": {
                    "ledger_type": transaction_data.get("ledger_type", "credential_ledger"),
                    "block_number": transaction_index,
                    "transaction_hash": f"ledger_tx_{secrets.token_hex(16)}"
                },
                "metadata": {
                    "created_by": "credential_ledger_system",
                    "version": "2.0.0",
                    "immutable": True,
                    "verified": True
                }
            }
            
            # Add transaction reference to credential entry
            credential_entry["transaction_references"].append({
                "transaction_id": transaction_id,
                "transaction_type": transaction_entry["transaction_type"],
                "created_at": transaction_entry["created_at"]
            })
            
            return transaction_entry
            
        except Exception as e:
            print(f"❌ Failed to create transaction entry: {e}")
            return {}
    
    async def _update_credential_indexes(self, ledger_data: Dict[str, Any], credential_entry: Dict[str, Any]):
        """Update credential indexes for fast lookup"""
        try:
            indexes = ledger_data["indexes"]
            credential_id = credential_entry["credential_id"]
            
            # Index by citizen DID
            citizen_did = credential_entry["citizen_did"]
            if citizen_did:
                if citizen_did not in indexes["by_citizen_did"]:
                    indexes["by_citizen_did"][citizen_did] = []
                indexes["by_citizen_did"][citizen_did].append(credential_id)
            
            # Index by credential type
            credential_type = credential_entry["credential_type"]
            if credential_type not in indexes["by_credential_type"]:
                indexes["by_credential_type"][credential_type] = []
            indexes["by_credential_type"][credential_type].append(credential_id)
            
            # Index by issuer
            issuer_id = credential_entry["issuer"]["id"]
            if issuer_id:
                if issuer_id not in indexes["by_issuer"]:
                    indexes["by_issuer"][issuer_id] = []
                indexes["by_issuer"][issuer_id].append(credential_id)
            
            # Index by status
            status = credential_entry["status"]
            if status not in indexes["by_status"]:
                indexes["by_status"][status] = []
            indexes["by_status"][status].append(credential_id)
            
            # Index by issued date
            issued_date = credential_entry["issued_at"][:10]  # YYYY-MM-DD
            if issued_date not in indexes["by_issued_date"]:
                indexes["by_issued_date"][issued_date] = []
            indexes["by_issued_date"][issued_date].append(credential_id)
            
            # Index by expiry date
            if credential_entry["expires_at"]:
                expiry_date = credential_entry["expires_at"][:10]  # YYYY-MM-DD
                if expiry_date not in indexes["by_expiry_date"]:
                    indexes["by_expiry_date"][expiry_date] = []
                indexes["by_expiry_date"][expiry_date].append(credential_id)
            
        except Exception as e:
            print(f"❌ Failed to update credential indexes: {e}")
    
    async def _update_transaction_indexes(self, ledger_data: Dict[str, Any], transaction_entry: Dict[str, Any]):
        """Update transaction indexes for fast lookup"""
        try:
            indexes = ledger_data["indexes"]
            transaction_id = transaction_entry["transaction_id"]
            
            # Index by transaction ID
            indexes["by_transaction_id"][transaction_id] = transaction_id
            
        except Exception as e:
            print(f"❌ Failed to update transaction indexes: {e}")
    
    async def _update_credential_statistics(self, ledger_data: Dict[str, Any], credential_entry: Dict[str, Any]):
        """Update credential statistics"""
        try:
            stats = ledger_data["statistics"]
            issued_date = credential_entry["issued_at"][:10]
            issued_month = credential_entry["issued_at"][:7]  # YYYY-MM
            credential_type = credential_entry["credential_type"]
            issuer_id = credential_entry["issuer"]["id"]
            
            # Daily issuances
            if issued_date not in stats["daily_issuances"]:
                stats["daily_issuances"][issued_date] = 0
            stats["daily_issuances"][issued_date] += 1
            
            # Monthly issuances
            if issued_month not in stats["monthly_issuances"]:
                stats["monthly_issuances"][issued_month] = 0
            stats["monthly_issuances"][issued_month] += 1
            
            # Credential type distribution
            if credential_type not in stats["credential_type_distribution"]:
                stats["credential_type_distribution"][credential_type] = 0
            stats["credential_type_distribution"][credential_type] += 1
            
            # Issuer distribution
            if issuer_id not in stats["issuer_distribution"]:
                stats["issuer_distribution"][issuer_id] = 0
            stats["issuer_distribution"][issuer_id] += 1
            
        except Exception as e:
            print(f"❌ Failed to update credential statistics: {e}")
    
    async def get_credentials_by_citizen_did(self, citizen_did: str) -> Dict[str, Any]:
        """Get all credentials for a citizen DID"""
        try:
            print(f"🔍 Getting credentials for citizen DID: {citizen_did}")
            
            ledger_data = await self._load_ledger()
            indexes = ledger_data["indexes"]
            
            if citizen_did in indexes["by_citizen_did"]:
                credential_ids = indexes["by_citizen_did"][citizen_did]
                credentials = {}
                
                for credential_id in credential_ids:
                    if credential_id in ledger_data["credentials"]:
                        credentials[credential_id] = ledger_data["credentials"][credential_id]
                
                return {
                    "success": True,
                    "citizen_did": citizen_did,
                    "credentials": credentials,
                    "count": len(credentials),
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "citizen_did": citizen_did,
                    "credentials": {},
                    "count": 0,
                    "message": "No credentials found for this DID"
                }
                
        except Exception as e:
            print(f"❌ Failed to get credentials by citizen DID: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_credentials_by_type(self, credential_type: str) -> Dict[str, Any]:
        """Get all credentials of a specific type"""
        try:
            print(f"🔍 Getting credentials by type: {credential_type}")
            
            ledger_data = await self._load_ledger()
            indexes = ledger_data["indexes"]
            
            if credential_type in indexes["by_credential_type"]:
                credential_ids = indexes["by_credential_type"][credential_type]
                credentials = {}
                
                for credential_id in credential_ids:
                    if credential_id in ledger_data["credentials"]:
                        credentials[credential_id] = ledger_data["credentials"][credential_id]
                
                return {
                    "success": True,
                    "credential_type": credential_type,
                    "credentials": credentials,
                    "count": len(credentials),
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "credential_type": credential_type,
                    "credentials": {},
                    "count": 0,
                    "message": f"No credentials found for type: {credential_type}"
                }
                
        except Exception as e:
            print(f"❌ Failed to get credentials by type: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_credentials_by_status(self, status: str) -> Dict[str, Any]:
        """Get all credentials with a specific status"""
        try:
            print(f"🔍 Getting credentials by status: {status}")
            
            ledger_data = await self._load_ledger()
            indexes = ledger_data["indexes"]
            
            if status in indexes["by_status"]:
                credential_ids = indexes["by_status"][status]
                credentials = {}
                
                for credential_id in credential_ids:
                    if credential_id in ledger_data["credentials"]:
                        credentials[credential_id] = ledger_data["credentials"][credential_id]
                
                return {
                    "success": True,
                    "status": status,
                    "credentials": credentials,
                    "count": len(credentials),
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": True,
                    "status": status,
                    "credentials": {},
                    "count": 0,
                    "message": f"No credentials found with status: {status}"
                }
                
        except Exception as e:
            print(f"❌ Failed to get credentials by status: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_transaction_by_id(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction by ID"""
        try:
            print(f"🔍 Getting transaction by ID: {transaction_id}")
            
            ledger_data = await self._load_ledger()
            
            if transaction_id in ledger_data["transactions"]:
                transaction = ledger_data["transactions"][transaction_id]
                
                return {
                    "success": True,
                    "transaction_id": transaction_id,
                    "transaction": transaction,
                    "retrieved_at": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": f"Transaction not found: {transaction_id}"
                }
                
        except Exception as e:
            print(f"❌ Failed to get transaction by ID: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_credential_status(self, credential_id: str, new_status: str, 
                                    reason: str = "") -> Dict[str, Any]:
        """Update credential status"""
        try:
            print(f"🔄 Updating credential status: {credential_id} -> {new_status}")
            
            ledger_data = await self._load_ledger()
            
            if credential_id not in ledger_data["credentials"]:
                return {"success": False, "error": "Credential not found in ledger"}
            
            credential_entry = ledger_data["credentials"][credential_id]
            old_status = credential_entry["status"]
            
            # Update status
            credential_entry["status"] = new_status
            credential_entry["last_updated"] = datetime.now().isoformat()
            
            if reason:
                credential_entry["status_change_reason"] = reason
                credential_entry["status_changed_at"] = datetime.now().isoformat()
            
            # Update ledger metadata
            if old_status == "ACTIVE" and new_status != "ACTIVE":
                ledger_data["ledger_metadata"]["active_credentials"] -= 1
            elif old_status != "ACTIVE" and new_status == "ACTIVE":
                ledger_data["ledger_metadata"]["active_credentials"] += 1
            
            if new_status == "EXPIRED":
                ledger_data["ledger_metadata"]["expired_credentials"] += 1
            elif new_status == "REVOKED":
                ledger_data["ledger_metadata"]["revoked_credentials"] += 1
            
            ledger_data["ledger_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Update indexes
            indexes = ledger_data["indexes"]
            
            # Remove from old status index
            if old_status in indexes["by_status"] and credential_id in indexes["by_status"][old_status]:
                indexes["by_status"][old_status].remove(credential_id)
            
            # Add to new status index
            if new_status not in indexes["by_status"]:
                indexes["by_status"][new_status] = []
            indexes["by_status"][new_status].append(credential_id)
            
            # Save ledger
            await self._save_ledger(ledger_data)
            
            print(f"✅ Credential status updated: {credential_id} -> {new_status}")
            
            return {
                "success": True,
                "credential_id": credential_id,
                "old_status": old_status,
                "new_status": new_status,
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to update credential status: {e}")
            return {"success": False, "error": str(e)}
    
    async def revoke_credential(self, credential_id: str, reason: str = "Government revocation") -> Dict[str, Any]:
        """Revoke a credential"""
        return await self.update_credential_status(credential_id, "REVOKED", reason)
    
    async def expire_credential(self, credential_id: str, reason: str = "Automatic expiration") -> Dict[str, Any]:
        """Expire a credential"""
        return await self.update_credential_status(credential_id, "EXPIRED", reason)
    
    async def get_ledger_statistics(self) -> Dict[str, Any]:
        """Get comprehensive ledger statistics"""
        try:
            ledger_data = await self._load_ledger()
            
            # Calculate additional statistics
            total_credentials = ledger_data["ledger_metadata"]["total_credentials"]
            active_credentials = ledger_data["ledger_metadata"]["active_credentials"]
            expired_credentials = ledger_data["ledger_metadata"]["expired_credentials"]
            revoked_credentials = ledger_data["ledger_metadata"]["revoked_credentials"]
            
            # Recent activity (last 30 days)
            recent_activity = 0
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            for date, count in ledger_data["statistics"]["daily_issuances"].items():
                if datetime.fromisoformat(date) >= thirty_days_ago:
                    recent_activity += count
            
            statistics = {
                "success": True,
                "ledger_metadata": ledger_data["ledger_metadata"],
                "summary": {
                    "total_credentials": total_credentials,
                    "total_transactions": ledger_data["ledger_metadata"]["total_transactions"],
                    "active_credentials": active_credentials,
                    "expired_credentials": expired_credentials,
                    "revoked_credentials": revoked_credentials,
                    "recent_activity_30_days": recent_activity,
                    "ledger_utilization": (total_credentials / self.ledger_config["max_credentials"]) * 100
                },
                "credential_type_distribution": ledger_data["statistics"]["credential_type_distribution"],
                "issuer_distribution": ledger_data["statistics"]["issuer_distribution"],
                "monthly_issuances": ledger_data["statistics"]["monthly_issuances"],
                "daily_issuances": ledger_data["statistics"]["daily_issuances"],
                "status_distribution": {
                    status: len(credential_ids) for status, credential_ids in ledger_data["indexes"]["by_status"].items()
                },
                "generated_at": datetime.now().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            print(f"❌ Failed to get ledger statistics: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_credentials(self, search_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced credential search with multiple criteria"""
        try:
            print(f"🔍 Advanced credential search with criteria: {search_criteria}")
            
            ledger_data = await self._load_ledger()
            matching_credentials = []
            
            for credential_id, credential_entry in ledger_data["credentials"].items():
                match = True
                
                # Check each search criterion
                for key, value in search_criteria.items():
                    if key == "citizen_did" and credential_entry["citizen_did"] != value:
                        match = False
                        break
                    elif key == "credential_type" and credential_entry["credential_type"] != value:
                        match = False
                        break
                    elif key == "status" and credential_entry["status"] != value:
                        match = False
                        break
                    elif key == "issuer_id" and credential_entry["issuer"]["id"] != value:
                        match = False
                        break
                    elif key == "issued_after":
                        if datetime.fromisoformat(credential_entry["issued_at"]) <= datetime.fromisoformat(value):
                            match = False
                            break
                    elif key == "issued_before":
                        if datetime.fromisoformat(credential_entry["issued_at"]) >= datetime.fromisoformat(value):
                            match = False
                            break
                    elif key == "expires_after":
                        if credential_entry["expires_at"] and datetime.fromisoformat(credential_entry["expires_at"]) <= datetime.fromisoformat(value):
                            match = False
                            break
                    elif key == "expires_before":
                        if credential_entry["expires_at"] and datetime.fromisoformat(credential_entry["expires_at"]) >= datetime.fromisoformat(value):
                            match = False
                            break
                
                if match:
                    matching_credentials.append({
                        "credential_id": credential_id,
                        "credential_entry": credential_entry
                    })
            
            return {
                "success": True,
                "search_criteria": search_criteria,
                "matching_credentials": matching_credentials,
                "count": len(matching_credentials),
                "searched_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to search credentials: {e}")
            return {"success": False, "error": str(e)}
    
    async def cleanup_expired_credentials(self) -> Dict[str, Any]:
        """Cleanup expired credentials"""
        try:
            print("🧹 Cleaning up expired credentials...")
            
            ledger_data = await self._load_ledger()
            current_time = datetime.now()
            expired_credentials = []
            
            for credential_id, credential_entry in ledger_data["credentials"].items():
                if credential_entry["expires_at"]:
                    expires_at = datetime.fromisoformat(credential_entry["expires_at"])
                    if current_time > expires_at and credential_entry["status"] == "ACTIVE":
                        expired_credentials.append(credential_id)
            
            # Update expired credentials status
            for credential_id in expired_credentials:
                await self.update_credential_status(credential_id, "EXPIRED", "Automatic expiration")
            
            print(f"✅ Cleaned up {len(expired_credentials)} expired credentials")
            
            return {
                "success": True,
                "expired_credentials": expired_credentials,
                "count": len(expired_credentials),
                "cleaned_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to cleanup expired credentials: {e}")
            return {"success": False, "error": str(e)}
    
    async def _load_ledger(self) -> Dict[str, Any]:
        """Load ledger data from file"""
        try:
            with open(self.ledger_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load ledger: {e}")
            return {}
    
    async def _save_ledger(self, ledger_data: Dict[str, Any]):
        """Save ledger data to file"""
        try:
            # Create backup if enabled
            if self.ledger_config["backup_enabled"]:
                backup_file = self.ledger_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
                with open(backup_file, 'w') as f:
                    json.dump(ledger_data, f, indent=2)
            
            # Save main ledger
            with open(self.ledger_file, 'w') as f:
                json.dump(ledger_data, f, indent=2)
                
        except Exception as e:
            print(f"❌ Failed to save ledger: {e}")

# Example usage and testing
async def test_credential_ledger_system():
    """Test the Credential Ledger System"""
    try:
        print("🧪 Testing Credential Ledger System")
        print("=" * 50)
        
        # Initialize ledger
        ledger = CredentialLedgerSystem()
        
        # Test credential storage
        print("\n📝 Testing credential storage...")
        
        test_credentials = []
        for i in range(3):
            credential_data = {
                "id": f"cred_test_{i+1}_{secrets.token_hex(8)}",
                "type": ["VerifiableCredential", f"TestCredential{i+1}"],
                "issuer": {
                    "id": "did:aadhaar:government:issuer",
                    "name": "Aadhaar Government Authority"
                },
                "issuanceDate": datetime.now().isoformat(),
                "expirationDate": (datetime.now() + timedelta(days=365)).isoformat(),
                "credentialSubject": {
                    "id": f"did:sdis:test_citizen_{i+1}",
                    "credential_type": f"test_credential_{i+1}",
                    "status": "VERIFIED"
                }
            }
            
            transaction_data = {
                "transaction_type": "CREDENTIAL_ISSUANCE",
                "citizen_did": credential_data["credentialSubject"]["id"],
                "credential_type": f"test_credential_{i+1}",
                "issued_at": credential_data["issuanceDate"],
                "status": "ISSUED",
                "ledger_type": "credential_ledger"
            }
            
            storage_result = await ledger.store_credential_transaction(credential_data, transaction_data)
            
            if storage_result["success"]:
                print(f"✅ Credential stored: {storage_result['credential_id']}")
                test_credentials.append(storage_result["credential_id"])
            else:
                print(f"❌ Credential storage failed: {storage_result['error']}")
        
        # Test credential lookup
        print("\n🔍 Testing credential lookup...")
        
        # Lookup by citizen DID
        citizen_lookup = await ledger.get_credentials_by_citizen_did("did:sdis:test_citizen_1")
        if citizen_lookup["success"]:
            print(f"✅ Citizen lookup successful: {citizen_lookup['count']} credentials")
        
        # Lookup by credential type
        type_lookup = await ledger.get_credentials_by_type("test_credential_1")
        if type_lookup["success"]:
            print(f"✅ Type lookup successful: {type_lookup['count']} credentials")
        
        # Lookup by status
        status_lookup = await ledger.get_credentials_by_status("ACTIVE")
        if status_lookup["success"]:
            print(f"✅ Status lookup successful: {status_lookup['count']} credentials")
        
        # Test status update
        print("\n🔄 Testing status update...")
        if test_credentials:
            status_update = await ledger.revoke_credential(test_credentials[0], "Test revocation")
            if status_update["success"]:
                print(f"✅ Credential revoked: {test_credentials[0]}")
        
        # Test advanced search
        print("\n🔍 Testing advanced search...")
        search_criteria = {
            "status": "ACTIVE",
            "credential_type": "test_credential_2"
        }
        search_result = await ledger.search_credentials(search_criteria)
        if search_result["success"]:
            print(f"✅ Advanced search found {search_result['count']} credentials")
        
        # Test ledger statistics
        print("\n📊 Testing ledger statistics...")
        stats = await ledger.get_ledger_statistics()
        if stats["success"]:
            print(f"✅ Ledger statistics:")
            print(f"   Total Credentials: {stats['summary']['total_credentials']}")
            print(f"   Total Transactions: {stats['summary']['total_transactions']}")
            print(f"   Active Credentials: {stats['summary']['active_credentials']}")
            print(f"   Utilization: {stats['summary']['ledger_utilization']:.2f}%")
        
        print(f"\n🎉 Credential Ledger System test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_credential_ledger_system())
