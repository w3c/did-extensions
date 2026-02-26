#!/usr/bin/env python3
"""
Python wrapper for Rust Indy Core
Provides Python interface to the Rust-based Indy ledger implementation
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
from datetime import datetime

class IndyRustCore:
    """Python wrapper for Rust Indy Core"""
    
    def __init__(self, ledger_file: str):
        self.ledger_file = ledger_file
        self.rust_binary_path = Path(__file__).parent / 'rust_indy_core' / 'target' / 'release' / 'indy-rust-cli'
        self.rust_lib_path = Path(__file__).parent / 'rust_indy_core' / 'target' / 'release' / 'libindy_rust_core.dylib'
        
        # Ensure ledger file directory exists
        Path(ledger_file).parent.mkdir(parents=True, exist_ok=True)
        
        print(f"🔗 Rust Indy Core initialized")
        print(f"   Ledger file: {ledger_file}")
        print(f"   Rust binary: {self.rust_binary_path}")
        print(f"   Rust library: {self.rust_lib_path}")
        
        # Initialize fallback ledger with the SAME ledger file
        from rust_style_indy import RustStyleIndyLedger
        self.fallback_ledger = RustStyleIndyLedger(self.ledger_file)
        
        # Initialize a separate ledger for verifiable credentials
        self.credential_ledger_file = str(Path(self.ledger_file).parent / 'rust_vc_ledger.json')
        self.credential_ledger = RustStyleIndyLedger(self.credential_ledger_file)
    
    async def create_pool(self, pool_name: str, genesis_file: str) -> str:
        """Create Indy pool using Rust core"""
        try:
            if not self.rust_binary_path.exists():
                print(f"❌ Rust binary not found at {self.rust_binary_path}")
                return await self._fallback_create_pool(pool_name, genesis_file)
            
            # Use Rust CLI to create pool
            cmd = [
                str(self.rust_binary_path),
                'create-pool',
                '--name', pool_name,
                '--genesis-file', genesis_file
            ]
            
            result = await self._run_command(cmd)
            if result['success']:
                print(f"✅ Created pool using Rust core: {pool_name}")
                return pool_name
            else:
                print(f"❌ Failed to create pool: {result['error']}")
                return await self._fallback_create_pool(pool_name, genesis_file)
                
        except Exception as e:
            print(f"❌ Pool creation failed: {e}")
            return await self._fallback_create_pool(pool_name, genesis_file)
    
    async def create_wallet(self, wallet_name: str, wallet_key: str) -> str:
        """Create wallet using Rust core"""
        try:
            if not self.rust_binary_path.exists():
                print(f"❌ Rust binary not found at {self.rust_binary_path}")
                return await self._fallback_create_wallet(wallet_name, wallet_key)
            
            # Use Rust CLI to create wallet
            cmd = [
                str(self.rust_binary_path),
                'create-wallet',
                '--name', wallet_name,
                '--key', wallet_key
            ]
            
            result = await self._run_command(cmd)
            if result['success']:
                print(f"✅ Created wallet using Rust core: {wallet_name}")
                return wallet_name
            else:
                print(f"❌ Failed to create wallet: {result['error']}")
                return await self._fallback_create_wallet(wallet_name, wallet_key)
                
        except Exception as e:
            print(f"❌ Wallet creation failed: {e}")
            return await self._fallback_create_wallet(wallet_name, wallet_key)
    
    async def create_did(self, wallet_name: str, wallet_key: str, seed: Optional[str] = None) -> Dict[str, str]:
        """Create DID using Rust core"""
        try:
            if not self.rust_binary_path.exists():
                print(f"❌ Rust binary not found at {self.rust_binary_path}")
                return await self._fallback_create_did(wallet_name, wallet_key, seed)
            
            # Use Rust CLI to create DID
            cmd = [
                str(self.rust_binary_path),
                'create-did',
                '--wallet', wallet_name,
                '--key', wallet_key
            ]
            
            if seed:
                cmd.extend(['--seed', seed])
            
            result = await self._run_command(cmd)
            if result['success']:
                # Parse the JSON response
                try:
                    did_data = json.loads(result['output'])
                    print(f"✅ Created DID using Rust core: {did_data.get('did', 'unknown')}")
                    return did_data
                except json.JSONDecodeError:
                    print(f"❌ Failed to parse DID response: {result['output']}")
                    return await self._fallback_create_did(wallet_name, wallet_key, seed)
            else:
                print(f"❌ Failed to create DID: {result['error']}")
                return await self._fallback_create_did(wallet_name, wallet_key, seed)
                
        except Exception as e:
            print(f"❌ DID creation failed: {e}")
            return await self._fallback_create_did(wallet_name, wallet_key, seed)
    
    async def write_nym_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """Write NYM transaction using Rust core"""
        try:
            if not self.rust_binary_path.exists():
                print(f"❌ Rust binary not found at {self.rust_binary_path}")
                return await self._fallback_write_nym_transaction(transaction_data)
            
            # Use Rust CLI to write NYM transaction
            cmd = [
                str(self.rust_binary_path),
                'write-nym',
                '--transaction', json.dumps(transaction_data)
            ]
            
            result = await self._run_command(cmd)
            if result['success']:
                print(f"✅ Written NYM transaction using Rust core: {result['output'].strip()}")
                return result['output'].strip()
            else:
                print(f"❌ Failed to write NYM transaction: {result['error']}")
                return await self._fallback_write_nym_transaction(transaction_data)
                
        except Exception as e:
            print(f"❌ NYM transaction write failed: {e}")
            return await self._fallback_write_nym_transaction(transaction_data)
    
    async def write_credential_transaction(self, credential_data: Dict[str, Any]) -> str:
        """Write credential transaction using Rust core"""
        try:
            if not self.rust_binary_path.exists():
                print(f"❌ Rust binary not found at {self.rust_binary_path}")
                return await self._fallback_write_credential_transaction(credential_data)
            
            # Use Rust CLI to write credential transaction
            cmd = [
                str(self.rust_binary_path),
                'ledger', 'credential',
                json.dumps(credential_data)
            ]
            
            result = await self._run_command(cmd)
            if result['success']:
                # Parse the transaction ID from the output
                output = result['output'].strip()
                print(f"✅ Written credential transaction using Rust core: {output}")
                
                # Try to extract transaction ID from output
                # Format: "✅ Written credential transaction to Rust Indy ledger: rust_cred_xxxxx"
                import re
                match = re.search(r'rust_cred_[a-f0-9]+', output)
                if match:
                    return match.group(0)
                else:
                    # Fallback to extracting any ID-like string
                    match = re.search(r'(rust_\w+_[a-f0-9]+)', output)
                    if match:
                        return match.group(0)
                
                return output
            else:
                print(f"❌ Failed to write credential transaction: {result['error']}")
                return await self._fallback_write_credential_transaction(credential_data)
                
        except Exception as e:
            print(f"❌ Credential transaction write failed: {e}")
            return await self._fallback_write_credential_transaction(credential_data)
    
    async def verify_did(self, did: str) -> Dict[str, Any]:
        """Verify DID using Rust core"""
        try:
            if not self.rust_binary_path.exists():
                print(f"❌ Rust binary not found at {self.rust_binary_path}")
                return await self._fallback_verify_did(did)
            
            # Use Rust CLI to verify DID
            cmd = [
                str(self.rust_binary_path),
                'verify-did',
                '--did', did
            ]
            
            result = await self._run_command(cmd)
            if result['success']:
                try:
                    verification_data = json.loads(result['output'])
                    print(f"✅ Verified DID using Rust core: {did}")
                    return verification_data
                except json.JSONDecodeError:
                    print(f"❌ Failed to parse verification response: {result['output']}")
                    return await self._fallback_verify_did(did)
            else:
                print(f"❌ Failed to verify DID: {result['error']}")
                return await self._fallback_verify_did(did)
                
        except Exception as e:
            print(f"❌ DID verification failed: {e}")
            return await self._fallback_verify_did(did)
    
    async def get_ledger_stats(self) -> Dict[str, Any]:
        """Get ledger statistics using Rust core"""
        try:
            if not self.rust_binary_path.exists():
                print(f"❌ Rust binary not found at {self.rust_binary_path}")
                return await self._fallback_get_ledger_stats()
            
            # Use Rust CLI to get ledger stats
            cmd = [
                str(self.rust_binary_path),
                'stats'
            ]
            
            result = await self._run_command(cmd)
            if result['success']:
                try:
                    # The Rust CLI outputs the stats as JSON
                    stats_data = json.loads(result['output'])
                    print(f"✅ Retrieved ledger stats using Rust core")
                    return stats_data
                except json.JSONDecodeError:
                    print(f"❌ Failed to parse stats response: {result['output']}")
                    return await self._fallback_get_ledger_stats()
            else:
                print(f"❌ Failed to get ledger stats: {result['error']}")
                return await self._fallback_get_ledger_stats()
                
        except Exception as e:
            print(f"❌ Ledger stats retrieval failed: {e}")
            return await self._fallback_get_ledger_stats()
    
    async def get_ledger_data(self) -> Dict[str, Any]:
        """Get full ledger data by reading the ledger file directly"""
        try:
            # Read the ledger file directly
            if os.path.exists(self.ledger_file):
                with open(self.ledger_file, 'r') as f:
                    ledger_data = json.load(f)
                return ledger_data
            else:
                print(f"❌ Ledger file not found: {self.ledger_file}")
                return {}
        except Exception as e:
            print(f"❌ Failed to read ledger data: {e}")
            return {}
            
    async def get_credential_ledger_data(self) -> Dict[str, Any]:
        """Get full credential ledger data by reading the credential ledger file directly"""
        try:
            if os.path.exists(self.credential_ledger_file):
                with open(self.credential_ledger_file, 'r') as f:
                    return json.load(f)
            else:
                print(f"❌ Credential ledger file not found: {self.credential_ledger_file}")
                return {}
        except Exception as e:
            print(f"❌ Failed to read credential ledger data: {e}")
            return {}
    
    async def get_credential_by_id(self, credential_id: str) -> Dict[str, Any]:
        """Get credential by credential_id from Rust Indy ledger"""
        try:
            ledger_data = await self.get_credential_ledger_data()
            transactions = ledger_data.get('transactions', {})
            
            # Search through transactions to find credential
            for tx_id, tx in transactions.items():
                if tx.get('transaction_type') == 'CREDENTIAL':
                    tx_data = tx.get('data', {})
                    if tx_data.get('credential_id') == credential_id:
                        return {
                            'found': True,
                            'credential_id': credential_id,
                            'transaction_id': tx_id,
                            'transaction': tx,
                            'credential_data': tx_data,
                            'status': tx_data.get('status', 'UNKNOWN'),
                            'citizen_did': tx_data.get('citizen_did', ''),
                            'credential_type': tx_data.get('credential_type', '')
                        }
            
            return {'found': False, 'credential_id': credential_id}
        except Exception as e:
            print(f"❌ Failed to get credential by ID: {e}")
            return {'found': False, 'error': str(e)}
    
    async def get_credentials_by_did(self, citizen_did: str) -> Dict[str, Any]:
        """Get all credentials for a citizen DID from Rust Indy ledger"""
        try:
            ledger_data = await self.get_credential_ledger_data()
            transactions = ledger_data.get('transactions', {})
            
            credentials = []
            for tx_id, tx in transactions.items():
                if tx.get('transaction_type') == 'CREDENTIAL':
                    tx_data = tx.get('data', {})
                    if tx_data.get('citizen_did') == citizen_did:
                        credentials.append({
                            'credential_id': tx_data.get('credential_id'),
                            'transaction_id': tx_id,
                            'credential_type': tx_data.get('credential_type', ''),
                            'status': tx_data.get('status', 'UNKNOWN'),
                            'issued_at': tx_data.get('issued_at', ''),
                            'expires_at': tx_data.get('expires_at', ''),
                            'transaction': tx
                        })
            
            return {
                'found': True,
                'citizen_did': citizen_did,
                'credentials': credentials,
                'count': len(credentials)
            }
        except Exception as e:
            print(f"❌ Failed to get credentials by DID: {e}")
            return {'found': False, 'error': str(e)}
    
    async def revoke_credential(self, credential_id: str, reason: str = "Government revocation") -> Dict[str, Any]:
        """Revoke a credential by creating a revocation transaction in Rust Indy ledger"""
        try:
            # First, find the credential
            cred_info = await self.get_credential_by_id(credential_id)
            if not cred_info.get('found'):
                return {'success': False, 'error': 'Credential not found'}
            
            # Read current ledger
            ledger_data = await self.get_credential_ledger_data()
            if not ledger_data:
                return {'success': False, 'error': 'Failed to read credential ledger'}
            
            # Parse reason if it's JSON (contains revocation details)
            reason_code = 'VC_ADMINISTRATIVE'
            revocation_reason = reason
            additional_details = None
            
            try:
                if isinstance(reason, str) and reason.startswith('{'):
                    import json as json_module
                    reason_dict = json_module.loads(reason)
                    revocation_reason = reason_dict.get('reason', reason)
                    reason_code = reason_dict.get('reason_code', 'VC_ADMINISTRATIVE')
                    additional_details = reason_dict.get('additional_details')
            except:
                # If parsing fails, use reason as-is
                pass
            
            # Create revocation transaction
            revocation_data = {
                'transaction_type': 'CREDENTIAL_REVOCATION',
                'credential_id': credential_id,
                'citizen_did': cred_info.get('citizen_did', ''),
                'credential_type': cred_info.get('credential_type', ''),
                'revocation_reason': revocation_reason,
                'reason_code': reason_code,
                'additional_details': additional_details,
                'revoked_at': datetime.now().isoformat(),
                'original_transaction_id': cred_info.get('transaction_id')
            }
            
            # Generate transaction hash
            tx_data_str = json.dumps(revocation_data, sort_keys=True)
            import hashlib
            tx_hash = hashlib.sha256(tx_data_str.encode()).hexdigest()
            revocation_tx_id = f"rust_revoke_{tx_hash[:16]}"
            
            # Create transaction
            transactions = ledger_data.get('transactions', {})
            metadata = ledger_data.get('metadata', {})
            
            revocation_transaction = {
                'id': revocation_tx_id,
                'transaction_type': 'CREDENTIAL_REVOCATION',
                'data': revocation_data,
                'timestamp': datetime.now().isoformat() + 'Z',
                'hash': tx_hash,
                'status': 'COMMITTED',
                'seq_no': metadata.get('total_transactions', 0) + 1,
                'signature': None
            }
            
            # Update original credential transaction data to mark as revoked
            if cred_info.get('transaction_id') in transactions:
                transactions[cred_info['transaction_id']]['data']['status'] = 'REVOKED'
                transactions[cred_info['transaction_id']]['data']['revoked_at'] = revocation_data['revoked_at']
                transactions[cred_info['transaction_id']]['data']['revocation_reason'] = reason
            
            # Add revocation transaction
            transactions[revocation_tx_id] = revocation_transaction
            
            # Update metadata
            metadata['total_transactions'] = metadata.get('total_transactions', 0) + 1
            metadata['last_updated'] = datetime.now().isoformat() + 'Z'
            ledger_data['metadata'] = metadata
            ledger_data['transactions'] = transactions
            
            # Save ledger
            with open(self.credential_ledger_file, 'w') as f:
                json.dump(ledger_data, f, indent=2)
            
            print(f"✅ Credential revoked in Rust VC ledger: {credential_id}")
            
            return {
                'success': True,
                'credential_id': credential_id,
                'revocation_transaction_id': revocation_tx_id,
                'revoked_at': revocation_data['revoked_at'],
                'reason': reason
            }
            
        except Exception as e:
            print(f"❌ Failed to revoke credential: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    async def revoke_did(self, did: str, reason: str = "Administrative DID revocation") -> Dict[str, Any]:
        """Revoke a DID by creating a revocation transaction in Rust Indy ledger"""
        try:
            # Read current ledger
            ledger_data = await self.get_ledger_data()
            if not ledger_data:
                return {'success': False, 'error': 'Failed to read ledger'}
            
            # Create DID revocation transaction
            revocation_data = {
                'transaction_type': 'DID_REVOCATION',
                'did': did,
                'revocation_reason': reason,
                'revoked_at': datetime.now().isoformat(),
            }
            
            # Generate transaction hash
            tx_data_str = json.dumps(revocation_data, sort_keys=True)
            import hashlib
            tx_hash = hashlib.sha256(tx_data_str.encode()).hexdigest()
            revocation_tx_id = f"rust_did_revoke_{tx_hash[:16]}"
            
            # Create transaction
            transactions = ledger_data.get('transactions', {})
            metadata = ledger_data.get('metadata', {})
            
            revocation_transaction = {
                'id': revocation_tx_id,
                'transaction_type': 'DID_REVOCATION',
                'data': revocation_data,
                'timestamp': datetime.now().isoformat() + 'Z',
                'hash': tx_hash,
                'status': 'COMMITTED',
                'seq_no': metadata.get('total_transactions', 0) + 1,
                'signature': None
            }
            
            # Update all credentials for this DID to mark as revoked
            for tx_id, tx in transactions.items():
                if tx.get('transaction_type') == 'CREDENTIAL':
                    if tx.get('data', {}).get('citizen_did') == did:
                        tx['data']['status'] = 'REVOKED'
                        tx['data']['revocation_reason'] = f"DID Revoked: {reason}"
                        tx['data']['revoked_at'] = revocation_data['revoked_at']
            
            # Add revocation transaction
            transactions[revocation_tx_id] = revocation_transaction
            
            # Update metadata
            metadata['total_transactions'] = metadata.get('total_transactions', 0) + 1
            metadata['last_updated'] = datetime.now().isoformat() + 'Z'
            ledger_data['metadata'] = metadata
            ledger_data['transactions'] = transactions
            
            # Save ledger
            with open(self.ledger_file, 'w') as f:
                json.dump(ledger_data, f, indent=2)
            
            print(f"✅ DID revoked in Rust Indy ledger: {did}")
            
            return {
                'success': True,
                'did': did,
                'revocation_transaction_id': revocation_tx_id,
                'revoked_at': revocation_data['revoked_at'],
                'reason': reason
            }
        except Exception as e:
            print(f"❌ Failed to revoke DID: {e}")
            return {'success': False, 'error': str(e)}

    async def _run_command(self, cmd: list) -> Dict[str, Any]:
        """Run a command and return result"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path(__file__).parent
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                'success': process.returncode == 0,
                'output': stdout.decode('utf-8') if stdout else '',
                'error': stderr.decode('utf-8') if stderr else '',
                'returncode': process.returncode
            }
            
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'returncode': -1
            }
    
    # Fallback methods using rust_style_indy
    async def _fallback_create_pool(self, pool_name: str, genesis_file: str) -> str:
        """Fallback pool creation using local fallback ledger"""
        try:
            success = await self.fallback_ledger.create_pool(pool_name, genesis_file)
            return pool_name if success else f"fallback_pool_{pool_name}"
        except Exception as e:
            print(f"❌ Fallback pool creation failed: {e}")
            return f"fallback_pool_{pool_name}"
    
    async def _fallback_create_wallet(self, wallet_name: str, wallet_key: str) -> str:
        """Fallback wallet creation using local fallback ledger"""
        try:
            success = await self.fallback_ledger.create_wallet(wallet_name, wallet_key)
            return wallet_name if success else f"fallback_wallet_{wallet_name}"
        except Exception as e:
            print(f"❌ Fallback wallet creation failed: {e}")
            return f"fallback_wallet_{wallet_name}"
    
    async def _fallback_create_did(self, wallet_name: str, wallet_key: str, seed: Optional[str] = None) -> Dict[str, str]:
        """Fallback DID creation using local fallback ledger"""
        try:
            result = await self.fallback_ledger.create_did(wallet_name, wallet_key, seed)
            return result if result else {"did": f"fallback_did_{wallet_name}", "verkey": f"fallback_verkey_{wallet_name}"}
        except Exception as e:
            print(f"❌ Fallback DID creation failed: {e}")
            return {"did": f"fallback_did_{wallet_name}", "verkey": f"fallback_verkey_{wallet_name}"}
    
    async def _fallback_write_nym_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """Fallback NYM transaction using local fallback ledger"""
        try:
            result = await self.fallback_ledger.write_nym_transaction(transaction_data)
            return result if result else f"fallback_nym_{hash(str(transaction_data))}"
        except Exception as e:
            print(f"❌ Fallback NYM transaction failed: {e}")
            return f"fallback_nym_{hash(str(transaction_data))}"
    
    async def _fallback_write_credential_transaction(self, credential_data: Dict[str, Any]) -> str:
        """Fallback credential transaction using local fallback ledger"""
        try:
            result = await self.credential_ledger.write_credential_transaction(credential_data)
            return result if result else f"fallback_cred_{hash(str(credential_data))}"
        except Exception as e:
            print(f"❌ Fallback credential transaction failed: {e}")
            return f"fallback_cred_{hash(str(credential_data))}"
    
    async def _fallback_verify_did(self, did: str) -> Dict[str, Any]:
        """Fallback DID verification using local fallback ledger"""
        try:
            result = await self.fallback_ledger.verify_did(did)
            return result if result else {"verified": False, "error": "Fallback verification failed"}
        except Exception as e:
            print(f"❌ Fallback DID verification failed: {e}")
            return {"verified": False, "error": str(e)}
    
    async def _fallback_get_ledger_stats(self) -> Dict[str, Any]:
        """Fallback ledger stats using local fallback ledger"""
        try:
            result = self.fallback_ledger.get_ledger_stats()
            return result if result else {"error": "Fallback stats failed"}
        except Exception as e:
            print(f"❌ Fallback ledger stats failed: {e}")
            return {"error": str(e)}

