
import sys
import os
from pathlib import Path

# Add project root and server to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'server'))

try:
    from server.pqie_framework import PQIECryptoEngine, PQIETokenGenerator, PQIETransactionManager
    print("✅ PQIE Framework imported successfully")
    
    crypto = PQIECryptoEngine()
    token_gen = PQIETokenGenerator(crypto)
    tx_manager = PQIETransactionManager(crypto, token_gen)
    print("✅ PQIE Components initialized")
    
    # Test DID suffix generation
    attributes = {"name": "Test", "email": "test@example.com"}
    tx = tx_manager.issue_did_document(attributes)
    print(f"✅ PQIE DID generated: {tx['did']}")
    
except Exception as e:
    print(f"❌ PQIE Verification failed: {e}")
    import traceback
    traceback.print_exc()
