#!/usr/bin/env python3
"""
DID Document Updater
Periodically updates DID documents on IPFS with current credential status
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from ipfs_util import upload_json_to_ipfs, is_ipfs_available, get_ipfs_link
from rust_indy_core import IndyRustCore


class DIDDocumentUpdater:
    """Updates DID documents on IPFS with current credential information"""
    
    def __init__(self):
        self.ledger_file = Path(__file__).parent.parent / 'data' / 'rust_indy_core_ledger.json'
        self.did_documents_file = Path(__file__).parent.parent / 'data' / 'did_documents.json'
        
    async def update_did_document_on_ipfs(self, citizen_did: str, force_update: bool = False) -> Dict[str, Any]:
        """
        Update DID document on IPFS with current credential status
        
        Args:
            citizen_did: The citizen's DID
            force_update: Force update even if recently updated
            
        Returns:
            Dict with update status, new IPFS CID, and document
        """
        try:
            print(f"🔄 Updating DID document on IPFS for: {citizen_did}")
            
            # Load current DID document from storage
            did_doc_data = await self._load_did_document(citizen_did)
            if not did_doc_data:
                print(f"⚠️ DID document not found for: {citizen_did}")
                return {'success': False, 'error': 'DID document not found'}
            
            # Check if update is needed (not force update and recently updated)
            if not force_update and self._is_recently_updated(did_doc_data):
                print(f"✅ DID document recently updated, skipping")
                return {
                    'success': True,
                    'skipped': True,
                    'reason': 'Recently updated',
                    'ipfs_cid': did_doc_data.get('ipfs_cid'),
                    'ipfs_url': did_doc_data.get('ipfs_url')
                }
            
            # Get current credentials from Rust Indy ledger
            rust_core = IndyRustCore(str(self.ledger_file))
            creds_result = await rust_core.get_credentials_by_did(citizen_did)
            
            # Build credential references
            credential_refs = []
            if creds_result.get('found') and creds_result.get('credentials'):
                ledger_data = await rust_core.get_ledger_data()
                transactions = ledger_data.get('transactions', {})
                
                for cred in creds_result['credentials']:
                    cred_data = cred.get('transaction', {}).get('data', {})
                    cred_id = cred['credential_id']
                    
                    # Check for revocation
                    is_revoked = False
                    revoked_at = None
                    revocation_reason = None
                    
                    if cred_data.get('status') == 'REVOKED':
                        is_revoked = True
                        revoked_at = cred_data.get('revoked_at')
                        revocation_reason = cred_data.get('revocation_reason')
                    else:
                        # Check for revocation transaction
                        for tx_id, tx in transactions.items():
                            if tx.get('transaction_type') == 'CREDENTIAL_REVOCATION':
                                if tx.get('data', {}).get('credential_id') == cred_id:
                                    is_revoked = True
                                    rev_data = tx.get('data', {})
                                    revoked_at = rev_data.get('revoked_at')
                                    revocation_reason = rev_data.get('revocation_reason')
                                    break
                    
                    credential_refs.append({
                        'id': cred_id,
                        'type': cred['credential_type'],
                        'status': 'REVOKED' if is_revoked else cred['status'],
                        'issued_at': cred['issued_at'],
                        'expires_at': cred.get('expires_at'),
                        'transaction_id': cred['transaction_id'],
                        'revoked': is_revoked,
                        'revoked_at': revoked_at,
                        'revocation_reason': revocation_reason,
                        'issuer': cred_data.get('issuer', 'Government of India'),
                        'credentialSubject': cred_data.get('credential_data', {})
                    })
            
            # Build updated DID document
            did_document = did_doc_data.get('document', {})
            if not did_document:
                # Generate base DID document
                did_document = await self._generate_base_did_document(citizen_did)
            
            # Update DID document with credential references
            did_document['updated_at'] = datetime.now().isoformat()
            did_document['credentialReferences'] = credential_refs
            did_document['credentialCount'] = len(credential_refs)
            did_document['activeCredentials'] = len([c for c in credential_refs if not c.get('revoked', False)])
            did_document['revokedCredentials'] = len([c for c in credential_refs if c.get('revoked', False)])
            
            # Add service endpoint for credential verification
            if 'service' not in did_document:
                did_document['service'] = []
            
            # Update or add credential service endpoint
            credential_service = None
            for service in did_document['service']:
                if service.get('type') == 'CredentialVerificationService':
                    credential_service = service
                    break
            
            if not credential_service:
                credential_service = {
                    'id': f"{citizen_did}#credentials",
                    'type': 'CredentialVerificationService',
                    'serviceEndpoint': f"https://ledger.gov.in/api/verify/{citizen_did}"
                }
                did_document['service'].append(credential_service)
            
            # Upload to IPFS
            if is_ipfs_available():
                # Generate filename from DID
                did_hash = citizen_did.split(':')[-1] if ':' in citizen_did else citizen_did
                filename = f"did_{did_hash}.json"
                
                ipfs_cid = upload_json_to_ipfs(did_document, filename)
                
                if ipfs_cid:
                    ipfs_url = get_ipfs_link(ipfs_cid)
                    
                    # Update stored DID document
                    did_doc_data['document'] = did_document
                    did_doc_data['ipfs_cid'] = ipfs_cid
                    did_doc_data['ipfs_url'] = ipfs_url
                    did_doc_data['updated_at'] = datetime.now().isoformat()
                    did_doc_data['last_ipfs_update'] = datetime.now().isoformat()
                    
                    await self._save_did_document(citizen_did, did_doc_data)
                    
                    print(f"✅ DID document updated on IPFS: {ipfs_cid}")
                    
                    return {
                        'success': True,
                        'ipfs_cid': ipfs_cid,
                        'ipfs_url': ipfs_url,
                        'credential_count': len(credential_refs),
                        'updated_at': did_doc_data['updated_at']
                    }
                else:
                    return {'success': False, 'error': 'Failed to upload to IPFS'}
            else:
                # IPFS not available, update local document only
                did_doc_data['document'] = did_document
                did_doc_data['updated_at'] = datetime.now().isoformat()
                await self._save_did_document(citizen_did, did_doc_data)
                
                return {
                    'success': True,
                    'ipfs_cid': did_doc_data.get('ipfs_cid'),
                    'ipfs_url': did_doc_data.get('ipfs_url'),
                    'credential_count': len(credential_refs),
                    'updated_at': did_doc_data['updated_at'],
                    'ipfs_unavailable': True
                }
                
        except Exception as e:
            print(f"❌ Failed to update DID document: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    async def _load_did_document(self, citizen_did: str) -> Optional[Dict[str, Any]]:
        """Load DID document from storage"""
        try:
            if self.did_documents_file.exists():
                with open(self.did_documents_file, 'r') as f:
                    documents = json.load(f)
                    return documents.get(citizen_did)
            
            # Also check citizens.json
            citizens_file = Path(__file__).parent.parent / 'data' / 'citizens.json'
            if citizens_file.exists():
                with open(citizens_file, 'r') as f:
                    citizens = json.load(f)
                    for citizen in citizens.values():
                        if citizen.get('did') == citizen_did:
                            return {
                                'document': citizen.get('did_document', {}),
                                'ipfs_cid': citizen.get('ipfs_cid'),
                                'ipfs_url': citizen.get('ipfs_link')
                            }
            
            return None
        except Exception as e:
            print(f"❌ Error loading DID document: {e}")
            return None
    
    async def _save_did_document(self, citizen_did: str, did_doc_data: Dict[str, Any]):
        """Save DID document to storage"""
        try:
            documents = {}
            if self.did_documents_file.exists():
                with open(self.did_documents_file, 'r') as f:
                    documents = json.load(f)
            
            documents[citizen_did] = did_doc_data
            
            with open(self.did_documents_file, 'w') as f:
                json.dump(documents, f, indent=2)
        except Exception as e:
            print(f"❌ Error saving DID document: {e}")
    
    async def _generate_base_did_document(self, citizen_did: str) -> Dict[str, Any]:
        """Generate base DID document structure"""
        did_hash = citizen_did.split(':')[-1] if ':' in citizen_did else citizen_did
        
        return {
            '@context': ['https://www.w3.org/ns/did/v1'],
            'id': citizen_did,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'verificationMethod': [{
                'id': f"{citizen_did}#key-1",
                'type': 'Ed25519VerificationKey2018',
                'controller': citizen_did
            }],
            'authentication': [f"{citizen_did}#key-1"],
            'service': [],
            'credentialReferences': [],
            'credentialCount': 0,
            'activeCredentials': 0,
            'revokedCredentials': 0
        }
    
    def _is_recently_updated(self, did_doc_data: Dict[str, Any], threshold_minutes: int = 5) -> bool:
        """Check if DID document was recently updated"""
        try:
            last_update = did_doc_data.get('last_ipfs_update') or did_doc_data.get('updated_at')
            if not last_update:
                return False
            
            from datetime import datetime, timezone, timedelta
            if isinstance(last_update, str):
                last_update_dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
            else:
                return False
            
            threshold = timedelta(minutes=threshold_minutes)
            return datetime.now(timezone.utc) - last_update_dt < threshold
        except Exception as e:
            print(f"⚠️ Error checking update time: {e}")
            return False
    
    async def update_all_did_documents(self):
        """Update all DID documents on IPFS (periodic task)"""
        try:
            print("🔄 Starting periodic DID document update...")
            
            # Get all DIDs from Rust Indy ledger
            rust_core = IndyRustCore(str(self.ledger_file))
            ledger_data = await rust_core.get_ledger_data()
            transactions = ledger_data.get('transactions', {})
            
            # Extract unique DIDs from transactions
            dids = set()
            for tx in transactions.values():
                if tx.get('transaction_type') == 'CREDENTIAL':
                    citizen_did = tx.get('data', {}).get('citizen_did')
                    if citizen_did:
                        dids.add(citizen_did)
            
            print(f"📋 Found {len(dids)} DIDs to update")
            
            results = []
            for citizen_did in dids:
                result = await self.update_did_document_on_ipfs(citizen_did, force_update=False)
                results.append({
                    'did': citizen_did,
                    'success': result.get('success', False),
                    'skipped': result.get('skipped', False)
                })
                
                # Small delay to avoid overwhelming IPFS
                await asyncio.sleep(0.5)
            
            successful = len([r for r in results if r['success'] and not r.get('skipped')])
            skipped = len([r for r in results if r.get('skipped')])
            failed = len([r for r in results if not r['success'] and not r.get('skipped')])
            
            print(f"✅ Periodic update complete: {successful} updated, {skipped} skipped, {failed} failed")
            
            return {
                'success': True,
                'total': len(dids),
                'updated': successful,
                'skipped': skipped,
                'failed': failed,
                'results': results
            }
        except Exception as e:
            print(f"❌ Periodic update failed: {e}")
            return {'success': False, 'error': str(e)}

