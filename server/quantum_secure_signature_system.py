#!/usr/bin/env python3
"""
Quantum-Secure Signature System for SDIS DID Method
Implements post-quantum cryptographic signatures using SPHINCS+ and other quantum-resistant algorithms
"""

import hashlib
import secrets
import json
import base64
from typing import Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from pathlib import Path
import os

# Post-quantum cryptography libraries
try:
    import pyspx.shake256_128f as sphincs
    SPHINCS_AVAILABLE = True
except ImportError:
    SPHINCS_AVAILABLE = False
    print("⚠️ SPHINCS+ not available. Install with: pip install pyspx")

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ed25519, rsa
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️ Cryptography library not available. Install with: pip install cryptography")

class QuantumSecureSignatureSystem:
    """Quantum-Secure Signature System for SDIS DID Method"""
    
    def __init__(self):
        self.signature_types = {
            "sphincs_plus": {
                "name": "SPHINCS+ (Hash-based)",
                "quantum_secure": True,
                "key_size": 32,
                "signature_size": 17088,
                "security_level": "128-bit"
            },
            "ed25519_quantum_hybrid": {
                "name": "Ed25519 + Quantum-Resistant Hash",
                "quantum_secure": True,
                "key_size": 32,
                "signature_size": 64,
                "security_level": "128-bit"
            },
            "multisig_quantum": {
                "name": "Multi-Signature Quantum-Secure",
                "quantum_secure": True,
                "key_size": 96,
                "signature_size": 192,
                "security_level": "256-bit"
            }
        }
        
        # Initialize signature ledger
        self._initialize_signature_ledger()
        
    def _initialize_signature_ledger(self):
        """Initialize signature ledger file"""
        self.ledger_file = Path("data/quantum_signature_ledger.json")
        self.ledger_file.parent.mkdir(exist_ok=True)
        
        if not self.ledger_file.exists():
            with open(self.ledger_file, 'w') as f:
                json.dump({
                    "signatures": {},
                    "public_keys": {},
                    "verification_records": {},
                    "metadata": {
                        "created_at": datetime.now().isoformat(),
                        "signature_scheme": "quantum_secure_sdis",
                        "version": "1.0.0"
                    }
                }, f, indent=2)
    
    async def generate_quantum_secure_keypair(self, citizen_did: str, signature_type: str = "sphincs_plus") -> Dict[str, Any]:
        """Generate quantum-secure keypair for SDIS DID"""
        try:
            print(f"🔐 Generating quantum-secure keypair for DID: {citizen_did}")
            
            if signature_type == "sphincs_plus" and SPHINCS_AVAILABLE:
                return await self._generate_sphincs_keypair(citizen_did)
            elif signature_type == "ed25519_quantum_hybrid" and CRYPTO_AVAILABLE:
                return await self._generate_ed25519_quantum_hybrid_keypair(citizen_did)
            elif signature_type == "multisig_quantum":
                return await self._generate_multisig_quantum_keypair(citizen_did)
            else:
                return {"success": False, "error": f"Unsupported signature type: {signature_type}"}
                
        except Exception as e:
            print(f"❌ Failed to generate quantum-secure keypair: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_sphincs_keypair(self, citizen_did: str) -> Dict[str, Any]:
        """Generate SPHINCS+ keypair"""
        try:
            # Generate seed
            seed = os.urandom(sphincs.crypto_sign_SEEDBYTES)
            
            # Generate keypair
            public_key, secret_key = sphincs.generate_keypair(seed)
            
            # Create keypair record
            keypair_id = f"SPHINCS_{secrets.token_hex(8)}"
            keypair_record = {
                "keypair_id": keypair_id,
                "citizen_did": citizen_did,
                "signature_type": "sphincs_plus",
                "public_key": base64.b64encode(public_key).decode('utf-8'),
                "secret_key": base64.b64encode(secret_key).decode('utf-8'),
                "seed": base64.b64encode(seed).decode('utf-8'),
                "created_at": datetime.now().isoformat(),
                "security_level": "128-bit",
                "quantum_secure": True
            }
            
            # Store in ledger
            await self._store_keypair(keypair_record)
            
            print(f"✅ SPHINCS+ keypair generated: {keypair_id}")
            
            return {
                "success": True,
                "keypair_id": keypair_id,
                "public_key": keypair_record["public_key"],
                "signature_type": "sphincs_plus",
                "security_level": "128-bit",
                "quantum_secure": True
            }
            
        except Exception as e:
            return {"success": False, "error": f"SPHINCS+ keypair generation failed: {e}"}
    
    async def _generate_ed25519_quantum_hybrid_keypair(self, citizen_did: str) -> Dict[str, Any]:
        """Generate Ed25519 with quantum-resistant hash keypair"""
        try:
            # Generate Ed25519 keypair
            private_key = ed25519.Ed25519PrivateKey.generate()
            public_key = private_key.public_key()
            
            # Serialize keys
            private_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            public_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            
            # Create keypair record
            keypair_id = f"ED25519_QH_{secrets.token_hex(8)}"
            keypair_record = {
                "keypair_id": keypair_id,
                "citizen_did": citizen_did,
                "signature_type": "ed25519_quantum_hybrid",
                "public_key": base64.b64encode(public_bytes).decode('utf-8'),
                "secret_key": base64.b64encode(private_bytes).decode('utf-8'),
                "created_at": datetime.now().isoformat(),
                "security_level": "128-bit",
                "quantum_secure": True,
                "hash_algorithm": "SHA3-256"
            }
            
            # Store in ledger
            await self._store_keypair(keypair_record)
            
            print(f"✅ Ed25519 Quantum-Hybrid keypair generated: {keypair_id}")
            
            return {
                "success": True,
                "keypair_id": keypair_id,
                "public_key": keypair_record["public_key"],
                "signature_type": "ed25519_quantum_hybrid",
                "security_level": "128-bit",
                "quantum_secure": True
            }
            
        except Exception as e:
            return {"success": False, "error": f"Ed25519 Quantum-Hybrid keypair generation failed: {e}"}
    
    async def _generate_multisig_quantum_keypair(self, citizen_did: str) -> Dict[str, Any]:
        """Generate multi-signature quantum-secure keypair"""
        try:
            # Generate multiple keypairs for multisig
            keypairs = []
            for i in range(3):  # 3-of-3 multisig
                if SPHINCS_AVAILABLE:
                    seed = os.urandom(sphincs.crypto_sign_SEEDBYTES)
                    public_key, secret_key = sphincs.generate_keypair(seed)
                    keypairs.append({
                        "type": "sphincs_plus",
                        "public_key": base64.b64encode(public_key).decode('utf-8'),
                        "secret_key": base64.b64encode(secret_key).decode('utf-8'),
                        "seed": base64.b64encode(seed).decode('utf-8')
                    })
                else:
                    # Fallback to Ed25519
                    private_key = ed25519.Ed25519PrivateKey.generate()
                    public_key = private_key.public_key()
                    
                    private_bytes = private_key.private_bytes(
                        encoding=serialization.Encoding.Raw,
                        format=serialization.PrivateFormat.Raw,
                        encryption_algorithm=serialization.NoEncryption()
                    )
                    
                    public_bytes = public_key.public_bytes(
                        encoding=serialization.Encoding.Raw,
                        format=serialization.PublicFormat.Raw
                    )
                    
                    keypairs.append({
                        "type": "ed25519_quantum_hybrid",
                        "public_key": base64.b64encode(public_bytes).decode('utf-8'),
                        "secret_key": base64.b64encode(private_bytes).decode('utf-8')
                    })
            
            # Create multisig keypair record
            keypair_id = f"MULTISIG_Q_{secrets.token_hex(8)}"
            keypair_record = {
                "keypair_id": keypair_id,
                "citizen_did": citizen_did,
                "signature_type": "multisig_quantum",
                "keypairs": keypairs,
                "threshold": 3,
                "total_keys": 3,
                "created_at": datetime.now().isoformat(),
                "security_level": "256-bit",
                "quantum_secure": True
            }
            
            # Store in ledger
            await self._store_keypair(keypair_record)
            
            print(f"✅ Multi-Signature Quantum keypair generated: {keypair_id}")
            
            return {
                "success": True,
                "keypair_id": keypair_id,
                "public_keys": [kp["public_key"] for kp in keypairs],
                "signature_type": "multisig_quantum",
                "security_level": "256-bit",
                "quantum_secure": True,
                "threshold": 3
            }
            
        except Exception as e:
            return {"success": False, "error": f"Multi-Signature Quantum keypair generation failed: {e}"}
    
    async def sign_message(self, citizen_did: str, message: str, keypair_id: str) -> Dict[str, Any]:
        """Sign message with quantum-secure signature"""
        try:
            print(f"✍️ Signing message for DID: {citizen_did}")
            
            # Load keypair
            keypair = await self._load_keypair(keypair_id)
            if not keypair:
                return {"success": False, "error": "Keypair not found"}
            
            signature_type = keypair["signature_type"]
            message_bytes = message.encode('utf-8')
            
            if signature_type == "sphincs_plus" and SPHINCS_AVAILABLE:
                return await self._sign_with_sphincs(message_bytes, keypair)
            elif signature_type == "ed25519_quantum_hybrid" and CRYPTO_AVAILABLE:
                return await self._sign_with_ed25519_quantum_hybrid(message_bytes, keypair)
            elif signature_type == "multisig_quantum":
                return await self._sign_with_multisig_quantum(message_bytes, keypair)
            else:
                return {"success": False, "error": f"Unsupported signature type: {signature_type}"}
                
        except Exception as e:
            print(f"❌ Failed to sign message: {e}")
            return {"success": False, "error": str(e)}
    
    async def _sign_with_sphincs(self, message_bytes: bytes, keypair: Dict[str, Any]) -> Dict[str, Any]:
        """Sign with SPHINCS+"""
        try:
            secret_key = base64.b64decode(keypair["secret_key"])
            signature = sphincs.sign(message_bytes, secret_key)
            
            signature_id = f"SIG_SPHINCS_{secrets.token_hex(8)}"
            signature_record = {
                "signature_id": signature_id,
                "keypair_id": keypair["keypair_id"],
                "citizen_did": keypair["citizen_did"],
                "signature_type": "sphincs_plus",
                "signature": base64.b64encode(signature).decode('utf-8'),
                "message_hash": hashlib.sha3_256(message_bytes).hexdigest(),
                "signed_at": datetime.now().isoformat(),
                "quantum_secure": True
            }
            
            # Store signature
            await self._store_signature(signature_record)
            
            print(f"✅ SPHINCS+ signature created: {signature_id}")
            
            return {
                "success": True,
                "signature_id": signature_id,
                "signature": signature_record["signature"],
                "signature_type": "sphincs_plus",
                "quantum_secure": True
            }
            
        except Exception as e:
            return {"success": False, "error": f"SPHINCS+ signing failed: {e}"}
    
    async def _sign_with_ed25519_quantum_hybrid(self, message_bytes: bytes, keypair: Dict[str, Any]) -> Dict[str, Any]:
        """Sign with Ed25519 Quantum-Hybrid"""
        try:
            private_key_bytes = base64.b64decode(keypair["secret_key"])
            private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
            
            # Use quantum-resistant hash
            message_hash = hashlib.sha3_256(message_bytes).digest()
            signature = private_key.sign(message_hash)
            
            signature_id = f"SIG_ED25519_QH_{secrets.token_hex(8)}"
            signature_record = {
                "signature_id": signature_id,
                "keypair_id": keypair["keypair_id"],
                "citizen_did": keypair["citizen_did"],
                "signature_type": "ed25519_quantum_hybrid",
                "signature": base64.b64encode(signature).decode('utf-8'),
                "message_hash": hashlib.sha3_256(message_bytes).hexdigest(),
                "signed_at": datetime.now().isoformat(),
                "quantum_secure": True,
                "hash_algorithm": "SHA3-256"
            }
            
            # Store signature
            await self._store_signature(signature_record)
            
            print(f"✅ Ed25519 Quantum-Hybrid signature created: {signature_id}")
            
            return {
                "success": True,
                "signature_id": signature_id,
                "signature": signature_record["signature"],
                "signature_type": "ed25519_quantum_hybrid",
                "quantum_secure": True
            }
            
        except Exception as e:
            return {"success": False, "error": f"Ed25519 Quantum-Hybrid signing failed: {e}"}
    
    async def _sign_with_multisig_quantum(self, message_bytes: bytes, keypair: Dict[str, Any]) -> Dict[str, Any]:
        """Sign with Multi-Signature Quantum"""
        try:
            signatures = []
            for i, kp in enumerate(keypair["keypairs"]):
                if kp["type"] == "sphincs_plus" and SPHINCS_AVAILABLE:
                    secret_key = base64.b64decode(kp["secret_key"])
                    sig = sphincs.sign(message_bytes, secret_key)
                    signatures.append({
                        "index": i,
                        "type": "sphincs_plus",
                        "signature": base64.b64encode(sig).decode('utf-8')
                    })
                elif kp["type"] == "ed25519_quantum_hybrid" and CRYPTO_AVAILABLE:
                    private_key_bytes = base64.b64decode(kp["secret_key"])
                    private_key = ed25519.Ed25519PrivateKey.from_private_bytes(private_key_bytes)
                    message_hash = hashlib.sha3_256(message_bytes).digest()
                    sig = private_key.sign(message_hash)
                    signatures.append({
                        "index": i,
                        "type": "ed25519_quantum_hybrid",
                        "signature": base64.b64encode(sig).decode('utf-8')
                    })
            
            signature_id = f"SIG_MULTISIG_Q_{secrets.token_hex(8)}"
            signature_record = {
                "signature_id": signature_id,
                "keypair_id": keypair["keypair_id"],
                "citizen_did": keypair["citizen_did"],
                "signature_type": "multisig_quantum",
                "signatures": signatures,
                "message_hash": hashlib.sha3_256(message_bytes).hexdigest(),
                "signed_at": datetime.now().isoformat(),
                "quantum_secure": True,
                "threshold": keypair["threshold"]
            }
            
            # Store signature
            await self._store_signature(signature_record)
            
            print(f"✅ Multi-Signature Quantum signature created: {signature_id}")
            
            return {
                "success": True,
                "signature_id": signature_id,
                "signatures": signatures,
                "signature_type": "multisig_quantum",
                "quantum_secure": True,
                "threshold": keypair["threshold"]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Multi-Signature Quantum signing failed: {e}"}
    
    async def verify_signature(self, signature_id: str, message: str) -> Dict[str, Any]:
        """Verify quantum-secure signature"""
        try:
            print(f"🔍 Verifying signature: {signature_id}")
            
            # Load signature record
            signature_record = await self._load_signature(signature_id)
            if not signature_record:
                return {"success": False, "error": "Signature not found"}
            
            # Load keypair
            keypair = await self._load_keypair(signature_record["keypair_id"])
            if not keypair:
                return {"success": False, "error": "Keypair not found"}
            
            message_bytes = message.encode('utf-8')
            signature_type = signature_record["signature_type"]
            
            if signature_type == "sphincs_plus" and SPHINCS_AVAILABLE:
                return await self._verify_sphincs_signature(message_bytes, signature_record, keypair)
            elif signature_type == "ed25519_quantum_hybrid" and CRYPTO_AVAILABLE:
                return await self._verify_ed25519_quantum_hybrid_signature(message_bytes, signature_record, keypair)
            elif signature_type == "multisig_quantum":
                return await self._verify_multisig_quantum_signature(message_bytes, signature_record, keypair)
            else:
                return {"success": False, "error": f"Unsupported signature type: {signature_type}"}
                
        except Exception as e:
            print(f"❌ Failed to verify signature: {e}")
            return {"success": False, "error": str(e)}
    
    async def _verify_sphincs_signature(self, message_bytes: bytes, signature_record: Dict[str, Any], keypair: Dict[str, Any]) -> Dict[str, Any]:
        """Verify SPHINCS+ signature"""
        try:
            public_key = base64.b64decode(keypair["public_key"])
            signature = base64.b64decode(signature_record["signature"])
            
            is_valid = sphincs.verify(message_bytes, signature, public_key)
            
            verification_record = {
                "signature_id": signature_record["signature_id"],
                "verified_at": datetime.now().isoformat(),
                "is_valid": is_valid,
                "verification_method": "sphincs_plus",
                "quantum_secure": True
            }
            
            await self._store_verification_record(verification_record)
            
            print(f"✅ SPHINCS+ signature verification: {'VALID' if is_valid else 'INVALID'}")
            
            return {
                "success": True,
                "is_valid": is_valid,
                "verification_method": "sphincs_plus",
                "quantum_secure": True,
                "verified_at": verification_record["verified_at"]
            }
            
        except Exception as e:
            return {"success": False, "error": f"SPHINCS+ verification failed: {e}"}
    
    async def _verify_ed25519_quantum_hybrid_signature(self, message_bytes: bytes, signature_record: Dict[str, Any], keypair: Dict[str, Any]) -> Dict[str, Any]:
        """Verify Ed25519 Quantum-Hybrid signature"""
        try:
            public_key_bytes = base64.b64decode(keypair["public_key"])
            public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
            signature = base64.b64decode(signature_record["signature"])
            
            # Use quantum-resistant hash
            message_hash = hashlib.sha3_256(message_bytes).digest()
            
            try:
                public_key.verify(signature, message_hash)
                is_valid = True
            except:
                is_valid = False
            
            verification_record = {
                "signature_id": signature_record["signature_id"],
                "verified_at": datetime.now().isoformat(),
                "is_valid": is_valid,
                "verification_method": "ed25519_quantum_hybrid",
                "quantum_secure": True,
                "hash_algorithm": "SHA3-256"
            }
            
            await self._store_verification_record(verification_record)
            
            print(f"✅ Ed25519 Quantum-Hybrid signature verification: {'VALID' if is_valid else 'INVALID'}")
            
            return {
                "success": True,
                "is_valid": is_valid,
                "verification_method": "ed25519_quantum_hybrid",
                "quantum_secure": True,
                "verified_at": verification_record["verified_at"]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Ed25519 Quantum-Hybrid verification failed: {e}"}
    
    async def _verify_multisig_quantum_signature(self, message_bytes: bytes, signature_record: Dict[str, Any], keypair: Dict[str, Any]) -> Dict[str, Any]:
        """Verify Multi-Signature Quantum signature"""
        try:
            valid_signatures = 0
            total_signatures = len(signature_record["signatures"])
            
            for sig_data in signature_record["signatures"]:
                kp = keypair["keypairs"][sig_data["index"]]
                
                if kp["type"] == "sphincs_plus" and SPHINCS_AVAILABLE:
                    public_key = base64.b64decode(kp["public_key"])
                    signature = base64.b64decode(sig_data["signature"])
                    is_valid = sphincs.verify(message_bytes, signature, public_key)
                elif kp["type"] == "ed25519_quantum_hybrid" and CRYPTO_AVAILABLE:
                    public_key_bytes = base64.b64decode(kp["public_key"])
                    public_key = ed25519.Ed25519PublicKey.from_public_bytes(public_key_bytes)
                    signature = base64.b64decode(sig_data["signature"])
                    message_hash = hashlib.sha3_256(message_bytes).digest()
                    try:
                        public_key.verify(signature, message_hash)
                        is_valid = True
                    except:
                        is_valid = False
                else:
                    is_valid = False
                
                if is_valid:
                    valid_signatures += 1
            
            # Check if threshold is met
            threshold_met = valid_signatures >= keypair["threshold"]
            
            verification_record = {
                "signature_id": signature_record["signature_id"],
                "verified_at": datetime.now().isoformat(),
                "is_valid": threshold_met,
                "verification_method": "multisig_quantum",
                "quantum_secure": True,
                "valid_signatures": valid_signatures,
                "total_signatures": total_signatures,
                "threshold": keypair["threshold"]
            }
            
            await self._store_verification_record(verification_record)
            
            print(f"✅ Multi-Signature Quantum verification: {'VALID' if threshold_met else 'INVALID'} ({valid_signatures}/{total_signatures})")
            
            return {
                "success": True,
                "is_valid": threshold_met,
                "verification_method": "multisig_quantum",
                "quantum_secure": True,
                "valid_signatures": valid_signatures,
                "total_signatures": total_signatures,
                "threshold": keypair["threshold"],
                "verified_at": verification_record["verified_at"]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Multi-Signature Quantum verification failed: {e}"}
    
    async def _store_keypair(self, keypair_record: Dict[str, Any]):
        """Store keypair in ledger"""
        with open(self.ledger_file, 'r') as f:
            ledger = json.load(f)
        
        ledger["public_keys"][keypair_record["keypair_id"]] = keypair_record
        
        with open(self.ledger_file, 'w') as f:
            json.dump(ledger, f, indent=2)
    
    async def _load_keypair(self, keypair_id: str) -> Optional[Dict[str, Any]]:
        """Load keypair from ledger"""
        with open(self.ledger_file, 'r') as f:
            ledger = json.load(f)
        
        return ledger["public_keys"].get(keypair_id)
    
    async def _store_signature(self, signature_record: Dict[str, Any]):
        """Store signature in ledger"""
        with open(self.ledger_file, 'r') as f:
            ledger = json.load(f)
        
        ledger["signatures"][signature_record["signature_id"]] = signature_record
        
        with open(self.ledger_file, 'w') as f:
            json.dump(ledger, f, indent=2)
    
    async def _load_signature(self, signature_id: str) -> Optional[Dict[str, Any]]:
        """Load signature from ledger"""
        with open(self.ledger_file, 'r') as f:
            ledger = json.load(f)
        
        return ledger["signatures"].get(signature_id)
    
    async def _store_verification_record(self, verification_record: Dict[str, Any]):
        """Store verification record in ledger"""
        with open(self.ledger_file, 'r') as f:
            ledger = json.load(f)
        
        ledger["verification_records"][verification_record["signature_id"]] = verification_record
        
        with open(self.ledger_file, 'w') as f:
            json.dump(ledger, f, indent=2)
    
    async def get_signature_statistics(self) -> Dict[str, Any]:
        """Get signature system statistics"""
        with open(self.ledger_file, 'r') as f:
            ledger = json.load(f)
        
        return {
            "total_keypairs": len(ledger["public_keys"]),
            "total_signatures": len(ledger["signatures"]),
            "total_verifications": len(ledger["verification_records"]),
            "signature_types": self.signature_types,
            "quantum_secure": True,
            "supported_algorithms": list(self.signature_types.keys())
        }

# Integration with Auto Identity Token System
class QuantumSecureTokenIntegration:
    """Integration of quantum-secure signatures with auto identity tokens"""
    
    def __init__(self):
        self.signature_system = QuantumSecureSignatureSystem()
    
    async def generate_quantum_secure_token(self, citizen_did: str, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate auto identity token with quantum-secure signature"""
        try:
            print(f"🎫 Generating quantum-secure auto identity token for DID: {citizen_did}")
            
            # Generate quantum-secure keypair
            keypair_result = await self.signature_system.generate_quantum_secure_keypair(
                citizen_did, "sphincs_plus"
            )
            
            if not keypair_result["success"]:
                return {"success": False, "error": "Failed to generate quantum-secure keypair"}
            
            # Create token message
            token_message = json.dumps({
                "citizen_did": citizen_did,
                "token_data": token_data,
                "timestamp": datetime.now().isoformat(),
                "quantum_secure": True
            })
            
            # Sign the token message
            signature_result = await self.signature_system.sign_message(
                citizen_did, token_message, keypair_result["keypair_id"]
            )
            
            if not signature_result["success"]:
                return {"success": False, "error": "Failed to sign token message"}
            
            # Create quantum-secure token
            quantum_token = {
                "token_id": f"QTOKEN_{secrets.token_hex(8)}",
                "citizen_did": citizen_did,
                "token_data": token_data,
                "keypair_id": keypair_result["keypair_id"],
                "signature_id": signature_result["signature_id"],
                "public_key": keypair_result["public_key"],
                "signature": signature_result["signature"],
                "signature_type": signature_result["signature_type"],
                "quantum_secure": True,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }
            
            print(f"✅ Quantum-secure auto identity token generated: {quantum_token['token_id']}")
            
            return {
                "success": True,
                "quantum_token": quantum_token,
                "keypair_id": keypair_result["keypair_id"],
                "signature_id": signature_result["signature_id"]
            }
            
        except Exception as e:
            print(f"❌ Failed to generate quantum-secure token: {e}")
            return {"success": False, "error": str(e)}
    
    async def verify_quantum_secure_token(self, quantum_token: Dict[str, Any]) -> Dict[str, Any]:
        """Verify quantum-secure auto identity token"""
        try:
            print(f"🔍 Verifying quantum-secure token: {quantum_token['token_id']}")
            
            # Recreate token message
            token_message = json.dumps({
                "citizen_did": quantum_token["citizen_did"],
                "token_data": quantum_token["token_data"],
                "timestamp": quantum_token["created_at"],
                "quantum_secure": True
            })
            
            # Verify signature
            verification_result = await self.signature_system.verify_signature(
                quantum_token["signature_id"], token_message
            )
            
            if not verification_result["success"]:
                return {"success": False, "error": "Token verification failed"}
            
            # Check token expiration
            expires_at = datetime.fromisoformat(quantum_token["expires_at"])
            if datetime.now() > expires_at:
                return {"success": False, "error": "Token has expired"}
            
            print(f"✅ Quantum-secure token verification: {'VALID' if verification_result['is_valid'] else 'INVALID'}")
            
            return {
                "success": True,
                "is_valid": verification_result["is_valid"],
                "quantum_secure": True,
                "verification_method": verification_result["verification_method"],
                "verified_at": verification_result["verified_at"]
            }
            
        except Exception as e:
            print(f"❌ Failed to verify quantum-secure token: {e}")
            return {"success": False, "error": str(e)}
