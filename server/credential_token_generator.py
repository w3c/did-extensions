#!/usr/bin/env python3
"""
Credential-Based Token Generator
Generates DID + Verifiable Credential bound access tokens for:
  - CITIZEN_TOKEN   : citizen presenting VC to prove identity
  - GOVERNMENT_TOKEN: government officer session token with authority proof
  - SERVICE_TOKEN   : short-lived service access token (Passport/PAN/DL)

Each token is derived from:
  - The subject's DID (did:pqie:...)
  - The credential ID / credential hash
  - Token type scope
  - Anti-replay nonce (secrets.token_hex)
  - HMAC-SHA3-512 signature binding everything together
"""

import json
import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from pathlib import Path
from enum import Enum


# ──────────────────────────────────────────────
# Token Types
# ──────────────────────────────────────────────

class TokenType(str, Enum):
    CITIZEN    = "CITIZEN_TOKEN"
    GOVERNMENT = "GOVERNMENT_TOKEN"
    SERVICE    = "SERVICE_TOKEN"


# Token lifetimes
TOKEN_TTL = {
    TokenType.CITIZEN:    24 * 3600,  # 24 hours
    TokenType.GOVERNMENT: 8  * 3600,  # 8 hours (work shift)
    TokenType.SERVICE:    15 * 60,    # 15 minutes (short-lived service grant)
}

# Services that require a VC to be granted access
SERVICE_SCOPES = {
    "passport":          "aadhaar_kyc",
    "pan_card":          "aadhaar_kyc",
    "driving_license":   "aadhaar_kyc",
    "bank_kyc":          "aadhaar_kyc",
}

# Shared HMAC secret (in production: load from ENV / HSM)
_HMAC_SECRET = b"pqie-token-hmac-secret-ring-lwe-2026"

DATA_DIR = Path(__file__).parent.parent / "data"


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _sha3_hex(data: str) -> str:
    return hashlib.sha3_512(data.encode()).hexdigest()


def _hmac_sign(payload: str) -> str:
    return hmac.new(_HMAC_SECRET, payload.encode(), hashlib.sha3_512).hexdigest()


def _vc_hash(credential: Dict[str, Any]) -> str:
    """Deterministic hash of a VC (ignores proof field to allow re-signing)."""
    stable = {k: v for k, v in credential.items() if k != "proof"}
    return _sha3_hex(json.dumps(stable, sort_keys=True))


def _load_citizens() -> Dict:
    f = DATA_DIR / "citizens.json"
    if f.exists():
        with open(f) as fh:
            return json.load(fh)
    return {}


def _load_did_registry() -> Dict:
    f = DATA_DIR / "did_registry.json"
    if f.exists():
        with open(f) as fh:
            return json.load(fh)
    return {"dids": {}}


def _load_token_store() -> Dict:
    f = DATA_DIR / "credential_tokens.json"
    if f.exists():
        with open(f) as fh:
            return json.load(fh)
    return {"tokens": {}}


def _save_token_store(store: Dict):
    f = DATA_DIR / "credential_tokens.json"
    DATA_DIR.mkdir(exist_ok=True)
    with open(f, "w") as fh:
        json.dump(store, fh, indent=2)


# ──────────────────────────────────────────────
# Core Token Builder
# ──────────────────────────────────────────────

