#!/usr/bin/env python3
"""
Unified Verifiable Credential Ledger System
Cross-blockchain VC management with transaction tracking and performance metrics
"""

import asyncio
import json
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import uuid

class UnifiedVCLedger:
    """Unified Verifiable Credential Ledger for Cross-Blockchain Identity"""
    
    def __init__(self):
        self.ledger_file = Path(__file__).parent.parent / 'data' / 'unified_vc_ledger.json'
        self.ledger_config = {
            "ledger_id": "unified_vc_cross_blockchain_ledger_v1",
            "version": "1.0.0",
            "max_credentials": 10000000,
            "supported_blockchains": ["indy", "ethereum", "polkadot", "hyperledger_fabric"]
        }
        
        # Transaction tracking
        self.transaction_types = {
            "ISSUANCE": "credential_issuance",
            "UPDATE": "credential_update",
            "REVOCATION": "credential_revocation",
            "SUSPENSION": "credential_suspension",
            "TRANSFER": "credential_transfer",
            "BACKUP": "credential_backup"
        }
        
        # Initialize ledger
        self._initialize_ledger()
    
    def _initialize_ledger(self):
        """Initialize the unified VC ledger"""
        try:
            self.ledger_file.parent.mkdir(exist_ok=True)
            
            if not self.ledger_file.exists():
                ledger_data = {
                    "ledger_metadata": {
                        "ledger_id": self.ledger_config["ledger_id"],
                        "version": self.ledger_config["version"],
                        "created_at": datetime.now().isoformat(),
                        "last_updated": datetime.now().isoformat(),
                        "supported_blockchains": self.ledger_config["supported_blockchains"],
                        "total_credentials": 0,
                        "total_transactions": 0,
                        "cross_chain_credentials": 0,
                        "active_credentials": 0,
                        "revoked_credentials": 0,
                        "suspended_credentials": 0
                    },
                    "performance_metrics": {
                        "total_issuances": 0,
                        "total_updates": 0,
                        "total_revocations": 0,
                        "average_transaction_time_ms": 0,
                        "average_transaction_cost_tokens": 0,
                        "throughput_tps": 0,
                        "blockchain_distribution": {},
                        "transaction_times": [],
                        "transaction_costs": [],
                        "scalability_metrics": {
                            "max_concurrent_transactions": 0,
                            "peak_tps": 0,
                            "latency_p95_ms": 0,
                            "latency_p99_ms": 0
                        }
                    },
                    "credentials": {},
                    "transactions": {},
                    "cross_chain_mappings": {},
                    "blockchain_registries": {
                        "indy": {"dids": {}, "credentials": {}},
                        "ethereum": {"dids": {}, "credentials": {}},
                        "polkadot": {"dids": {}, "credentials": {}},
                        "hyperledger_fabric": {"dids": {}, "credentials": {}}
                    },
                    "misuse_protection": {
                        "fraud_detection_count": 0,
                        "blocked_attempts": 0,
                        "suspicious_patterns": [],
                        "rate_limits": {}
                    }
                }
                
                with open(self.ledger_file, 'w') as f:
                    json.dump(ledger_data, f, indent=2)
                
                print("✅ Unified VC Ledger initialized successfully!")
            else:
                print("✅ Unified VC Ledger loaded from existing file")
                
        except Exception as e:
            print(f"❌ Failed to initialize unified VC ledger: {e}")
            import traceback
            traceback.print_exc()
    
    async def issue_credential(self, citizen_did: str, credential_data: Dict[str, Any], 
                              blockchain: str = "indy", cross_chain: bool = False) -> Dict[str, Any]:
        """Issue verifiable credential with transaction tracking and performance metrics"""
        try:
            print(f"📝 Issuing VC on {blockchain} blockchain for DID: {citizen_did}")
            start_time = datetime.now()
            
            # Load ledger
            ledger_data = await self._load_ledger()
            
            # Check blockchain support
            if blockchain not in self.ledger_config["supported_blockchains"]:
                return {"success": False, "error": f"Unsupported blockchain: {blockchain}"}
            
            # Generate credential ID
            credential_id = f"vc_{blockchain}_{secrets.token_hex(16)}"
            
            # Create credential entry
            credential_entry = {
                "credential_id": credential_id,
                "citizen_did": citizen_did,
                "blockchain": blockchain,
                "cross_chain": cross_chain,
                "credential_data": credential_data,
                "status": "ACTIVE",
                "issued_at": datetime.now().isoformat(),
                "issuer": "government_portal",
                "verification_keys": {
                    "public_key": f"pk_{secrets.token_hex(32)}",
                    "proof_type": "Ed25519Signature2020"
                },
                "metadata": {
                    "version": "1.0",
                    "credential_type": credential_data.get("type", "kyc"),
                    "schem_version": "1.0"
                },
                "performance": {
                    "issuance_time_ms": 0,
                    "transaction_fee": 0,
                    "gas_cost": 0 if blockchain in ["ethereum", "polkadot"] else 0
                }
            }
            
            # Store credential
            ledger_data["credentials"][credential_id] = credential_entry
            
            # Register on blockchain-specific registry
            if citizen_did not in ledger_data["blockchain_registries"][blockchain]["dids"]:
                ledger_data["blockchain_registries"][blockchain]["dids"][citizen_did] = {
                    "registered_at": datetime.now().isoformat(),
                    "credentials": []
                }
            
            ledger_data["blockchain_registries"][blockchain]["dids"][citizen_did]["credentials"].append(credential_id)
            ledger_data["blockchain_registries"][blockchain]["credentials"][credential_id] = credential_entry
            
            # Create transaction record
            transaction_id = f"tx_{blockchain}_{secrets.token_hex(16)}"
            transaction_entry = await self._create_transaction(
                transaction_id, "ISSUANCE", citizen_did, credential_id, 
                blockchain, start_time
            )
            
            ledger_data["transactions"][transaction_id] = transaction_entry
            
            # Update metadata
            ledger_data["ledger_metadata"]["total_credentials"] += 1
            ledger_data["ledger_metadata"]["total_transactions"] += 1
            ledger_data["ledger_metadata"]["active_credentials"] += 1
            if cross_chain:
                ledger_data["ledger_metadata"]["cross_chain_credentials"] += 1
            
            # Update performance metrics
            await self._update_performance_metrics(ledger_data, transaction_entry, "ISSUANCE")
            
            # Save ledger
            await self._save_ledger(ledger_data)
            
            print(f"✅ VC issued on {blockchain}: {credential_id}")
            
            return {
                "success": True,
                "credential_id": credential_id,
                "transaction_id": transaction_id,
                "blockchain": blockchain,
                "cross_chain": cross_chain,
                "performance": transaction_entry["performance"]
            }
            
        except Exception as e:
            print(f"❌ Failed to issue credential: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_credential(self, credential_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing verifiable credential"""
        try:
            print(f"🔄 Updating VC: {credential_id}")
            start_time = datetime.now()
            
            ledger_data = await self._load_ledger()
            
            if credential_id not in ledger_data["credentials"]:
                return {"success": False, "error": "Credential not found"}
            
            credential = ledger_data["credentials"][credential_id]
            
            # Check if can be updated
            if credential["status"] not in ["ACTIVE", "SUSPENDED"]:
                return {"success": False, "error": "Cannot update credential in current status"}
            
            # Update credential data
            old_data = credential["credential_data"].copy()
            credential["credential_data"].update(updates)
            credential["updated_at"] = datetime.now().isoformat()
            credential["update_count"] = credential.get("update_count", 0) + 1
            
            # Create transaction
            transaction_id = f"tx_update_{secrets.token_hex(16)}"
            transaction_entry = await self._create_transaction(
                transaction_id, "UPDATE", credential["citizen_did"], 
                credential_id, credential["blockchain"], start_time
            )
            transaction_entry["updates"] = updates
            transaction_entry["old_data"] = old_data
            
            ledger_data["transactions"][transaction_id] = transaction_entry
            
            # Update performance metrics
            await self._update_performance_metrics(ledger_data, transaction_entry, "UPDATE")
            
            # Save ledger
            await self._save_ledger(ledger_data)
            
            print(f"✅ VC updated: {credential_id}")
            
            return {
                "success": True,
                "credential_id": credential_id,
                "transaction_id": transaction_id,
                "performance": transaction_entry["performance"]
            }
            
        except Exception as e:
            print(f"❌ Failed to update credential: {e}")
            return {"success": False, "error": str(e)}
    
    async def revoke_credential(self, credential_id: str, reason: str = "Government revocation") -> Dict[str, Any]:
        """Revoke verifiable credential"""
        try:
            print(f"🚫 Revoking VC: {credential_id}")
            start_time = datetime.now()
            
            ledger_data = await self._load_ledger()
            
            if credential_id not in ledger_data["credentials"]:
                return {"success": False, "error": "Credential not found"}
            
            credential = ledger_data["credentials"][credential_id]
            
            # Update status
            credential["status"] = "REVOKED"
            credential["revoked_at"] = datetime.now().isoformat()
            credential["revocation_reason"] = reason
            
            # Create transaction
            transaction_id = f"tx_revoke_{secrets.token_hex(16)}"
            transaction_entry = await self._create_transaction(
                transaction_id, "REVOCATION", credential["citizen_did"], 
                credential_id, credential["blockchain"], start_time
            )
            transaction_entry["revocation_reason"] = reason
            
            ledger_data["transactions"][transaction_id] = transaction_entry
            
            # Update metadata
            ledger_data["ledger_metadata"]["active_credentials"] -= 1
            ledger_data["ledger_metadata"]["revoked_credentials"] += 1
            
            # Update performance metrics
            await self._update_performance_metrics(ledger_data, transaction_entry, "REVOCATION")
            
            # Save ledger
            await self._save_ledger(ledger_data)
            
            print(f"✅ VC revoked: {credential_id}")
            
            return {
                "success": True,
                "credential_id": credential_id,
                "transaction_id": transaction_id,
                "performance": transaction_entry["performance"]
            }
            
        except Exception as e:
            print(f"❌ Failed to revoke credential: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_cross_chain_mapping(self, credential_id: str, target_blockchain: str) -> Dict[str, Any]:
        """Create cross-chain mapping for a credential"""
        try:
            print(f"🌐 Creating cross-chain mapping: {credential_id} -> {target_blockchain}")
            
            ledger_data = await self._load_ledger()
            
            if credential_id not in ledger_data["credentials"]:
                return {"success": False, "error": "Credential not found"}
            
            credential = ledger_data["credentials"][credential_id]
            source_blockchain = credential["blockchain"]
            
            # Create mapping entry
            mapping_id = f"mapping_{credential_id}_{target_blockchain}"
            mapping_entry = {
                "mapping_id": mapping_id,
                "source_credential_id": credential_id,
                "source_blockchain": source_blockchain,
                "target_blockchain": target_blockchain,
                "mapped_at": datetime.now().isoformat(),
                "status": "ACTIVE",
                "verification_hash": secrets.token_hex(32)
            }
            
            ledger_data["cross_chain_mappings"][mapping_id] = mapping_entry
            
            # Mark credential as cross-chain
            credential["cross_chain"] = True
            if "cross_chain_mappings" not in credential:
                credential["cross_chain_mappings"] = []
            credential["cross_chain_mappings"].append(mapping_id)
            
            # Save ledger
            await self._save_ledger(ledger_data)
            
            print(f"✅ Cross-chain mapping created: {mapping_id}")
            
            return {
                "success": True,
                "mapping_id": mapping_id,
                "source_blockchain": source_blockchain,
                "target_blockchain": target_blockchain
            }
            
        except Exception as e:
            print(f"❌ Failed to create cross-chain mapping: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_transaction(self, transaction_id: str, transaction_type: str, 
                                 citizen_did: str, credential_id: str, blockchain: str, 
                                 start_time: datetime) -> Dict[str, Any]:
        """Create transaction entry with performance tracking"""
        end_time = datetime.now()
        duration_ms = (end_time - start_time).total_seconds() * 1000
        
        # Simulate blockchain costs
        costs = {
            "indy": {"transaction_fee": 0, "gas_cost": 0},
            "ethereum": {"transaction_fee": 0.001, "gas_cost": 21000},
            "polkadot": {"transaction_fee": 0.0001, "gas_cost": 1000000},
            "hyperledger_fabric": {"transaction_fee": 0, "gas_cost": 0}
        }
        
        blockchain_cost = costs.get(blockchain, {"transaction_fee": 0, "gas_cost": 0})
        
        transaction = {
            "transaction_id": transaction_id,
            "transaction_type": transaction_type,
            "citizen_did": citizen_did,
            "credential_id": credential_id,
            "blockchain": blockchain,
            "timestamp": start_time.isoformat(),
            "status": "COMMITTED",
            "performance": {
                "duration_ms": round(duration_ms, 2),
                "transaction_fee": blockchain_cost["transaction_fee"],
                "gas_cost": blockchain_cost["gas_cost"],
                "latency_ms": round(duration_ms, 2)
            }
        }
        
        return transaction
    
    async def _update_performance_metrics(self, ledger_data: Dict[str, Any], 
                                         transaction_entry: Dict[str, Any], 
                                         transaction_type: str):
        """Update performance metrics"""
        metrics = ledger_data["performance_metrics"]
        
        # Update counts
        if transaction_type == "ISSUANCE":
            metrics["total_issuances"] += 1
        elif transaction_type == "UPDATE":
            metrics["total_updates"] += 1
        elif transaction_type == "REVOCATION":
            metrics["total_revocations"] += 1
        
        # Update transaction times
        duration_ms = transaction_entry["performance"]["duration_ms"]
        metrics["transaction_times"].append(duration_ms)
        
        # Keep only last 1000 times
        if len(metrics["transaction_times"]) > 1000:
            metrics["transaction_times"] = metrics["transaction_times"][-1000:]
        
        # Update average transaction time
        if metrics["transaction_times"]:
            metrics["average_transaction_time_ms"] = round(
                sum(metrics["transaction_times"]) / len(metrics["transaction_times"]), 2
            )
        
        # Update transaction costs
        cost = transaction_entry["performance"]["transaction_fee"]
        metrics["transaction_costs"].append(cost)
        
        # Keep only last 1000 costs
        if len(metrics["transaction_costs"]) > 1000:
            metrics["transaction_costs"] = metrics["transaction_costs"][-1000:]
        
        # Update average cost
        if metrics["transaction_costs"]:
            metrics["average_transaction_cost_tokens"] = round(
                sum(metrics["transaction_costs"]) / len(metrics["transaction_costs"]), 6
            )
        
        # Update blockchain distribution
        blockchain = transaction_entry["blockchain"]
        if blockchain not in metrics["blockchain_distribution"]:
            metrics["blockchain_distribution"][blockchain] = 0
        metrics["blockchain_distribution"][blockchain] += 1
        
        # Update scalability metrics
        metrics["scalability_metrics"]["peak_tps"] = max(
            metrics["scalability_metrics"]["peak_tps"],
            len(metrics["transaction_times"])
        )
        
        # Calculate percentiles
        if metrics["transaction_times"]:
            sorted_times = sorted(metrics["transaction_times"])
            n = len(sorted_times)
            metrics["scalability_metrics"]["latency_p95_ms"] = round(sorted_times[int(0.95 * n)], 2)
            metrics["scalability_metrics"]["latency_p99_ms"] = round(sorted_times[int(0.99 * n)], 2)
        
        ledger_data["performance_metrics"] = metrics
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        ledger_data = await self._load_ledger()
        return ledger_data["performance_metrics"]
    
    async def get_ledger_statistics(self) -> Dict[str, Any]:
        """Get ledger statistics"""
        ledger_data = await self._load_ledger()
        return {
            "success": True,
            "ledger_metadata": ledger_data["ledger_metadata"],
            "performance_metrics": ledger_data["performance_metrics"],
            "total_credentials": ledger_data["ledger_metadata"]["total_credentials"],
            "total_transactions": ledger_data["ledger_metadata"]["total_transactions"],
            "cross_chain_credentials": ledger_data["ledger_metadata"]["cross_chain_credentials"],
            "supported_blockchains": ledger_data["ledger_metadata"]["supported_blockchains"]
        }
    
    async def _load_ledger(self) -> Dict[str, Any]:
        """Load the unified VC ledger"""
        try:
            with open(self.ledger_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load ledger: {e}")
            return {}
    
    async def _save_ledger(self, ledger_data: Dict[str, Any]):
        """Save the unified VC ledger"""
        try:
            ledger_data["ledger_metadata"]["last_updated"] = datetime.now().isoformat()
            with open(self.ledger_file, 'w') as f:
                json.dump(ledger_data, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save ledger: {e}")

# Test the unified VC ledger
async def test_unified_vc_ledger():
    """Test the unified VC ledger"""
    print("🧪 Testing Unified VC Ledger")
    print("=" * 60)
    
    ledger = UnifiedVCLedger()
    
    # Test issuing credentials on different blockchains
    citizen_did = "did:sdis:test123:456789"
    
    print("\n1. Testing credential issuance on Indy...")
    result1 = await ledger.issue_credential(
        citizen_did,
        {"type": "kyc", "level": "LEVEL_1", "status": "VERIFIED"},
        "indy"
    )
    print(f"✅ Result: {result1.get('credential_id', 'Failed')}")
    
    print("\n2. Testing credential issuance on Ethereum...")
    result2 = await ledger.issue_credential(
        citizen_did,
        {"type": "kyc", "level": "LEVEL_1", "status": "VERIFIED"},
        "ethereum"
    )
    print(f"✅ Result: {result2.get('credential_id', 'Failed')}")
    
    print("\n3. Testing cross-chain mapping...")
    if result1.get('success'):
        mapping = await ledger.create_cross_chain_mapping(
            result1["credential_id"], "ethereum"
        )
        print(f"✅ Mapping: {mapping.get('mapping_id', 'Failed')}")
    
    print("\n4. Testing credential update...")
    if result1.get('success'):
        update = await ledger.update_credential(
            result1["credential_id"],
            {"level": "LEVEL_2"}
        )
        print(f"✅ Update: {update.get('transaction_id', 'Failed')}")
    
    print("\n5. Testing credential revocation...")
    if result1.get('success'):
        revoke = await ledger.revoke_credential(result1["credential_id"])
        print(f"✅ Revocation: {revoke.get('transaction_id', 'Failed')}")
    
    print("\n6. Getting performance metrics...")
    metrics = await ledger.get_performance_metrics()
    print(f"✅ Average transaction time: {metrics.get('average_transaction_time_ms', 0)}ms")
    print(f"✅ Average cost: {metrics.get('average_transaction_cost_tokens', 0)} tokens")
    print(f"✅ Blockchain distribution: {metrics.get('blockchain_distribution', {})}")
    
    print("\n7. Getting ledger statistics...")
    stats = await ledger.get_ledger_statistics()
    print(f"✅ Total credentials: {stats.get('total_credentials', 0)}")
    print(f"✅ Total transactions: {stats.get('total_transactions', 0)}")
    print(f"✅ Cross-chain credentials: {stats.get('cross_chain_credentials', 0)}")
    
    print("\n🎉 Unified VC Ledger test completed!")

if __name__ == "__main__":
    asyncio.run(test_unified_vc_ledger())