# Test the implementation
if __name__ == "__main__":
    async def test_rust_core():
        print("🧪 Testing Rust Indy Core Integration")
        print("=" * 50)
        
        # Initialize Rust core
        ledger_file = "data/test_rust_ledger.json"
        rust_core = IndyRustCore(ledger_file)
        
        # Test pool creation
        print("\n1. Testing pool creation...")
        pool_result = await rust_core.create_pool("test_pool", "test_genesis.txn")
        print(f"✅ Pool creation result: {pool_result}")
        
        # Test wallet creation
        print("\n2. Testing wallet creation...")
        wallet_result = await rust_core.create_wallet("test_wallet", "test_key")
        print(f"✅ Wallet creation result: {wallet_result}")
        
        # Test DID creation
        print("\n3. Testing DID creation...")
        did_result = await rust_core.create_did("test_wallet", "test_key", "test_seed")
        print(f"✅ DID creation result: {did_result}")
        
        # Test NYM transaction
        if did_result and 'did' in did_result:
            print("\n4. Testing NYM transaction...")
            nym_data = {
                "dest": did_result['did'],
                "verkey": did_result.get('verkey', '~test_verkey'),
                "role": "TRUST_ANCHOR"
            }
            nym_result = await rust_core.write_nym_transaction(nym_data)
            print(f"✅ NYM transaction result: {nym_result}")
            
            # Test DID verification
            print("\n5. Testing DID verification...")
            verify_result = await rust_core.verify_did(did_result['did'])
            print(f"✅ DID verification result: {verify_result}")
        
        # Test ledger stats
        print("\n6. Testing ledger stats...")
        stats_result = await rust_core.get_ledger_stats()
        print(f"✅ Ledger stats result: {stats_result}")
        
        print("\n🎉 Rust Indy Core integration test completed!")
    
    asyncio.run(test_rust_core())
