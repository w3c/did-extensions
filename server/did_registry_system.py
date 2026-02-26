#!/usr/bin/env python3
"""
DID Registry System
Centralized registry for all generated DIDs with comprehensive management.
Supports full W3C DID CRUD operations: Create, Resolve, Update, Deactivate.
"""

import asyncio
import json
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import uuid

class DIDRegistrySystem:
    """Centralized DID Registry System"""
    
    def __init__(self):
        self.registry_file = Path(__file__).parent.parent / 'data' / 'did_registry.json'
        self.registry_config = {
            "registry_id": "aadhaar_did_registry_v2",
            "version": "2.0.0",
            "max_dids": 1000000,
            "backup_enabled": True,
            "indexing_enabled": True
        }
        
        # DID indexing for fast lookup
        self.did_indexes = {
            "by_email": {},
            "by_phone": {},
            "by_aadhaar": {},
            "by_name": {},
            "by_created_date": {},
            "by_status": {}
        }
        
        # Initialize registry
        self._initialize_registry()
        
    def _initialize_registry(self):
        """Initialize the DID registry"""
        try:
            # Create data directory
            self.registry_file.parent.mkdir(exist_ok=True)
            
            # Initialize registry if not exists
            if not self.registry_file.exists():
                registry_data = {
                    "registry_metadata": {
                        "registry_id": self.registry_config["registry_id"],
                        "version": self.registry_config["version"],
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "total_dids": 0,
                        "active_dids": 0,
                        "revoked_dids": 0,
                        "max_dids": self.registry_config["max_dids"]
                    },
                    "registry_settings": {
                        "backup_enabled": self.registry_config["backup_enabled"],
                        "indexing_enabled": self.registry_config["indexing_enabled"],
                        "auto_cleanup": True,
                        "retention_days": 3650  # 10 years
                    },
                    "dids": {},
                    "indexes": {
                        "by_email": {},
                        "by_phone": {},
                        "by_aadhaar": {},
                        "by_name": {},
                        "by_created_date": {},
                        "by_status": {}
                    },
                    "statistics": {
                        "daily_registrations": {},
                        "monthly_registrations": {},
                        "blockchain_distribution": {},
                        "credential_types": {}
                    }
                }
                
                with open(self.registry_file, 'w') as f:
                    json.dump(registry_data, f, indent=2)
                
                print("✅ DID Registry initialized successfully!")
            else:
                print("✅ DID Registry loaded from existing file")
                
        except Exception as e:
            print(f"❌ Failed to initialize DID registry: {e}")
    
    async def register_did(self, did: str, did_document: Dict[str, Any], 
                          citizen_data: Dict[str, Any], 
                          blockchain: str = "indy") -> Dict[str, Any]:
        """Register a new DID in the registry"""
        try:
            print(f"📝 Registering DID in registry: {did}")
            
            # Load registry
            registry_data = await self._load_registry()
            
            # Check if DID already exists
            if did in registry_data["dids"]:
                return {"success": False, "error": "DID already exists in registry"}
            
            # Check registry capacity
            if registry_data["registry_metadata"]["total_dids"] >= self.registry_config["max_dids"]:
                return {"success": False, "error": "Registry capacity exceeded"}
            
            # Create DID entry
            did_entry = await self._create_did_entry(did, did_document, citizen_data, blockchain)
            
            # Add to registry
            registry_data["dids"][did] = did_entry
            registry_data["registry_metadata"]["total_dids"] += 1
            registry_data["registry_metadata"]["active_dids"] += 1
            registry_data["registry_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Update indexes
            await self._update_indexes(registry_data, did, did_entry)
            
            # Update statistics
            await self._update_statistics(registry_data, did_entry)
            
            # Save registry
            await self._save_registry(registry_data)
            
            print(f"✅ DID registered successfully: {did}")
            
            return {
                "success": True,
                "did": did,
                "registry_index": did_entry["registry_index"],
                "registered_at": did_entry["registered_at"],
                "blockchain": blockchain
            }
            
        except Exception as e:
            print(f"❌ Failed to register DID: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_did_entry(self, did: str, did_document: Dict[str, Any], 
                              citizen_data: Dict[str, Any], blockchain: str) -> Dict[str, Any]:
        """Create a comprehensive DID entry"""
        try:
            registry_data = await self._load_registry()
            registry_index = registry_data["registry_metadata"]["total_dids"] + 1
            
            # Extract verification methods
            verification_methods = []
            if "verificationMethod" in did_document:
                for vm in did_document["verificationMethod"]:
                    verification_methods.append({
                        "id": vm["id"],
                        "type": vm["type"],
                        "controller": vm.get("controller", did),
                        "public_key": vm.get("publicKeyBase58", vm.get("publicKeyMultibase", ""))
                    })
            
            # Extract services
            services = []
            if "service" in did_document:
                for service in did_document["service"]:
                    services.append({
                        "id": service["id"],
                        "type": service["type"],
                        "service_endpoint": service.get("serviceEndpoint", "")
                    })
            
            # Create comprehensive DID entry
            did_entry = {
                "did": did,
                "registry_index": registry_index,
                "did_document": did_document,
                "citizen_data": {
                    "name": citizen_data.get("name", ""),
                    "email": citizen_data.get("email", ""),
                    "phone": citizen_data.get("phone", ""),
                    "address": citizen_data.get("address", ""),
                    "dob": citizen_data.get("dob", ""),
                    "gender": citizen_data.get("gender", ""),
                    "aadhaar_number": citizen_data.get("aadhaar_number", "")
                },
                "blockchain_info": {
                    "blockchain": blockchain,
                    "ledger_type": blockchain,
                    "transaction_hash": f"{blockchain}_tx_{secrets.token_hex(16)}",
                    "block_number": registry_index
                },
                "verification_methods": verification_methods,
                "services": services,
                "status": "ACTIVE",
                "registered_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=3650)).isoformat(),  # 10 years
                "metadata": {
                    "created_by": "did_registry_system",
                    "version": "2.0.0",
                    "backup_enabled": True,
                    "indexed": True
                }
            }
            
            return did_entry
            
        except Exception as e:
            print(f"❌ Failed to create DID entry: {e}")
            return {}
    
    async def _update_indexes(self, registry_data: Dict[str, Any], did: str, did_entry: Dict[str, Any]):
        """Update registry indexes for fast lookup"""
        try:
            indexes = registry_data["indexes"]
            citizen_data = did_entry["citizen_data"]
            
            # Index by email
            if citizen_data["email"]:
                indexes["by_email"][citizen_data["email"]] = did
            
            # Index by phone
            if citizen_data["phone"]:
                indexes["by_phone"][citizen_data["phone"]] = did
            
            # Index by Aadhaar number
            if citizen_data["aadhaar_number"]:
                indexes["by_aadhaar"][citizen_data["aadhaar_number"]] = did
            
            # Index by name
            if citizen_data["name"]:
                indexes["by_name"][citizen_data["name"]] = did
            
            # Index by created date
            created_date = did_entry["registered_at"][:10]  # YYYY-MM-DD
            if created_date not in indexes["by_created_date"]:
                indexes["by_created_date"][created_date] = []
            indexes["by_created_date"][created_date].append(did)
            
            # Index by status
            status = did_entry["status"]
            if status not in indexes["by_status"]:
                indexes["by_status"][status] = []
            indexes["by_status"][status].append(did)
            
        except Exception as e:
            print(f"❌ Failed to update indexes: {e}")
    
    async def _update_statistics(self, registry_data: Dict[str, Any], did_entry: Dict[str, Any]):
        """Update registry statistics"""
        try:
            stats = registry_data["statistics"]
            created_date = did_entry["registered_at"][:10]
            created_month = did_entry["registered_at"][:7]  # YYYY-MM
            blockchain = did_entry["blockchain_info"]["blockchain"]
            
            # Daily registrations
            if created_date not in stats["daily_registrations"]:
                stats["daily_registrations"][created_date] = 0
            stats["daily_registrations"][created_date] += 1
            
            # Monthly registrations
            if created_month not in stats["monthly_registrations"]:
                stats["monthly_registrations"][created_month] = 0
            stats["monthly_registrations"][created_month] += 1
            
            # Blockchain distribution
            if blockchain not in stats["blockchain_distribution"]:
                stats["blockchain_distribution"][blockchain] = 0
            stats["blockchain_distribution"][blockchain] += 1
            
        except Exception as e:
            print(f"❌ Failed to update statistics: {e}")
    
    async def lookup_did(self, lookup_type: str, lookup_value: str) -> Dict[str, Any]:
        """Lookup DID by various criteria"""
        try:
            print(f"🔍 Looking up DID by {lookup_type}: {lookup_value}")
            
            registry_data = await self._load_registry()
            indexes = registry_data["indexes"]
            
            if lookup_type not in indexes:
                return {"found": False, "error": f"Invalid lookup type: {lookup_type}"}
            
            if lookup_value in indexes[lookup_type]:
                if lookup_type in ["by_email", "by_phone", "by_aadhaar", "by_name"]:
                    # Single DID lookup
                    did = indexes[lookup_type][lookup_value]
                    did_entry = registry_data["dids"][did]
                    
                    return {
                        "found": True,
                        "did": did,
                        "did_entry": did_entry,
                        "lookup_type": lookup_type,
                        "lookup_value": lookup_value
                    }
                else:
                    # Multiple DIDs lookup
                    dids = indexes[lookup_type][lookup_value]
                    did_entries = {}
                    
                    for did in dids:
                        if did in registry_data["dids"]:
                            did_entries[did] = registry_data["dids"][did]
                    
                    return {
                        "found": True,
                        "dids": dids,
                        "did_entries": did_entries,
                        "count": len(dids),
                        "lookup_type": lookup_type,
                        "lookup_value": lookup_value
                    }
            else:
                return {"found": False, "lookup_type": lookup_type, "lookup_value": lookup_value}
                
        except Exception as e:
            print(f"❌ Failed to lookup DID: {e}")
            return {"found": False, "error": str(e)}
    
    async def get_did_by_email(self, email: str) -> Dict[str, Any]:
        """Get DID by email"""
        return await self.lookup_did("by_email", email)
    
    async def get_did_by_phone(self, phone: str) -> Dict[str, Any]:
        """Get DID by phone"""
        return await self.lookup_did("by_phone", phone)
    
    async def get_did_by_aadhaar(self, aadhaar_number: str) -> Dict[str, Any]:
        """Get DID by Aadhaar number"""
        return await self.lookup_did("by_aadhaar", aadhaar_number)
    
    async def get_dids_by_status(self, status: str) -> Dict[str, Any]:
        """Get DIDs by status"""
        return await self.lookup_did("by_status", status)
    
    async def get_dids_by_date(self, date: str) -> Dict[str, Any]:
        """Get DIDs by creation date"""
        return await self.lookup_did("by_created_date", date)
    
    async def update_did_status(self, did: str, new_status: str, reason: str = "") -> Dict[str, Any]:
        """Update DID status"""
        try:
            print(f"🔄 Updating DID status: {did} -> {new_status}")
            
            registry_data = await self._load_registry()
            
            if did not in registry_data["dids"]:
                return {"success": False, "error": "DID not found in registry"}
            
            did_entry = registry_data["dids"][did]
            old_status = did_entry["status"]
            
            # Update status
            did_entry["status"] = new_status
            did_entry["last_updated"] = datetime.now().isoformat()
            
            if reason:
                did_entry["status_change_reason"] = reason
                did_entry["status_changed_at"] = datetime.now().isoformat()
            
            # Update registry metadata
            if old_status == "ACTIVE" and new_status != "ACTIVE":
                registry_data["registry_metadata"]["active_dids"] -= 1
            elif old_status != "ACTIVE" and new_status == "ACTIVE":
                registry_data["registry_metadata"]["active_dids"] += 1
            
            if new_status == "REVOKED":
                registry_data["registry_metadata"]["revoked_dids"] += 1
            
            registry_data["registry_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Update indexes
            indexes = registry_data["indexes"]
            
            # Remove from old status index
            if old_status in indexes["by_status"] and did in indexes["by_status"][old_status]:
                indexes["by_status"][old_status].remove(did)
            
            # Add to new status index
            if new_status not in indexes["by_status"]:
                indexes["by_status"][new_status] = []
            indexes["by_status"][new_status].append(did)
            
            # Save registry
            await self._save_registry(registry_data)
            
            print(f"✅ DID status updated: {did} -> {new_status}")
            
            return {
                "success": True,
                "did": did,
                "old_status": old_status,
                "new_status": new_status,
                "updated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to update DID status: {e}")
            return {"success": False, "error": str(e)}
    
    async def revoke_did(self, did: str, reason: str = "Government revocation") -> Dict[str, Any]:
        """Revoke a DID"""
        return await self.update_did_status(did, "REVOKED", reason)
    
    async def activate_did(self, did: str, reason: str = "Government approval") -> Dict[str, Any]:
        """Activate a DID"""
        return await self.update_did_status(did, "ACTIVE", reason)

    # ─────────────────────────────────────────────────────────────
    #  W3C DID RESOLVE  (Read operation)
    # ─────────────────────────────────────────────────────────────
    async def resolve_did(self, did: str) -> Dict[str, Any]:
        """
        Resolve a did:sdis DID to its DID Document.

        Returns a W3C DID Resolution Result:
        {
            "@context": "https://w3id.org/did-resolution/v1",
            "didDocument": { ... },
            "didResolutionMetadata": { "contentType": "application/did+ld+json", ... },
            "didDocumentMetadata": { "created": ..., "updated": ..., "versionId": ..., ... }
        }
        """
        try:
            print(f"🔍 Resolving DID: {did}")

            # ── 1. Registry lookup ──────────────────────────────
            registry_data = await self._load_registry()
            did_entry = registry_data.get("dids", {}).get(did)

            if not did_entry:
                # Fallback: scan did_documents.json
                did_documents_file = Path(__file__).parent.parent / 'data' / 'did_documents.json'
                if did_documents_file.exists():
                    with open(did_documents_file, 'r') as f:
                        did_docs = json.load(f)
                    if did in did_docs:
                        stored = did_docs[did]
                        return self._build_resolution_result(
                            did=did,
                            did_document=stored.get("document", {}),
                            status="ACTIVE",
                            registered_at=stored.get("created_at"),
                            updated_at=stored.get("updated_at"),
                            version_id=stored.get("version_id", "1"),
                            ipfs_cid=stored.get("ipfs_cid"),
                            from_source="did_documents_file"
                        )

                # Last fallback: citizens.json
                citizens_file = Path(__file__).parent.parent / 'data' / 'citizens.json'
                if citizens_file.exists():
                    with open(citizens_file, 'r') as f:
                        citizens = json.load(f)
                    for cit in citizens.values():
                        if cit.get('did') == did:
                            return self._build_resolution_result(
                                did=did,
                                did_document=cit.get("did_document", {}),
                                status="ACTIVE",
                                registered_at=cit.get("created_at"),
                                updated_at=cit.get("updated_at"),
                                version_id="1",
                                ipfs_cid=cit.get("ipfs_cid"),
                                from_source="citizens_file"
                            )

                return {
                    "@context": "https://w3id.org/did-resolution/v1",
                    "didDocument": None,
                    "didResolutionMetadata": {
                        "error": "notFound",
                        "message": f"DID not found: {did}",
                        "resolved_at": datetime.now().isoformat()
                    },
                    "didDocumentMetadata": {}
                }

            # ── 2. Deactivated / expired check ─────────────────
            status = did_entry.get("status", "ACTIVE")
            if status in ("REVOKED", "DEACTIVATED"):
                return {
                    "@context": "https://w3id.org/did-resolution/v1",
                    "didDocument": did_entry.get("did_document"),
                    "didResolutionMetadata": {
                        "contentType": "application/did+ld+json",
                        "resolved_at": datetime.now().isoformat()
                    },
                    "didDocumentMetadata": {
                        "created": did_entry.get("registered_at"),
                        "updated": did_entry.get("last_updated"),
                        "versionId": did_entry.get("version_id", "1"),
                        "deactivated": True,
                        "status": status,
                        "status_reason": did_entry.get("status_change_reason", "")
                    }
                }

            # ── 3. Enrich DID document with latest IPFS data ────
            did_document = did_entry.get("did_document", {})
            ipfs_cid = did_entry.get("blockchain_info", {}).get("ipfs_cid")

            # Try did_documents.json for the most up-to-date version (includes VCs)
            did_documents_file = Path(__file__).parent.parent / 'data' / 'did_documents.json'
            if did_documents_file.exists():
                with open(did_documents_file, 'r') as f:
                    did_docs = json.load(f)
                if did in did_docs:
                    stored = did_docs[did]
                    did_document = stored.get("document") or did_document
                    ipfs_cid = stored.get("ipfs_cid") or ipfs_cid

            print(f"✅ DID resolved successfully: {did}")
            return self._build_resolution_result(
                did=did,
                did_document=did_document,
                status=status,
                registered_at=did_entry.get("registered_at"),
                updated_at=did_entry.get("last_updated"),
                version_id=did_entry.get("version_id", "1"),
                ipfs_cid=ipfs_cid,
                from_source="registry"
            )

        except Exception as e:
            print(f"❌ DID resolution failed: {e}")
            import traceback; traceback.print_exc()
            return {
                "@context": "https://w3id.org/did-resolution/v1",
                "didDocument": None,
                "didResolutionMetadata": {
                    "error": "internalError",
                    "message": str(e),
                    "resolved_at": datetime.now().isoformat()
                },
                "didDocumentMetadata": {}
            }

    def _build_resolution_result(
        self, did: str, did_document: dict, status: str,
        registered_at: str, updated_at: str, version_id: str,
        ipfs_cid: str, from_source: str
    ) -> Dict[str, Any]:
        """Build a W3C-compliant DID Resolution Result object."""
        # Ensure @context is present
        if did_document and "@context" not in did_document:
            did_document["@context"] = [
                "https://www.w3.org/ns/did/v1",
                "https://w3id.org/security/suites/ed25519-2018/v1"
            ]
        return {
            "@context": "https://w3id.org/did-resolution/v1",
            "didDocument": did_document,
            "didResolutionMetadata": {
                "contentType": "application/did+ld+json",
                "resolved_at": datetime.now().isoformat(),
                "source": from_source
            },
            "didDocumentMetadata": {
                "created": registered_at,
                "updated": updated_at,
                "versionId": str(version_id),
                "deactivated": status not in ("ACTIVE",),
                "status": status,
                "ipfs_cid": ipfs_cid,
                "ipfs_url": f"https://ipfs.io/ipfs/{ipfs_cid}" if ipfs_cid else None
            }
        }

    # ─────────────────────────────────────────────────────────────
    #  W3C DID UPDATE  (Update operation)
    # ─────────────────────────────────────────────────────────────
    async def update_did_document(
        self,
        did: str,
        updates: Dict[str, Any],
        updated_by: str = "CITIZEN"
    ) -> Dict[str, Any]:
        """
        Update a DID Document with partial changes.

        `updates` may contain any combination of:
        - service           : list of service objects to add/replace
        - verificationMethod: list of VM objects to add/replace
        - remove_service_ids: list of service IDs to remove
        - custom_fields     : dict of arbitrary top-level fields to merge
        - verifiableCredentials: list of full VC objects to embed

        On success:
        - Increments versionId in registry entry
        - Writes an UPDATE transaction to rust_indy_core_ledger.json
        - Re-uploads updated document to IPFS (if available)
        - Saves back to did_documents.json and did_registry.json
        """
        try:
            print(f"🔄 Updating DID document: {did}")

            if not updates:
                return {"success": False, "error": "No updates provided"}

            # ── 1. Load current document ───────────────────────
            resolution = await self.resolve_did(did)
            if resolution["didResolutionMetadata"].get("error"):
                return {"success": False, "error": f"DID not found: {did}"}

            did_document: dict = resolution["didDocument"] or {}
            doc_metadata: dict = resolution["didDocumentMetadata"]
            current_version = int(doc_metadata.get("versionId", "1"))
            new_version = current_version + 1

            # ── 2. Apply updates ───────────────────────────────
            # Services: add or replace by id
            if "service" in updates:
                existing_services: list = did_document.get("service", [])
                incoming_ids = {s["id"] for s in updates["service"]}
                # Remove any existing services with same id
                existing_services = [s for s in existing_services if s["id"] not in incoming_ids]
                existing_services.extend(updates["service"])
                did_document["service"] = existing_services

            # Remove specific services
            if "remove_service_ids" in updates:
                remove_ids = set(updates["remove_service_ids"])
                did_document["service"] = [
                    s for s in did_document.get("service", []) if s["id"] not in remove_ids
                ]

            # Verification methods: add or replace by id
            if "verificationMethod" in updates:
                existing_vms: list = did_document.get("verificationMethod", [])
                incoming_vm_ids = {vm["id"] for vm in updates["verificationMethod"]}
                existing_vms = [vm for vm in existing_vms if vm["id"] not in incoming_vm_ids]
                existing_vms.extend(updates["verificationMethod"])
                did_document["verificationMethod"] = existing_vms

            # Embedded verifiable credentials
            if "verifiableCredentials" in updates:
                existing_vcs: list = did_document.get("verifiableCredentials", [])
                incoming_vc_ids = {vc.get("id", vc.get("credential_id", "")) for vc in updates["verifiableCredentials"]}
                existing_vcs = [vc for vc in existing_vcs
                                if vc.get("id", vc.get("credential_id", "")) not in incoming_vc_ids]
                existing_vcs.extend(updates["verifiableCredentials"])
                did_document["verifiableCredentials"] = existing_vcs
                # Keep credentialReferences in sync
                did_document["credentialReferences"] = [
                    {
                        "id": vc.get("id", vc.get("credential_id")),
                        "type": vc.get("type", "VerifiableCredential"),
                        "status": vc.get("status", "ACTIVE"),
                        "issued_at": vc.get("issuanceDate") or vc.get("issued_at"),
                        "revoked": vc.get("status") == "REVOKED"
                    }
                    for vc in did_document["verifiableCredentials"]
                ]

            # Arbitrary custom fields
            if "custom_fields" in updates:
                for k, v in updates["custom_fields"].items():
                    did_document[k] = v

            # Bump timestamps and version
            now_iso = datetime.now().isoformat()
            did_document["updated"] = now_iso
            did_document["updated_at"] = now_iso
            did_document["versionId"] = str(new_version)

            # ── 3. Write UPDATE transaction to Rust ledger ─────
            ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
            if ledger_file.exists():
                try:
                    with open(ledger_file, 'r') as f:
                        ledger = json.load(f)
                    tx_id = f"DID_UPDATE_{secrets.token_hex(12)}"
                    ledger.setdefault("transactions", {})[tx_id] = {
                        "transaction_id": tx_id,
                        "transaction_type": "DID_UPDATE",
                        "did": did,
                        "updated_by": updated_by,
                        "version_id": str(new_version),
                        "update_fields": list(updates.keys()),
                        "timestamp": now_iso
                    }
                    with open(ledger_file, 'w') as f:
                        json.dump(ledger, f, indent=2)
                except Exception as le:
                    print(f"⚠️ Could not write UPDATE transaction to ledger: {le}")
                    tx_id = f"DID_UPDATE_{secrets.token_hex(12)}"
            else:
                tx_id = f"DID_UPDATE_{secrets.token_hex(12)}"

            # ── 4. Re-upload to IPFS ───────────────────────────
            new_ipfs_cid = None
            new_ipfs_url = None
            try:
                import sys
                sys.path.insert(0, str(Path(__file__).parent))
                from ipfs_util import upload_json_to_ipfs, is_ipfs_available, get_ipfs_link
                if is_ipfs_available():
                    did_hash = did.split(':')[-1] if ':' in did else did
                    filename = f"did_{did_hash}_v{new_version}.json"
                    new_ipfs_cid = upload_json_to_ipfs(did_document, filename)
                    if new_ipfs_cid:
                        new_ipfs_url = get_ipfs_link(new_ipfs_cid)
                        print(f"✅ Updated DID document uploaded to IPFS: {new_ipfs_cid}")
            except Exception as ie:
                print(f"⚠️ IPFS upload skipped: {ie}")

            # ── 5. Persist to did_documents.json ───────────────
            did_documents_file = Path(__file__).parent.parent / 'data' / 'did_documents.json'
            did_docs = {}
            if did_documents_file.exists():
                with open(did_documents_file, 'r') as f:
                    did_docs = json.load(f)
            did_docs.setdefault(did, {})
            did_docs[did]["document"] = did_document
            did_docs[did]["updated_at"] = now_iso
            did_docs[did]["version_id"] = str(new_version)
            if new_ipfs_cid:
                did_docs[did]["ipfs_cid"] = new_ipfs_cid
                did_docs[did]["ipfs_url"] = new_ipfs_url
                did_docs[did]["last_ipfs_update"] = now_iso
            with open(did_documents_file, 'w') as f:
                json.dump(did_docs, f, indent=2)

            # ── 6. Persist version to registry ─────────────────
            registry_data = await self._load_registry()
            if did in registry_data.get("dids", {}):
                registry_data["dids"][did]["last_updated"] = now_iso
                registry_data["dids"][did]["version_id"] = str(new_version)
                if new_ipfs_cid:
                    registry_data["dids"][did].setdefault("blockchain_info", {})["ipfs_cid"] = new_ipfs_cid
                    registry_data["dids"][did].setdefault("blockchain_info", {})["ipfs_url"] = new_ipfs_url
                await self._save_registry(registry_data)

            print(f"✅ DID document updated to version {new_version}: {did}")
            return {
                "success": True,
                "did": did,
                "version_id": str(new_version),
                "transaction_id": tx_id,
                "updated_at": now_iso,
                "ipfs_cid": new_ipfs_cid,
                "ipfs_url": new_ipfs_url,
                "updated_fields": list(updates.keys())
            }

        except Exception as e:
            print(f"❌ DID document update failed: {e}")
            import traceback; traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def get_registry_statistics(self) -> Dict[str, Any]:
        """Get comprehensive registry statistics"""
        try:
            registry_data = await self._load_registry()
            
            # Calculate additional statistics
            total_dids = registry_data["registry_metadata"]["total_dids"]
            active_dids = registry_data["registry_metadata"]["active_dids"]
            revoked_dids = registry_data["registry_metadata"]["revoked_dids"]
            
            # Blockchain distribution
            blockchain_dist = registry_data["statistics"]["blockchain_distribution"]
            
            # Recent activity (last 30 days)
            recent_activity = 0
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            for date, count in registry_data["statistics"]["daily_registrations"].items():
                if datetime.fromisoformat(date) >= thirty_days_ago:
                    recent_activity += count
            
            statistics = {
                "success": True,
                "registry_metadata": registry_data["registry_metadata"],
                "summary": {
                    "total_dids": total_dids,
                    "active_dids": active_dids,
                    "revoked_dids": revoked_dids,
                    "recent_activity_30_days": recent_activity,
                    "registry_utilization": (total_dids / self.registry_config["max_dids"]) * 100
                },
                "blockchain_distribution": blockchain_dist,
                "monthly_registrations": registry_data["statistics"]["monthly_registrations"],
                "daily_registrations": registry_data["statistics"]["daily_registrations"],
                "status_distribution": {
                    status: len(dids) for status, dids in registry_data["indexes"]["by_status"].items()
                },
                "generated_at": datetime.now().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            print(f"❌ Failed to get registry statistics: {e}")
            return {"success": False, "error": str(e)}
    
    async def search_dids(self, search_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Advanced DID search with multiple criteria"""
        try:
            print(f"🔍 Advanced DID search with criteria: {search_criteria}")
            
            registry_data = await self._load_registry()
            matching_dids = []
            
            for did, did_entry in registry_data["dids"].items():
                match = True
                
                # Check each search criterion
                for key, value in search_criteria.items():
                    if key == "name" and did_entry["citizen_data"]["name"] != value:
                        match = False
                        break
                    elif key == "email" and did_entry["citizen_data"]["email"] != value:
                        match = False
                        break
                    elif key == "phone" and did_entry["citizen_data"]["phone"] != value:
                        match = False
                        break
                    elif key == "status" and did_entry["status"] != value:
                        match = False
                        break
                    elif key == "blockchain" and did_entry["blockchain_info"]["blockchain"] != value:
                        match = False
                        break
                    elif key == "created_after":
                        if datetime.fromisoformat(did_entry["registered_at"]) <= datetime.fromisoformat(value):
                            match = False
                            break
                    elif key == "created_before":
                        if datetime.fromisoformat(did_entry["registered_at"]) >= datetime.fromisoformat(value):
                            match = False
                            break
                
                if match:
                    matching_dids.append({
                        "did": did,
                        "did_entry": did_entry
                    })
            
            return {
                "success": True,
                "search_criteria": search_criteria,
                "matching_dids": matching_dids,
                "count": len(matching_dids),
                "searched_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to search DIDs: {e}")
            return {"success": False, "error": str(e)}
    
    async def _load_registry(self) -> Dict[str, Any]:
        """Load registry data from file"""
        try:
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load registry: {e}")
            return {}
    
    async def _save_registry(self, registry_data: Dict[str, Any]):
        """Save registry data to file"""
        try:
            # Create backup if enabled
            if self.registry_config["backup_enabled"]:
                backup_file = self.registry_file.with_suffix(f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
                with open(backup_file, 'w') as f:
                    json.dump(registry_data, f, indent=2)
            
            # Save main registry
            with open(self.registry_file, 'w') as f:
                json.dump(registry_data, f, indent=2)
                
        except Exception as e:
            print(f"❌ Failed to save registry: {e}")
    
    async def cleanup_expired_dids(self) -> Dict[str, Any]:
        """Cleanup expired DIDs"""
        try:
            print("🧹 Cleaning up expired DIDs...")
            
            registry_data = await self._load_registry()
            current_time = datetime.now()
            expired_dids = []
            
            for did, did_entry in registry_data["dids"].items():
                expires_at = datetime.fromisoformat(did_entry["expires_at"])
                if current_time > expires_at and did_entry["status"] == "ACTIVE":
                    expired_dids.append(did)
            
            # Update expired DIDs status
            for did in expired_dids:
                await self.update_did_status(did, "EXPIRED", "Automatic expiration")
            
            print(f"✅ Cleaned up {len(expired_dids)} expired DIDs")
            
            return {
                "success": True,
                "expired_dids": expired_dids,
                "count": len(expired_dids),
                "cleaned_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Failed to cleanup expired DIDs: {e}")
            return {"success": False, "error": str(e)}

# Example usage and testing
async def test_did_registry_system():
    """Test the DID Registry System"""
    try:
        print("🧪 Testing DID Registry System")
        print("=" * 50)
        
        # Initialize registry
        registry = DIDRegistrySystem()
        
        # Test DID registration
        print("\n📝 Testing DID registration...")
        
        test_dids = []
        for i in range(3):
            citizen_data = {
                "name": f"Test Citizen {i+1}",
                "email": f"test{i+1}@example.com",
                "phone": f"+123456789{i:02d}",
                "address": f"{100+i} Test Street",
                "dob": "1990-01-01",
                "gender": "Other",
                "aadhaar_number": f"12345678901{i}"
            }
            
            did = f"did:sdis:test_{secrets.token_hex(16)}"
            did_document = {
                "@context": "https://www.w3.org/ns/did/v1",
                "id": did,
                "verificationMethod": [{
                    "id": f"{did}#key-1",
                    "type": "Ed25519VerificationKey2018",
                    "controller": did,
                    "publicKeyBase58": f"~{secrets.token_hex(32)}"
                }]
            }
            
            registration_result = await registry.register_did(did, did_document, citizen_data, "indy")
            
            if registration_result["success"]:
                print(f"✅ DID registered: {did}")
                test_dids.append(did)
            else:
                print(f"❌ DID registration failed: {registration_result['error']}")
        
        # Test DID lookup
        print("\n🔍 Testing DID lookup...")
        
        # Lookup by email
        email_lookup = await registry.get_did_by_email("test1@example.com")
        if email_lookup["found"]:
            print(f"✅ Email lookup successful: {email_lookup['did']}")
        
        # Lookup by phone
        phone_lookup = await registry.get_did_by_phone("+12345678900")
        if phone_lookup["found"]:
            print(f"✅ Phone lookup successful: {phone_lookup['did']}")
        
        # Lookup by Aadhaar
        aadhaar_lookup = await registry.get_did_by_aadhaar("123456789010")
        if aadhaar_lookup["found"]:
            print(f"✅ Aadhaar lookup successful: {aadhaar_lookup['did']}")
        
        # Test status update
        print("\n🔄 Testing status update...")
        if test_dids:
            status_update = await registry.revoke_did(test_dids[0], "Test revocation")
            if status_update["success"]:
                print(f"✅ DID revoked: {test_dids[0]}")
        
        # Test advanced search
        print("\n🔍 Testing advanced search...")
        search_criteria = {
            "status": "ACTIVE",
            "blockchain": "indy"
        }
        search_result = await registry.search_dids(search_criteria)
        if search_result["success"]:
            print(f"✅ Advanced search found {search_result['count']} DIDs")
        
        # Test registry statistics
        print("\n📊 Testing registry statistics...")
        stats = await registry.get_registry_statistics()
        if stats["success"]:
            print(f"✅ Registry statistics:")
            print(f"   Total DIDs: {stats['summary']['total_dids']}")
            print(f"   Active DIDs: {stats['summary']['active_dids']}")
            print(f"   Revoked DIDs: {stats['summary']['revoked_dids']}")
            print(f"   Utilization: {stats['summary']['registry_utilization']:.2f}%")
        
        print(f"\n🎉 DID Registry System test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_did_registry_system())
