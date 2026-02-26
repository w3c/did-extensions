#!/usr/bin/env python3
"""
System Data Reset Script
Clears all ledger, wallet, and credential data for a fresh start.
"""
import json
import os
from pathlib import Path
from datetime import datetime, timezone

DATA_DIR = Path(__file__).parent / 'data'

def reset():
    print("🔄 Starting system data reset...")
    
    # 1. Remove backup files
    for f in DATA_DIR.glob("*.backup_*.json"):
        f.unlink()
        print(f"  🗑️  Deleted backup: {f.name}")

    # 2. Remove individual Indy wallet files (hex-named)
    for f in DATA_DIR.glob("????????????????.json"):
        f.unlink()
        print(f"  🗑️  Deleted wallet file: {f.name}")

    # 3. Reset all data files to empty structures
    resets = {
        "aadhaar_requests.json": {"requests": {}, "total_requests": 0},
        "citizens.json": {},
        "user_accounts.json": {},
        "user_sessions.json": {},
        "did_registry.json": {
            "registry_metadata": {
                "registry_id": "aadhaar_did_registry_v2",
                "version": "2.0.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "total_dids": 0,
                "active_dids": 0,
                "revoked_dids": 0,
                "max_dids": 1000000
            },
            "registry_settings": {"backup_enabled": True, "indexing_enabled": True, "auto_cleanup": False, "retention_days": 3650},
            "indexes": {"by_status": {"ACTIVE": [], "REVOKED": [], "SUSPENDED": []}, "by_blockchain": {"indy": []}, "by_citizen_name": {}},
            "statistics": {"blockchain_distribution": {"indy": 0, "ethereum": 0, "other": 0}, "monthly_registrations": {}, "daily_registrations": {}, "status_distribution": {"ACTIVE": 0, "REVOKED": 0, "SUSPENDED": 0}},
            "dids": {}
        },
        "credential_ledger.json": {
            "ledger_id": "aadhaar_credential_ledger_v2",
            "version": "2.0.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_credentials": 0,
            "active_credentials": 0,
            "revoked_credentials": 0,
            "credentials": {},
            "indexes": {"by_citizen_did": {}, "by_type": {}, "by_status": {}, "by_date": {}}
        },
        "rust_indy_core_ledger.json": {
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
        },
        "rust_style_indy_ledger.json": {
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
        },
        "indy_ledger.json": {"transactions": [], "total_transactions": 0},
        "unified_vc_ledger.json": {
            "ledger_metadata": {
                "ledger_id": "unified_vc_cross_blockchain_ledger_v1",
                "version": "1.0.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "last_updated": datetime.now(timezone.utc).isoformat(),
                "supported_blockchains": ["indy", "ethereum", "polkadot", "hyperledger_fabric"],
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
        },
        "unified_indy_ledger.json": {"transactions": {}, "total": 0},
        "auto_identity_tokens.json": {
            "ledger_id": "auto_identity_token_ledger_v1",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "total_tokens": 0,
            "active_tokens": 0,
            "expired_tokens": 0,
            "revoked_tokens": 0,
            "tokens": {},
            "token_indexes": {"by_citizen_did": {}, "by_token_type": {}, "by_status": {}, "by_issued_date": {}}
        },
        "did_documents.json": {"documents": {}, "total": 0},
        "vc_transactions.json": {"transactions": {}, "total_transactions": 0},
        "quantum_signature_ledger.json": {"signatures": {}, "total": 0},
        "service_ledger.json": {"services": {}, "total": 0},
    }

    for filename, empty_data in resets.items():
        filepath = DATA_DIR / filename
        with open(filepath, 'w') as f:
            json.dump(empty_data, f, indent=2)
        print(f"  ✅ Reset: {filename}")

    print("\n✅ System data reset complete! All ledgers are now empty.")
    print("   You can now start fresh with a new citizen registration.")

if __name__ == "__main__":
    reset()
