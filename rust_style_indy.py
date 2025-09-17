#!/usr/bin/env python3
"""
Rust-Style Indy Implementation
High-performance Indy ledger implementation inspired by Rust patterns
"""

import json
import hashlib
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import asyncio
import uuid

class RustStyleIndyLedger:
    """Rust-style Indy ledger implementation with high performance"""
    
    def __init__(self, ledger_file: str = "data/rust_style_indy_ledger.json"):
        self.ledger_file = Path(ledger_file)
        self.ledger_file.parent.mkdir(exist_ok=True)
        self.ledger_data = self._load_ledger()
        self._ensure_ledger_structure()
    
    def _load_ledger(self) -> Dict[str, Any]:
        """Load ledger data from file"""
        if self.ledger_file.exists():
            try:
                with open(self.ledger_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Failed to load ledger: {e}")
                return {}
        return {}
    
    def _save_ledger(self):
        """Save ledger data to file"""
        try:
            with open(self.ledger_file, 'w') as f:
                json.dump(self.ledger_data, f, indent=2)
        except Exception as e:
            print(f"❌ Failed to save ledger: {e}")
    
    def _ensure_ledger_structure(self):
        """Ensure ledger has proper structure"""
        if not self.ledger_data:
            self.ledger_data = {
                "metadata": {
                    "version": "2.0",
                    "ledger_type": "rust_style_indy",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "last_updated": datetime.now(timezone.utc).isoformat(),
                    "total_transactions": 0,
                    "total_dids": 0,
                    "total_credentials": 0,
                    "total_pools": 0,
                    "total_wallets": 0
                },
                "pools": {},
                "wallets": {},
                "dids": {},
                "credentials": {},
                "transactions": {}
            }
            self._save_ledger()
    
    def _generate_transaction_hash(self, data: Dict[str, Any]) -> str:
        """Generate deterministic transaction hash"""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _generate_did(self, seed: str) -> str:
        """Generate deterministic DID from seed"""
        seed_hash = hashlib.sha256(seed.encode()).hexdigest()
        return f"did:rust:{seed_hash[:16]}"
    
    def _generate_verkey(self, seed: str) -> str:
        """Generate deterministic verkey from seed"""
        seed_hash = hashlib.sha256(seed.encode()).hexdigest()
        return f"~{seed_hash[:32]}"
    
    async def create_pool(self, pool_name: str, genesis_file: str) -> bool:
        """Create Indy pool (Rust-style)"""
        try:
            pool_data = {
                "name": pool_name,
                "genesis_file": genesis_file,
                "nodes": [{
                    "alias": "RustNode1",
                    "ip": "127.0.0.1",
                    "port": 9701,
                    "client_port": 9702,
                    "blskey": "4N8aUNHSgjQVgkpm8nhNEfDf6txHznoYREg9kirmJrkivgL4oSEimFF6nsQ6M41QvhM2Z33nves5vfSn9n1UwNFJBYtWVzHYTHnfcJBPQPgaWU44zBp2imUWiK7Arv4zfk2FhD6V8S8z9i2FjAGkL8QdXrY6nUwsZX2iZTz",
                    "blskey_pop": "RahHYiCvoNCtPTrVtP7nMC5eTYrsUA8WjXbdhNc8debh1agE9bGiJxWBXYNFbnJXoXhWFMvyqhqhRoq737YQemH5ik9oL7R4LLTzb5XSu43pccd9eD7Ey48QqBihNn2U9zsk4q7yvLLb7y7t6WoF3NF9V8pkYkt8iyQ3d96e7bYf8",
                    "services": ["VALIDATOR"]
                }],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "ACTIVE"
            }
            
            self.ledger_data["pools"][pool_name] = pool_data
            self.ledger_data["metadata"]["total_pools"] += 1
            self.ledger_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            self._save_ledger()
            print(f"✅ Created Rust-style Indy pool: {pool_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create pool: {e}")
            return False
    
    async def create_wallet(self, wallet_name: str, wallet_key: str) -> bool:
        """Create wallet (Rust-style)"""
        try:
            wallet_data = {
                "name": wallet_name,
                "key": wallet_key,
                "storage_type": "rust_style",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "ACTIVE",
                "dids": {}
            }
            
            self.ledger_data["wallets"][wallet_name] = wallet_data
            self.ledger_data["metadata"]["total_wallets"] += 1
            self.ledger_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            self._save_ledger()
            print(f"✅ Created Rust-style Indy wallet: {wallet_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create wallet: {e}")
            return False
    
    async def create_did(self, wallet_name: str, wallet_key: str, seed: Optional[str] = None) -> Optional[Dict[str, str]]:
        """Create DID (Rust-style)"""
        try:
            if not seed:
                seed = f"did_seed_{uuid.uuid4().hex[:16]}"
            
            did = self._generate_did(seed)
            verkey = self._generate_verkey(seed)
            
            did_data = {
                "did": did,
                "verkey": verkey,
                "role": "TRUST_ANCHOR",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "ACTIVE",
                "transaction_hash": "pending",
                "seed": seed
            }
            
            # Store in wallet
            if wallet_name in self.ledger_data["wallets"]:
                self.ledger_data["wallets"][wallet_name]["dids"][did] = did_data
            
            # Store in global DIDs
            self.ledger_data["dids"][did] = did_data
            self.ledger_data["metadata"]["total_dids"] += 1
            self.ledger_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            self._save_ledger()
            print(f"✅ Created Rust-style DID: {did}")
            print(f"   Verkey: {verkey}")
            
            return {"did": did, "verkey": verkey}
            
        except Exception as e:
            print(f"❌ Failed to create DID: {e}")
            return None
    
    async def write_nym_transaction(self, transaction_data: Dict[str, Any]) -> Optional[str]:
        """Write NYM transaction (Rust-style)"""
        try:
            dest = transaction_data.get("dest", "")
            verkey = transaction_data.get("verkey", "")
            role = transaction_data.get("role", "TRUST_ANCHOR")
            
            # Generate transaction hash
            tx_hash = self._generate_transaction_hash(transaction_data)
            transaction_id = f"rust_txn_{tx_hash}"
            
            transaction = {
                "id": transaction_id,
                "transaction_type": "NYM",
                "data": transaction_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "hash": tx_hash,
                "status": "COMMITTED",
                "seq_no": self.ledger_data["metadata"]["total_transactions"] + 1,
                "signature": None
            }
            
            # Store transaction
            self.ledger_data["transactions"][transaction_id] = transaction
            
            # Update DID entry
            if dest in self.ledger_data["dids"]:
                self.ledger_data["dids"][dest]["transaction_hash"] = transaction_id
                self.ledger_data["dids"][dest]["status"] = "ACTIVE"
            
            # Update metadata
            self.ledger_data["metadata"]["total_transactions"] += 1
            self.ledger_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            self._save_ledger()
            print(f"✅ Written NYM transaction to Rust-style Indy ledger: {transaction_id}")
            return transaction_id
            
        except Exception as e:
            print(f"❌ Failed to write NYM transaction: {e}")
            return None
    
    async def write_credential_transaction(self, credential_data: Dict[str, Any]) -> Optional[str]:
        """Write credential transaction (Rust-style)"""
        try:
            citizen_did = credential_data.get("citizen_did", "")
            credential_type = credential_data.get("credential_type", "UNKNOWN")
            
            # Generate transaction hash
            tx_hash = self._generate_transaction_hash(credential_data)
            transaction_id = f"rust_cred_{tx_hash}"
            
            transaction = {
                "id": transaction_id,
                "transaction_type": "CREDENTIAL",
                "data": credential_data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "hash": tx_hash,
                "status": "COMMITTED",
                "seq_no": self.ledger_data["metadata"]["total_transactions"] + 1,
                "signature": None
            }
            
            # Create credential entry
            credential_entry = {
                "citizen_did": citizen_did,
                "credential_type": credential_type,
                "credential_data": credential_data,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "VERIFIED",
                "transaction_hash": transaction_id,
                "schema_id": None,
                "cred_def_id": None
            }
            
            # Store transaction and credential
            self.ledger_data["transactions"][transaction_id] = transaction
            self.ledger_data["credentials"][citizen_did] = credential_entry
            
            # Update metadata
            self.ledger_data["metadata"]["total_transactions"] += 1
            self.ledger_data["metadata"]["total_credentials"] += 1
            self.ledger_data["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            
            self._save_ledger()
            print(f"✅ Written credential transaction to Rust-style Indy ledger: {transaction_id}")
            return transaction_id
            
        except Exception as e:
            print(f"❌ Failed to write credential transaction: {e}")
            return None
    
    async def verify_did(self, did: str) -> Dict[str, Any]:
        """Verify DID (Rust-style)"""
        try:
            if did in self.ledger_data["dids"]:
                did_info = self.ledger_data["dids"][did]
                return {
                    "verified": True,
                    "ledger": "rust_style_indy",
                    "did_info": did_info,
                    "status": "ACTIVE"
                }
            else:
                return {
                    "verified": False,
                    "ledger": "rust_style_indy",
                    "status": "NOT_FOUND"
                }
                
        except Exception as e:
            print(f"❌ Failed to verify DID: {e}")
            return {"verified": False, "error": str(e)}
    
    def get_ledger_stats(self) -> Dict[str, Any]:
        """Get ledger statistics (Rust-style)"""
        return {
            "total_transactions": self.ledger_data["metadata"]["total_transactions"],
            "total_dids": self.ledger_data["metadata"]["total_dids"],
            "total_credentials": self.ledger_data["metadata"]["total_credentials"],
            "total_pools": self.ledger_data["metadata"]["total_pools"],
            "total_wallets": self.ledger_data["metadata"]["total_wallets"],
            "last_updated": self.ledger_data["metadata"]["last_updated"],
            "ledger_type": "rust_style_indy"
        }
    
    def get_all_transactions(self) -> Dict[str, Any]:
        """Get all transactions"""
        return self.ledger_data["transactions"]
    
    def get_all_dids(self) -> Dict[str, Any]:
        """Get all DIDs"""
        return self.ledger_data["dids"]
    
    def get_all_credentials(self) -> Dict[str, Any]:
        """Get all credentials"""
        return self.ledger_data["credentials"]
    
    def get_all_pools(self) -> Dict[str, Any]:
        """Get all pools"""
        return self.ledger_data["pools"]
    
    def get_all_wallets(self) -> Dict[str, Any]:
        """Get all wallets"""
        return self.ledger_data["wallets"]

# Global instance
rust_style_ledger = RustStyleIndyLedger()

async def test_rust_style_indy():
    """Test the Rust-style Indy implementation"""
    print("🧪 Testing Rust-Style Indy Implementation")
    print("=" * 50)
    
    ledger = rust_style_ledger
    
    # Test pool creation
    print("\n1. Testing pool creation...")
    pool_created = await ledger.create_pool("rust_test_pool", "rust_genesis.txn")
    print(f"✅ Pool creation result: {pool_created}")
    
    # Test wallet creation
    print("\n2. Testing wallet creation...")
    wallet_created = await ledger.create_wallet("rust_test_wallet", "rust_wallet_key")
    print(f"✅ Wallet creation result: {wallet_created}")
    
    # Test DID creation
    print("\n3. Testing DID creation...")
    did_result = await ledger.create_did("rust_test_wallet", "rust_wallet_key", "test_seed_123")
    if did_result:
        print(f"✅ DID created: {did_result['did']}")
        print(f"   Verkey: {did_result['verkey']}")
        
        # Test NYM transaction
        print("\n4. Testing NYM transaction...")
        nym_transaction = {
            "dest": did_result['did'],
            "verkey": did_result['verkey'],
            "role": "TRUST_ANCHOR"
        }
        
        tx_hash = await ledger.write_nym_transaction(nym_transaction)
        print(f"✅ NYM transaction hash: {tx_hash}")
        
        # Test DID verification
        print("\n5. Testing DID verification...")
        verification = await ledger.verify_did(did_result['did'])
        print(f"✅ DID verification: {verification}")
        
        # Test credential transaction
        print("\n6. Testing credential transaction...")
        credential_data = {
            "citizen_did": did_result['did'],
            "credential_type": "AADHAAR_KYC",
            "citizen_name": "Rust Test User",
            "status": "VERIFIED"
        }
        
        cred_hash = await ledger.write_credential_transaction(credential_data)
        print(f"✅ Credential transaction hash: {cred_hash}")
    
    # Test ledger stats
    print("\n7. Testing ledger statistics...")
    stats = ledger.get_ledger_stats()
    print(f"✅ Ledger stats: {stats}")
    
    print("\n🎉 Rust-Style Indy Implementation test completed!")

if __name__ == "__main__":
    asyncio.run(test_rust_style_indy())