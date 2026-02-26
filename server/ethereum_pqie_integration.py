#!/usr/bin/env python3
"""
Ethereum Integration for PQIE Framework
Smart contracts and Web3 integration for post-quantum identity on Ethereum
"""

import json
import base64
import secrets
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from web3 import Web3
from web3.contract import Contract
from web3.middleware import geth_poa_middleware
from eth_account import Account
import asyncio

class EthereumPQIEIntegration:
    """
    Complete Ethereum integration for PQIE framework
    Handles smart contracts, Web3 connections, and blockchain operations
    """
    
    def __init__(self, web3_provider: str = "http://localhost:8545", 
                 private_key: str = None, contract_address: str = None):
        """
        Initialize Ethereum integration
        
        Args:
            web3_provider: Web3 provider URL
            private_key: Private key for transactions (optional)
            contract_address: Deployed contract address (optional)
        """
        self.web3_provider = web3_provider
        self.w3 = Web3(Web3.HTTPProvider(web3_provider))
        
        # Add POA middleware for testnets
        if "testnet" in web3_provider or "localhost" in web3_provider:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        # Account setup
        self.account = None
        if private_key:
            self.account = Account.from_key(private_key)
            self.w3.eth.default_account = self.account.address
        
        # Contract setup
        self.contract_address = contract_address
        self.contract = None
        
        # Gas settings
        self.gas_limit = 5000000
        self.gas_price = self.w3.eth.gas_price
        
        print(f"🔗 Ethereum PQIE Integration initialized")
        print(f"📡 Provider: {web3_provider}")
        print(f"👤 Account: {self.account.address if self.account else 'Not set'}")
        print(f"📋 Contract: {contract_address if contract_address else 'Not deployed'}")
    
    def deploy_pqie_contract(self, pqie_framework) -> str:
        """
        Deploy PQIE smart contract to Ethereum
        
        Args:
            pqie_framework: PQIEFramework instance
            
        Returns:
            Contract address
        """
        if not self.account:
            raise ValueError("Account required for contract deployment")
        
        # Get contract bytecode and ABI
        contract_data = self._generate_pqie_contract()
        
        # Deploy contract
        contract = self.w3.eth.contract(
            abi=contract_data["abi"],
            bytecode=contract_data["bytecode"]
        )
        
        # Build transaction
        transaction = contract.constructor().build_transaction({
            'from': self.account.address,
            'gas': self.gas_limit,
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })
        
        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for deployment
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = tx_receipt.contractAddress
        
        self.contract_address = contract_address
        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=contract_data["abi"]
        )
        
        print(f"✅ PQIE Contract deployed: {contract_address}")
        return contract_address
    
    def _generate_pqie_contract(self) -> Dict[str, Any]:
        """
        Generate PQIE smart contract bytecode and ABI
        """
        # Simplified Solidity contract for PQIE
        contract_source = """
        pragma solidity ^0.8.0;

        contract PQIEIdentity {
            struct IdentityRecord {
                string did;
                string publicKey;
                string documentHash;
                uint256 timestamp;
                bool active;
                address owner;
            }
            
            mapping(string => IdentityRecord) public identities;
            mapping(address => string[]) public ownerToDids;
            
            event IdentityCreated(string indexed did, address indexed owner);
            event IdentityUpdated(string indexed did);
            event IdentityRevoked(string indexed did);
            
            function createIdentity(
                string memory did,
                string memory publicKey,
                string memory documentHash
            ) public {
                require(identities[did].timestamp == 0, "Identity already exists");
                
                identities[did] = IdentityRecord({
                    did: did,
                    publicKey: publicKey,
                    documentHash: documentHash,
                    timestamp: block.timestamp,
                    active: true,
                    owner: msg.sender
                });
                
                ownerToDids[msg.sender].push(did);
                emit IdentityCreated(did, msg.sender);
            }
            
            function updateIdentity(
                string memory did,
                string memory newDocumentHash
            ) public {
                require(identities[did].owner == msg.sender, "Not owner");
                require(identities[did].active, "Identity not active");
                
                identities[did].documentHash = newDocumentHash;
                identities[did].timestamp = block.timestamp;
                
                emit IdentityUpdated(did);
            }
            
            function revokeIdentity(string memory did) public {
                require(identities[did].owner == msg.sender, "Not owner");
                
                identities[did].active = false;
                identities[did].timestamp = block.timestamp;
                
                emit IdentityRevoked(did);
            }
            
            function getIdentity(string memory did) public view returns (
                string memory,
                string memory,
                string memory,
                uint256,
                bool,
                address
            ) {
                IdentityRecord memory record = identities[did];
                return (
                    record.did,
                    record.publicKey,
                    record.documentHash,
                    record.timestamp,
                    record.active,
                    record.owner
                );
            }
            
            function getOwnerDids(address owner) public view returns (string[] memory) {
                return ownerToDids[owner];
            }
        }
        """
        
        # For this implementation, we'll use a simplified approach
        # In production, you'd compile this with solc
        return {
            "abi": self._get_contract_abi(),
            "bytecode": "0x608060405234801561001057600080fd5b50..."  # Simplified bytecode
        }
    
    def _get_contract_abi(self) -> List[Dict[str, Any]]:
        """
        Get contract ABI for PQIE identity management
        """
        return [
            {
                "inputs": [
                    {"name": "did", "type": "string"},
                    {"name": "publicKey", "type": "string"},
                    {"name": "documentHash", "type": "string"}
                ],
                "name": "createIdentity",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "did", "type": "string"},
                    {"name": "newDocumentHash", "type": "string"}
                ],
                "name": "updateIdentity",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "did", "type": "string"}],
                "name": "revokeIdentity",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "did", "type": "string"}],
                "name": "getIdentity",
                "outputs": [
                    {"name": "", "type": "string"},
                    {"name": "", "type": "string"},
                    {"name": "", "type": "string"},
                    {"name": "", "type": "uint256"},
                    {"name": "", "type": "bool"},
                    {"name": "", "type": "address"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "did", "type": "string"},
                    {"indexed": True, "name": "owner", "type": "address"}
                ],
                "name": "IdentityCreated",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "did", "type": "string"}
                ],
                "name": "IdentityUpdated",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "did", "type": "string"}
                ],
                "name": "IdentityRevoked",
                "type": "event"
            }
        ]
    
    def register_did_on_ethereum(self, identity_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register DID on Ethereum blockchain
        
        Args:
            identity_package: PQIE identity package
            
        Returns:
            Transaction receipt
        """
        if not self.contract:
            raise ValueError("Contract not deployed or not connected")
        
        if not self.account:
            raise ValueError("Account required for transactions")
        
        # Prepare data for blockchain
        did = identity_package["did"]
        public_key = identity_package["signature_public_key"]
        document_hash = self._calculate_document_hash(identity_package)
        
        # Build transaction
        transaction = self.contract.functions.createIdentity(
            did, public_key, document_hash
        ).build_transaction({
            'from': self.account.address,
            'gas': self.gas_limit,
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })
        
        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for confirmation
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        result = {
            "transaction_hash": tx_hash.hex(),
            "block_number": tx_receipt.blockNumber,
            "gas_used": tx_receipt.gasUsed,
            "status": "success" if tx_receipt.status == 1 else "failed",
            "did": did,
            "contract_address": self.contract_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"✅ DID registered on Ethereum: {did}")
        print(f"📝 Transaction: {tx_hash.hex()}")
        print(f"⛽ Gas used: {tx_receipt.gasUsed}")
        
        return result
    
    def update_did_on_ethereum(self, did: str, updated_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update DID on Ethereum blockchain
        
        Args:
            did: Decentralized Identifier
            updated_package: Updated identity package
            
        Returns:
            Transaction receipt
        """
        if not self.contract:
            raise ValueError("Contract not deployed or not connected")
        
        if not self.account:
            raise ValueError("Account required for transactions")
        
        # Calculate new document hash
        document_hash = self._calculate_document_hash(updated_package)
        
        # Build transaction
        transaction = self.contract.functions.updateIdentity(
            did, document_hash
        ).build_transaction({
            'from': self.account.address,
            'gas': self.gas_limit,
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })
        
        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for confirmation
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        result = {
            "transaction_hash": tx_hash.hex(),
            "block_number": tx_receipt.blockNumber,
            "gas_used": tx_receipt.gasUsed,
            "status": "success" if tx_receipt.status == 1 else "failed",
            "did": did,
            "contract_address": self.contract_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"✅ DID updated on Ethereum: {did}")
        print(f"📝 Transaction: {tx_hash.hex()}")
        
        return result
    
    def revoke_did_on_ethereum(self, did: str) -> Dict[str, Any]:
        """
        Revoke DID on Ethereum blockchain
        
        Args:
            did: Decentralized Identifier
            
        Returns:
            Transaction receipt
        """
        if not self.contract:
            raise ValueError("Contract not deployed or not connected")
        
        if not self.account:
            raise ValueError("Account required for transactions")
        
        # Build transaction
        transaction = self.contract.functions.revokeIdentity(did).build_transaction({
            'from': self.account.address,
            'gas': self.gas_limit,
            'gasPrice': self.gas_price,
            'nonce': self.w3.eth.get_transaction_count(self.account.address)
        })
        
        # Sign and send transaction
        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for confirmation
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        result = {
            "transaction_hash": tx_hash.hex(),
            "block_number": tx_receipt.blockNumber,
            "gas_used": tx_receipt.gasUsed,
            "status": "success" if tx_receipt.status == 1 else "failed",
            "did": did,
            "contract_address": self.contract_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        print(f"✅ DID revoked on Ethereum: {did}")
        print(f"📝 Transaction: {tx_hash.hex()}")
        
        return result
    
    def get_did_from_ethereum(self, did: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve DID from Ethereum blockchain
        
        Args:
            did: Decentralized Identifier
            
        Returns:
            DID record or None
        """
        if not self.contract:
            raise ValueError("Contract not deployed or not connected")
        
        try:
            record = self.contract.functions.getIdentity(did).call()
            
            result = {
                "did": record[0],
                "public_key": record[1],
                "document_hash": record[2],
                "timestamp": record[3],
                "active": record[4],
                "owner": record[5],
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
            return result
            
        except Exception as e:
            print(f"❌ Error retrieving DID {did}: {e}")
            return None
    
    def _calculate_document_hash(self, identity_package: Dict[str, Any]) -> str:
        """
        Calculate hash of DID document for blockchain storage
        
        Args:
            identity_package: PQIE identity package
            
        Returns:
            Document hash
        """
        import hashlib
        
        # Extract relevant fields for hashing
        document_data = {
            "did": identity_package["did"],
            "did_document": identity_package["did_document"],
            "created_at": identity_package["created_at"],
            "expires_at": identity_package["expires_at"]
        }
        
        # Convert to JSON and hash
        document_json = json.dumps(document_data, sort_keys=True)
        document_hash = hashlib.sha256(document_json.encode()).hexdigest()
        
        return document_hash
    
    def get_ethereum_stats(self) -> Dict[str, Any]:
        """
        Get Ethereum blockchain statistics
        
        Returns:
            Blockchain statistics
        """
        if not self.w3.is_connected():
            return {"error": "Not connected to Ethereum"}
        
        try:
            latest_block = self.w3.eth.get_block('latest')
            gas_price = self.w3.eth.gas_price
            
            stats = {
                "connected": True,
                "latest_block": latest_block.number,
                "block_timestamp": latest_block.timestamp,
                "gas_price": gas_price,
                "gas_price_gwei": self.w3.from_wei(gas_price, 'gwei'),
                "network_id": self.w3.eth.chain_id,
                "contract_address": self.contract_address,
                "account_address": self.account.address if self.account else None,
                "account_balance": self.w3.eth.get_balance(self.account.address) if self.account else None
            }
            
            return stats
            
        except Exception as e:
            return {"error": str(e), "connected": False}

class EthereumPQIEFramework:
    """
    Enhanced PQIE Framework with Ethereum integration
    """
    
    def __init__(self, pqie_framework, ethereum_integration):
        self.pqie = pqie_framework
        self.ethereum = ethereum_integration
        
        print("🔐 Ethereum-PQIE Framework initialized")
    
    def generate_and_register_identity(self, user_attributes: Dict[str, Any], 
                                   user_identifier: str = None) -> Dict[str, Any]:
        """
        Generate identity and register on Ethereum
        
        Args:
            user_attributes: User identity attributes
            user_identifier: User identifier for tracking
            
        Returns:
            Complete identity package with Ethereum registration
        """
        # Generate PQIE identity package
        identity_package = self.pqie.generate_complete_identity_package(
            user_attributes, user_identifier, "ethereum"
        )
        
        # Register on Ethereum
        ethereum_result = self.ethereum.register_did_on_ethereum(identity_package)
        
        # Combine results
        complete_result = {
            "pqie_package": identity_package,
            "ethereum_registration": ethereum_result,
            "blockchain": "ethereum",
            "registered_at": datetime.utcnow().isoformat()
        }
        
        return complete_result
    
    def verify_ethereum_identity(self, did: str) -> Dict[str, Any]:
        """
        Verify identity from Ethereum blockchain
        
        Args:
            did: Decentralized Identifier
            
        Returns:
            Verification result
        """
        # Get DID from Ethereum
        ethereum_record = self.ethereum.get_did_from_ethereum(did)
        
        if not ethereum_record:
            return {"valid": False, "error": "DID not found on Ethereum"}
        
        # Verify with PQIE framework
        # Note: In practice, you'd need to reconstruct the package or store it off-chain
        verification = {
            "did": did,
            "ethereum_record": ethereum_record,
            "blockchain_verified": True,
            "active": ethereum_record["active"],
            "verified_at": datetime.utcnow().isoformat()
        }
        
        return verification
    
    def update_ethereum_identity(self, did: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update identity on Ethereum blockchain
        
        Args:
            did: Decentralized Identifier
            updates: Identity updates
            
        Returns:
            Update result
        """
        # Update with PQIE framework
        pqie_update = self.pqie.transaction_manager.update_did_document(
            did, updates, "ethereum"
        )
        
        # Update on Ethereum
        ethereum_update = self.ethereum.update_did_on_ethereum(did, pqie_update)
        
        return {
            "pqie_update": pqie_update,
            "ethereum_update": ethereum_update,
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def revoke_ethereum_identity(self, did: str, reason: str) -> Dict[str, Any]:
        """
        Revoke identity on Ethereum blockchain
        
        Args:
            did: Decentralized Identifier
            reason: Revocation reason
            
        Returns:
            Revocation result
        """
        # Revoke with PQIE framework
        pqie_revoke = self.pqie.transaction_manager.revoke_did_document(did, reason, "ethereum")
        
        # Revoke on Ethereum
        ethereum_revoke = self.ethereum.revoke_did_on_ethereum(did)
        
        return {
            "pqie_revoke": pqie_revoke,
            "ethereum_revoke": ethereum_revoke,
            "revoked_at": datetime.utcnow().isoformat(),
            "reason": reason
        }

# Usage example
if __name__ == "__main__":
    print("=== Ethereum PQIE Integration Testing ===")
    
    # Initialize Ethereum integration
    eth_integration = EthereumPQIEIntegration(
        web3_provider="http://localhost:8545",
        private_key="your_private_key_here"  # Replace with actual private key
    )
    
    # Deploy contract (if needed)
    # contract_address = eth_integration.deploy_pqie_contract(pqie_framework)
    
    # Get Ethereum stats
    stats = eth_integration.get_ethereum_stats()
    print(f"📊 Ethereum Stats: {stats}")
    
    print("🎉 Ethereum PQIE Integration ready!")
