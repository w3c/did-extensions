#!/usr/bin/env python3
"""
Complete Ethereum-PQIE Integration Example
Demonstrates full workflow with Ethereum blockchain
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pqie_framework import PQIEFramework
from ethereum_pqie_integration import EthereumPQIEIntegration, EthereumPQIEFramework

def main():
    """
    Complete Ethereum-PQIE integration demonstration
    """
    print("🔐 Ethereum-PQIE Integration Demo")
    print("=" * 50)
    
    # Initialize PQIE Framework
    print("\n1️⃣ Initializing PQIE Framework...")
    pqie = PQIEFramework()
    
    # Initialize Ethereum Integration
    print("\n2️⃣ Initializing Ethereum Integration...")
    eth_integration = EthereumPQIEIntegration(
        web3_provider="http://localhost:8545",  # Update with your provider
        private_key="0x..."  # Update with your private key
    )
    
    # Check Ethereum connection
    print("\n3️⃣ Checking Ethereum Connection...")
    stats = eth_integration.get_ethereum_stats()
    if stats.get("connected"):
        print(f"✅ Connected to Ethereum (Chain ID: {stats['network_id']})")
        print(f"📊 Latest Block: {stats['latest_block']}")
        print(f"⛽ Gas Price: {stats['gas_price_gwei']} gwei")
    else:
        print(f"❌ Ethereum connection failed: {stats.get('error')}")
        return
    
    # Create Ethereum-PQIE Framework
    print("\n4️⃣ Creating Ethereum-PQIE Framework...")
    eth_pqie = EthereumPQIEFramework(pqie, eth_integration)
    
    # Sample user data
    user_attributes = {
        "name": "Alice Johnson",
        "email": "alice.johnson@example.com",
        "phone": "+1234567890",
        "address": "123 Quantum Street, Crypto City, 12345",
        "dob": "1985-06-15",
        "gender": "Female",
        "national_id": "198506154321",
        "ethereum_address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4Db45"  # Example
    }
    
    # Generate and register identity
    print("\n5️⃣ Generating and Registering Identity on Ethereum...")
    try:
        identity_result = eth_pqie.generate_and_register_identity(
            user_attributes, 
            user_identifier="alice_ethereum"
        )
        
        did = identity_result["pqie_package"]["did"]
        print(f"✅ Identity generated: {did}")
        print(f"📝 Ethereum TX: {identity_result['ethereum_registration']['transaction_hash']}")
        print(f"⛽ Gas Used: {identity_result['ethereum_registration']['gas_used']}")
        
    except Exception as e:
        print(f"❌ Identity generation failed: {e}")
        return
    
    # Verify identity on Ethereum
    print("\n6️⃣ Verifying Identity on Ethereum...")
    try:
        verification = eth_pqie.verify_ethereum_identity(did)
        if verification["blockchain_verified"]:
            print(f"✅ Identity verified on Ethereum")
            print(f"👤 Owner: {verification['ethereum_record']['owner']}")
            print(f"📅 Created: {verification['ethereum_record']['timestamp']}")
        else:
            print(f"❌ Verification failed: {verification.get('error')}")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    
    # Update identity
    print("\n7️⃣ Updating Identity on Ethereum...")
    updates = {
        "service": [{
            "id": f"{did}#ethereum-storage",
            "type": "EthereumStorageService",
            "serviceEndpoint": f"https://storage.ethereum.network/{did}"
        }]
    }
    
    try:
        update_result = eth_pqie.update_ethereum_identity(did, updates)
        print(f"✅ Identity updated on Ethereum")
        print(f"📝 Update TX: {update_result['ethereum_update']['transaction_hash']}")
        
    except Exception as e:
        print(f"❌ Update failed: {e}")
    
    # Get final verification
    print("\n8️⃣ Final Identity Verification...")
    try:
        final_verification = eth_pqie.verify_ethereum_identity(did)
        print(f"🔍 Final Status: {'Active' if final_verification['ethereum_record']['active'] else 'Inactive'}")
        
    except Exception as e:
        print(f"❌ Final verification failed: {e}")
    
    print("\n🎉 Ethereum-PQIE Integration Demo Complete!")

def deploy_contract_demo():
    """
    Demonstrate contract deployment
    """
    print("🏗️ Ethereum Smart Contract Deployment Demo")
    print("=" * 50)
    
    # Initialize components
    pqie = PQIEFramework()
    eth_integration = EthereumPQIEIntegration(
        web3_provider="http://localhost:8545",
        private_key="0x..."  # Update with your private key
    )
    
    try:
        print("\n📋 Deploying PQIE Smart Contract...")
        contract_address = eth_integration.deploy_pqie_contract(pqie)
        print(f"✅ Contract deployed: {contract_address}")
        print(f"📝 Save this address for future use!")
        
    except Exception as e:
        print(f"❌ Contract deployment failed: {e}")

if __name__ == "__main__":
    print("Choose demo:")
    print("1. Full Ethereum-PQIE Integration")
    print("2. Smart Contract Deployment")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        main()
    elif choice == "2":
        deploy_contract_demo()
    else:
        print("Invalid choice. Running full integration demo...")
        main()
