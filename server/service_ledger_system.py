#!/usr/bin/env python3
"""
Service Ledger System
Records all government service requests, approvals, and rejections
"""

import json
import secrets
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class ServiceLedgerSystem:
    """Service Ledger System for tracking service requests and grants"""
    
    def __init__(self, ledger_file: Optional[str] = None):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        if ledger_file is None:
            ledger_file = str(self.data_dir / 'service_ledger.json')
        self.ledger_file = Path(ledger_file)
        
        # Initialize ledger if it doesn't exist
        self._initialize_ledger()
    
    def _initialize_ledger(self):
        """Initialize the service ledger file"""
        if not self.ledger_file.exists():
            ledger_data = {
                "ledger_metadata": {
                    "ledger_id": "service_ledger_v1",
                    "created_at": datetime.now().isoformat(),
                    "total_requests": 0,
                    "approved_requests": 0,
                    "rejected_requests": 0,
                    "pending_requests": 0
                },
                "service_requests": {},
                "service_grants": {}
            }
            
            with open(self.ledger_file, 'w') as f:
                json.dump(ledger_data, f, indent=2)
            
            print(f"✅ Initialized service ledger: {self.ledger_file}")
    
    async def _load_ledger(self) -> Dict[str, Any]:
        """Load ledger data from file"""
        try:
            if self.ledger_file.exists():
                with open(self.ledger_file, 'r') as f:
                    data = json.load(f)
                    # Ensure required structure exists
                    if "service_requests" not in data:
                        data["service_requests"] = {}
                    if "service_grants" not in data:
                        data["service_grants"] = {}
                    if "ledger_metadata" not in data:
                        data["ledger_metadata"] = {
                            "ledger_id": "service_ledger_v1",
                            "created_at": datetime.now().isoformat(),
                            "total_requests": 0,
                            "approved_requests": 0,
                            "rejected_requests": 0,
                            "pending_requests": 0
                        }
                    return data
            else:
                self._initialize_ledger()
                return await self._load_ledger()
        except Exception as e:
            print(f"❌ Error loading service ledger: {e}")
            return {
                "ledger_metadata": {
                    "ledger_id": "service_ledger_v1",
                    "created_at": datetime.now().isoformat(),
                    "total_requests": 0,
                    "approved_requests": 0,
                    "rejected_requests": 0,
                    "pending_requests": 0
                },
                "service_requests": {},
                "service_grants": {}
            }
    
    async def _save_ledger(self, ledger_data: Dict[str, Any]):
        """Save ledger data to file"""
        try:
            with open(self.ledger_file, 'w') as f:
                json.dump(ledger_data, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving service ledger: {e}")
            raise
    
    async def create_service_request(self, 
                                    service_id: str,
                                    service_name: str,
                                    citizen_did: str,
                                    citizen_name: str,
                                    verifiable_presentation: Dict[str, Any],
                                    identity_token: Optional[Dict[str, Any]] = None,
                                    vc_credential: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new service request with verifiable presentation"""
        try:
            ledger_data = await self._load_ledger()
            
            # Generate request ID
            request_id = f"service_req_{secrets.token_hex(16)}"
            
            # Create service request entry
            service_request = {
                "request_id": request_id,
                "service_id": service_id,
                "service_name": service_name,
                "citizen_did": citizen_did,
                "citizen_name": citizen_name,
                "verifiable_presentation": verifiable_presentation,
                "identity_token": identity_token,
                "vc_credential": vc_credential,
                "status": "PENDING",
                "requested_at": datetime.now().isoformat(),
                "requested_timestamp": datetime.now().timestamp(),
                "approved_at": None,
                "rejected_at": None,
                "approved_by": None,
                "rejected_by": None,
                "rejection_reason": None,
                "grant_id": None
            }
            
            # Store request
            ledger_data["service_requests"][request_id] = service_request
            
            # Update metadata
            ledger_data["ledger_metadata"]["total_requests"] += 1
            ledger_data["ledger_metadata"]["pending_requests"] += 1
            ledger_data["ledger_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save ledger
            await self._save_ledger(ledger_data)
            
            print(f"✅ Service request created: {request_id} for service: {service_name}")
            
            return {
                "success": True,
                "request_id": request_id,
                "service_request": service_request
            }
            
        except Exception as e:
            print(f"❌ Error creating service request: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def approve_service_request(self, 
                                     request_id: str,
                                     approved_by: str = "Government Official") -> Dict[str, Any]:
        """Approve a service request and create grant"""
        try:
            ledger_data = await self._load_ledger()
            
            if request_id not in ledger_data["service_requests"]:
                return {
                    "success": False,
                    "error": "Service request not found"
                }
            
            service_request = ledger_data["service_requests"][request_id]
            
            if service_request["status"] != "PENDING":
                return {
                    "success": False,
                    "error": f"Service request already {service_request['status']}"
                }
            
            # Generate grant ID
            grant_id = f"grant_{secrets.token_hex(16)}"
            
            # Update request status
            service_request["status"] = "APPROVED"
            service_request["approved_at"] = datetime.now().isoformat()
            service_request["approved_by"] = approved_by
            service_request["grant_id"] = grant_id
            
            # Create service grant entry
            service_grant = {
                "grant_id": grant_id,
                "request_id": request_id,
                "service_id": service_request["service_id"],
                "service_name": service_request["service_name"],
                "citizen_did": service_request["citizen_did"],
                "citizen_name": service_request["citizen_name"],
                "identity_token": service_request.get("identity_token"),
                "vc_credential": service_request.get("vc_credential"),
                "verifiable_presentation": service_request.get("verifiable_presentation"),
                "granted_at": datetime.now().isoformat(),
                "granted_by": approved_by,
                "status": "ACTIVE",
                "transaction_hash": None  # Can be set if recorded on blockchain
            }
            
            # Store grant
            ledger_data["service_grants"][grant_id] = service_grant
            
            # Update metadata
            ledger_data["ledger_metadata"]["approved_requests"] += 1
            ledger_data["ledger_metadata"]["pending_requests"] -= 1
            ledger_data["ledger_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save ledger
            await self._save_ledger(ledger_data)
            
            print(f"✅ Service request approved: {request_id}, Grant ID: {grant_id}")
            
            return {
                "success": True,
                "request_id": request_id,
                "grant_id": grant_id,
                "service_grant": service_grant,
                "service_request": service_request
            }
            
        except Exception as e:
            print(f"❌ Error approving service request: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def reject_service_request(self, 
                                    request_id: str,
                                    rejection_reason: str,
                                    rejected_by: str = "Government Official") -> Dict[str, Any]:
        """Reject a service request"""
        try:
            ledger_data = await self._load_ledger()
            
            if request_id not in ledger_data["service_requests"]:
                return {
                    "success": False,
                    "error": "Service request not found"
                }
            
            service_request = ledger_data["service_requests"][request_id]
            
            if service_request["status"] != "PENDING":
                return {
                    "success": False,
                    "error": f"Service request already {service_request['status']}"
                }
            
            # Update request status
            service_request["status"] = "REJECTED"
            service_request["rejected_at"] = datetime.now().isoformat()
            service_request["rejected_by"] = rejected_by
            service_request["rejection_reason"] = rejection_reason
            
            # Update metadata
            ledger_data["ledger_metadata"]["rejected_requests"] += 1
            ledger_data["ledger_metadata"]["pending_requests"] -= 1
            ledger_data["ledger_metadata"]["last_updated"] = datetime.now().isoformat()
            
            # Save ledger
            await self._save_ledger(ledger_data)
            
            print(f"✅ Service request rejected: {request_id}")
            
            return {
                "success": True,
                "request_id": request_id,
                "service_request": service_request
            }
            
        except Exception as e:
            print(f"❌ Error rejecting service request: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_service_requests(self, status: Optional[str] = None) -> Dict[str, Any]:
        """Get all service requests, optionally filtered by status"""
        try:
            ledger_data = await self._load_ledger()
            
            requests = list(ledger_data["service_requests"].values())
            
            if status:
                requests = [req for req in requests if req["status"] == status.upper()]
            
            # Sort by requested_at (newest first)
            requests.sort(key=lambda x: x.get("requested_timestamp", 0), reverse=True)
            
            return {
                "success": True,
                "requests": requests,
                "total": len(requests),
                "metadata": ledger_data["ledger_metadata"]
            }
            
        except Exception as e:
            print(f"❌ Error getting service requests: {e}")
            return {
                "success": False,
                "error": str(e),
                "requests": []
            }
    
    async def get_service_request(self, request_id: str) -> Dict[str, Any]:
        """Get a specific service request"""
        try:
            ledger_data = await self._load_ledger()
            
            if request_id not in ledger_data["service_requests"]:
                return {
                    "success": False,
                    "error": "Service request not found"
                }
            
            return {
                "success": True,
                "service_request": ledger_data["service_requests"][request_id]
            }
            
        except Exception as e:
            print(f"❌ Error getting service request: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_service_grants(self, citizen_did: Optional[str] = None) -> Dict[str, Any]:
        """Get all service grants, optionally filtered by citizen DID"""
        try:
            ledger_data = await self._load_ledger()
            
            grants = list(ledger_data["service_grants"].values())
            
            if citizen_did:
                grants = [grant for grant in grants if grant["citizen_did"] == citizen_did]
            
            # Sort by granted_at (newest first)
            grants.sort(key=lambda x: x.get("granted_at", ""), reverse=True)
            
            return {
                "success": True,
                "grants": grants,
                "total": len(grants)
            }
            
        except Exception as e:
            print(f"❌ Error getting service grants: {e}")
            return {
                "success": False,
                "error": str(e),
                "grants": []
            }