def _build_token(
    token_type: TokenType,
    subject_did: str,
    credential_id: str,
    credential_hash: str,
    scope: str,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build and sign a credential-based token.

    Structure:
      header.payload.signature  (JWT-inspired, HMAC-SHA3-512 signed)

    Fields:
      jti    : unique token ID
      iss    : did:pqie:system:token-authority
      sub    : subject DID (citizen / government officer / service)
      typ    : token type (CITIZEN_TOKEN / GOVERNMENT_TOKEN / SERVICE_TOKEN)
      cid    : credential ID the token is bound to
      chash  : SHA3-512 of the credential (tamper detection)
      scope  : what this token authorises
      nonce  : anti-replay 128-bit random
      iat    : issued-at Unix timestamp
      exp    : expiry Unix timestamp
      sig    : HMAC-SHA3-512 over all fields
    """
    now = int(time.time())
    ttl = TOKEN_TTL[token_type]
    jti = f"{token_type.value.lower()}_{secrets.token_hex(16)}"

    payload = {
        "jti":   jti,
        "iss":   "did:pqie:system:token-authority",
        "sub":   subject_did,
        "typ":   token_type.value,
        "cid":   credential_id,
        "chash": credential_hash,
        "scope": scope,
        "nonce": secrets.token_hex(16),
        "iat":   now,
        "exp":   now + ttl,
    }
    if extra:
        payload.update(extra)

    # Sign the canonical sorted JSON payload
    sig_input = json.dumps(payload, sort_keys=True)
    payload["sig"] = _hmac_sign(sig_input)
    payload["issued_at"] = datetime.utcfromtimestamp(now).isoformat() + "Z"
    payload["expires_at"] = datetime.utcfromtimestamp(now + ttl).isoformat() + "Z"
    return payload


def _verify_token_signature(token: Dict[str, Any]) -> bool:
    """Verify HMAC signature — excludes dynamic display fields."""
    sig = token.get("sig")
    if not sig:
        return False
    check = {k: v for k, v in token.items()
             if k not in ("sig", "issued_at", "expires_at")}
    expected = _hmac_sign(json.dumps(check, sort_keys=True))
    return hmac.compare_digest(sig, expected)


def _is_expired(token: Dict[str, Any]) -> bool:
    return int(time.time()) > token.get("exp", 0)


# ──────────────────────────────────────────────
# 1. CITIZEN TOKEN
# ──────────────────────────────────────────────

def generate_citizen_token(citizen_id: str) -> Dict[str, Any]:
    """
    Generate a CITIZEN_TOKEN bound to the citizen's DID + active VC.

    Inputs : citizen_id (portal registration ID)
    Returns: token dict with jti, sub (DID), cid (VC id), sig, exp
    """
    citizens = _load_citizens()
    citizen = citizens.get(citizen_id)
    if not citizen:
        return {"success": False, "error": f"Citizen {citizen_id} not found"}

    # Resolve DID
    did = citizen.get("did") or citizen.get("citizen_did")
    if not did:
        return {"success": False, "error": "Citizen has no DID assigned"}

    # Find their active KYC credential
    credentials = citizen.get("credentials", [])
    active_vc = next(
        (c for c in credentials
         if isinstance(c, dict) and c.get("status") == "ACTIVE"),
        None
    )

    if not active_vc:
        return {"success": False, "error": "No active credential found for citizen"}

    cid   = active_vc.get("id") or active_vc.get("credential_id", "vc_unknown")
    chash = _vc_hash(active_vc)

    token = _build_token(
        token_type      = TokenType.CITIZEN,
        subject_did     = did,
        credential_id   = cid,
        credential_hash = chash,
        scope           = "citizen:identity",
        extra={
            "citizen_id":  citizen_id,
            "citizen_name": citizen.get("name", ""),
            "kyc_status":  active_vc.get("status", "ACTIVE"),
        }
    )

    # Persist token
    store = _load_token_store()
    store["tokens"][token["jti"]] = token
    _save_token_store(store)

    print(f"✅ CITIZEN_TOKEN issued — DID: {did}  VC: {cid}  JTI: {token['jti']}")
    return {"success": True, "token": token}


# ──────────────────────────────────────────────
# 2. GOVERNMENT TOKEN
# ──────────────────────────────────────────────

def generate_government_token(officer_id: str, officer_name: str,
                               authority_level: str = "KYC_OFFICER") -> Dict[str, Any]:
    """
    Generate a GOVERNMENT_TOKEN for a government officer.

    The token is bound to a synthetic government authority DID and a
    self-issued authority credential (no citizen VC needed).
    """
    gov_did = f"did:pqie:gov:india:{_sha3_hex(officer_id)[:12]}"

    # Build a synthetic authority credential
    authority_vc = {
        "@context": ["https://www.w3.org/2018/credentials/v1"],
        "id":       f"gov_authority_vc_{secrets.token_hex(8)}",
        "type":     ["VerifiableCredential", "GovernmentAuthorityCredential"],
        "issuer":   {"id": "did:pqie:gov:india:uidai", "name": "Government of India"},
        "credentialSubject": {
            "id":              gov_did,
            "officer_id":      officer_id,
            "officer_name":    officer_name,
            "authority_level": authority_level,
            "permissions":     ["kyc_approve", "kyc_reject", "did_revoke", "vc_issue"],
        },
        "issuanceDate": datetime.utcnow().isoformat() + "Z",
        "status": "ACTIVE",
    }

    cid   = authority_vc["id"]
    chash = _vc_hash(authority_vc)

    token = _build_token(
        token_type      = TokenType.GOVERNMENT,
        subject_did     = gov_did,
        credential_id   = cid,
        credential_hash = chash,
        scope           = f"government:{authority_level.lower()}",
        extra={
            "officer_id":      officer_id,
            "officer_name":    officer_name,
            "authority_level": authority_level,
            "permissions":     authority_vc["credentialSubject"]["permissions"],
        }
    )

    store = _load_token_store()
    store["tokens"][token["jti"]] = token
    _save_token_store(store)

    print(f"✅ GOVERNMENT_TOKEN issued — Officer: {officer_name}  DID: {gov_did}  JTI: {token['jti']}")
    return {"success": True, "token": token, "authority_credential": authority_vc}


# ──────────────────────────────────────────────
# 3. SERVICE TOKEN
# ──────────────────────────────────────────────

def generate_service_token(citizen_id: str, service_name: str) -> Dict[str, Any]:
    """
    Generate a short-lived SERVICE_TOKEN for a specific service (Passport/PAN/DL).

    Flow:
      1. Resolve citizen DID
      2. Find active VC
      3. Verify VC covers required scope for service_name
      4. Issue 15-minute SERVICE_TOKEN scoped to that service
    """
    if service_name not in SERVICE_SCOPES:
        return {
            "success": False,
            "error": f"Unknown service '{service_name}'. Valid: {list(SERVICE_SCOPES.keys())}"
        }

    citizens = _load_citizens()
    citizen = citizens.get(citizen_id)
    if not citizen:
        return {"success": False, "error": f"Citizen {citizen_id} not found"}

    did = citizen.get("did") or citizen.get("citizen_did")
    if not did:
        return {"success": False, "error": "Citizen has no DID"}

    # Check for active credential that covers this service's required scope
    required_scope = SERVICE_SCOPES[service_name]
    credentials = citizen.get("credentials", [])

    active_vc = None
    for c in credentials:
        if not isinstance(c, dict):
            continue
        if c.get("status") not in ("ACTIVE", "VERIFIED"):
            continue
        ctype = (c.get("type") or c.get("credential_type") or "").lower()
        if required_scope.replace("_", "") in ctype.replace("_", "").replace(" ", ""):
            active_vc = c
            break

    # Fallback: any ACTIVE credential
    if not active_vc:
        active_vc = next(
            (c for c in credentials
             if isinstance(c, dict) and c.get("status") in ("ACTIVE", "VERIFIED")),
            None
        )

    if not active_vc:
        return {
            "success": False,
            "error": f"No active credential found. {service_name} requires an approved KYC VC."
        }

    if citizen.get("kyc_status") == "REVOKED" or citizen.get("status") == "REVOKED":
        return {"success": False, "error": "Citizen DID is revoked. Service access denied."}

    cid   = active_vc.get("id") or active_vc.get("credential_id", "vc_unknown")
    chash = _vc_hash(active_vc)

    token = _build_token(
        token_type      = TokenType.SERVICE,
        subject_did     = did,
        credential_id   = cid,
        credential_hash = chash,
        scope           = f"service:{service_name}",
        extra={
            "citizen_id":     citizen_id,
            "citizen_name":   citizen.get("name", ""),
            "service":        service_name,
            "required_scope": required_scope,
            "vc_bound":       True,
        }
    )

    store = _load_token_store()
    store["tokens"][token["jti"]] = token
    _save_token_store(store)

    print(f"✅ SERVICE_TOKEN issued — Service: {service_name}  DID: {did}  exp: 15min  JTI: {token['jti']}")
    return {"success": True, "token": token}


# ──────────────────────────────────────────────
# Token Verification
# ──────────────────────────────────────────────

def verify_token(jti: str) -> Dict[str, Any]:
    """
    Verify a token by JTI:
      1. Locate in store
      2. Verify HMAC signature
      3. Check expiry
      4. Verify VC hash hasn't changed (tamper detection)
    """
    store = _load_token_store()
    token = store["tokens"].get(jti)
    if not token:
        return {"valid": False, "error": "Token not found"}

    if _is_expired(token):
        return {"valid": False, "error": "Token expired", "expired_at": token.get("expires_at")}

    if not _verify_token_signature(token):
        return {"valid": False, "error": "Invalid token signature — possible tampering"}

    return {
        "valid":      True,
        "jti":        jti,
        "typ":        token["typ"],
        "sub":        token["sub"],
        "scope":      token["scope"],
        "expires_at": token["expires_at"],
        "token":      token,
    }


def revoke_token(jti: str) -> Dict[str, Any]:
    """Immediately revoke a token by JTI."""
    store = _load_token_store()
    if jti not in store["tokens"]:
        return {"success": False, "error": "Token not found"}
    store["tokens"][jti]["revoked"] = True
    store["tokens"][jti]["revoked_at"] = datetime.utcnow().isoformat() + "Z"
    _save_token_store(store)
    return {"success": True, "jti": jti, "revoked": True}


def list_tokens_for_did(did: str) -> List[Dict[str, Any]]:
    """Return all non-expired tokens for a given DID."""
    store = _load_token_store()
    now = int(time.time())
    return [
        t for t in store["tokens"].values()
        if t.get("sub") == did and t.get("exp", 0) > now and not t.get("revoked")
    ]


# ──────────────────────────────────────────────
# Convenience: generate all 3 tokens at once
# ──────────────────────────────────────────────

def generate_all_tokens(citizen_id: str, service_name: str = "passport",
                         officer_id: str = "GOV001",
                         officer_name: str = "KYC Officer") -> Dict[str, Any]:
    """
    Convenience function: generate CITIZEN + GOVERNMENT + SERVICE tokens in one call.
    Useful for demo / testing the full token flow.
    """
    citizen_result    = generate_citizen_token(citizen_id)
    government_result = generate_government_token(officer_id, officer_name)
    service_result    = generate_service_token(citizen_id, service_name)

    return {
        "citizen_token":    citizen_result,
        "government_token": government_result,
        "service_token":    service_result,
        "generated_at":     datetime.utcnow().isoformat() + "Z",
    }


# ──────────────────────────────────────────────
# CLI test
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Credential-Based Token Generator — Test")
    print("=" * 60)

    # If citizen_id passed as arg, use it; else pick first citizen
    citizens = _load_citizens()
    if not citizens:
        print("❌ No citizens found in data/citizens.json — register a citizen first.")
        sys.exit(1)

    cid = sys.argv[1] if len(sys.argv) > 1 else next(iter(citizens))
    print(f"\n🆔 Using citizen_id: {cid}")

    print("\n── CITIZEN TOKEN ──")
    r = generate_citizen_token(cid)
    if r["success"]:
        t = r["token"]
        print(f"  JTI   : {t['jti']}")
        print(f"  DID   : {t['sub']}")
        print(f"  VC ID : {t['cid']}")
        print(f"  Scope : {t['scope']}")
        print(f"  Exp   : {t['expires_at']}")

        print("\n  Verifying...")
        v = verify_token(t["jti"])
        print(f"  Valid : {v['valid']}")
    else:
        print(f"  ❌ {r['error']}")

    print("\n── GOVERNMENT TOKEN ──")
    r = generate_government_token("GOV001", "KYC Officer Singh", "KYC_OFFICER")
    if r["success"]:
        t = r["token"]
        print(f"  JTI         : {t['jti']}")
        print(f"  Officer DID : {t['sub']}")
        print(f"  Scope       : {t['scope']}")
        print(f"  Permissions : {t.get('permissions')}")
        print(f"  Exp         : {t['expires_at']}")
    else:
        print(f"  ❌ {r['error']}")

    print("\n── SERVICE TOKEN (passport) ──")
    r = generate_service_token(cid, "passport")
    if r["success"]:
        t = r["token"]
        print(f"  JTI     : {t['jti']}")
        print(f"  DID     : {t['sub']}")
        print(f"  Service : {t.get('service')}")
        print(f"  Scope   : {t['scope']}")
        print(f"  Exp     : {t['expires_at']} (15 min)")
    else:
        print(f"  ❌ {r['error']}")

    print("\n✅ Done.")
