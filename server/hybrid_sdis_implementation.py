
#!/usr/bin/env python3
"""
HYBRID Blockchain Implementation with SDIS DID Method
Supports both Hyperledger Indy and Ethereum with SDIS DID format
"""

import asyncio
from typing import Dict, Any
from server.real_blockchain_did import RealBlockchainDIDManager

class HybridIndyBlockchainManager:
    """HYBRID Blockchain Manager using SDIS DID method"""
    
    def __init__(self):
        self.blockchain_manager = RealBlockchainDIDManager()
        print("🔗 Hybrid Blockchain Manager initialized with SDIS DID support")
    
    async def create_citizen_did(self, citizen_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create citizen DID using SDIS method"""
        try:
            # Try Indy first, fallback to Ethereum
            result = await self.blockchain_manager.create_indy_did(citizen_data)
            if result.get('status') == 'simulated':
                # If Indy simulation, try Ethereum
                eth_result = await self.blockchain_manager.create_ethereum_did(citizen_data)
                if eth_result.get('status') != 'simulated':
                    return eth_result
            return result
        except Exception as e:
            print(f"❌ Hybrid DID creation failed: {e}")
            # Fallback to simulation
            return await self.blockchain_manager._simulate_sdis_did(citizen_data, "indy")
    
    async def verify_did(self, did: str) -> bool:
        """Verify DID on blockchain"""
        try:
            result = await self.blockchain_manager.verify_did(did)
            return result.get('verified', False)
        except Exception as e:
            print(f"❌ DID verification failed: {e}")
            return False
    
    async def get_ledger_status(self) -> Dict[str, Any]:
        """Get blockchain ledger status"""
        return {
            "indy": {
                "status": "connected" if (hasattr(self.blockchain_manager, 'INDY_AVAILABLE') and self.blockchain_manager.INDY_AVAILABLE) else "local_storage",
                "method": "sdis",
                "description": "Hyperledger Indy with SDIS DID method"
            },
            "ethereum": {
                "status": "connected" if (hasattr(self.blockchain_manager, 'ETHEREUM_AVAILABLE') and self.blockchain_manager.ETHEREUM_AVAILABLE) else "local_storage",
                "method": "sdis", 
                "description": "Ethereum with SDIS DID method"
            }
        }
    
    async def query_ledger(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Query blockchain ledger"""
        return {
            "query": query,
            "results": [],
            "total": 0,
            "ledger_type": "hybrid_sdis",
            "status": "success"
        }

# Test the implementation
if __name__ == "__main__":
    async def test_sdis_implementation():
        manager = HybridIndyBlockchainManager()
        
        # Test citizen data
        citizen_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "1234567890"
        }
        
        print("🔗 Testing SDIS DID Implementation")
        print("=" * 50)
        
        # Test DID creation
        print("\n📋 Testing SDIS DID Creation:")
        result = await manager.create_citizen_did(citizen_data)
        print(f"✅ SDIS DID: {result['did']}")
        print(f"   Status: {result['status']}")
        print(f"   Method: {result.get('did_method', 'unknown')}")
        print(f"   Ledger: {result['ledger_type']}")
        
        # Test verification
        print("\n🔍 Testing DID Verification:")
        verified = await manager.verify_did(result['did'])
        print(f"✅ Verification: {verified}")
        
        # Test ledger status
        print("\n📊 Testing Ledger Status:")
        status = await manager.get_ledger_status()
        print(f"✅ Indy Status: {status['indy']['status']}")
        print(f"✅ Ethereum Status: {status['ethereum']['status']}")
    
    asyncio.run(test_sdis_implementation())
