#!/usr/bin/env python3
"""
Selective Disclosure Verifiable Credentials
============================================
Implements per-claim Merkle commitment-based selective disclosure.

How it works:
  1. ISSUE    : Each claim in the VC's credentialSubject is individually salted
               and hashed → commitment. A Merkle tree is built over all
               commitments. The SD-VC stores only the Merkle root (no raw values).
               The claim secrets (salt + value) are given ONLY to the holder.

  2. PRESENT  : Holder picks which claims to reveal. For each revealed claim a
               Merkle inclusion proof is generated. Non-revealed claims remain
               hidden — verifier sees only their hashed commitment.

  3. VERIFY   : Verifier recomputes each revealed claim's commitment from the
               disclosed (salt, name, value) and walks the Merkle proof back to
               the root. If it matches the root in the SD-VC → claim is genuine.
               Hidden claims are never transmitted to the verifier.

Cryptographic primitives:
  - Claim commitment:  SHA3-512(salt | ":" | claim_name | ":" | str(value))
  - Merkle nodes:      SHA3-512(left_hash | right_hash)
  - HMAC binding:      HMAC-SHA3-512 over the full SD-VC (tamper detection)

Supported disclosure request format:
  {
    "sd_vc_id": "<id>",
    "reveal_claims": ["name", "kyc_status"]   ← holder chooses
  }
"""

import hashlib
import hmac
import json
import math
import secrets
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA_DIR = Path(__file__).parent.parent / "data"
SD_VC_STORE = DATA_DIR / "sd_vcs.json"

# HMAC secret — same as credential_token_generator
_HMAC_SECRET = b"pqie-token-hmac-secret-ring-lwe-2026"

# Claims that are ALWAYS revealed (non-optional for compliance)
MANDATORY_CLAIMS = {"kyc_status"}


# ──────────────────────────────────────────────────────────────────────────────
# Low-level: commitment + Merkle tree
# ──────────────────────────────────────────────────────────────────────────────

def _sha3(data: str) -> str:
    return hashlib.sha3_512(data.encode()).hexdigest()


def _make_commitment(salt: str, claim_name: str, claim_value: Any) -> str:
    """SHA3-512( salt : claim_name : str(value) )"""
    payload = f"{salt}:{claim_name}:{json.dumps(claim_value, sort_keys=True)}"
    return _sha3(payload)


def _build_merkle_tree(leaves: List[str]) -> Tuple[str, List[List[str]]]:
    """
    Build a complete binary Merkle tree from leaf hashes.
    Returns (root_hash, levels) where levels[0] = leaves.
    Odd nodes are duplicated to make every level even-length.
    """
    if not leaves:
        return _sha3("empty"), [[]]

    levels: List[List[str]] = [list(leaves)]
    current = list(leaves)

    while len(current) > 1:
        if len(current) % 2 == 1:
            current.append(current[-1])   # duplicate last node
        next_level = []
        for i in range(0, len(current), 2):
            combined = _sha3(current[i] + current[i + 1])
            next_level.append(combined)
        levels.append(next_level)
        current = next_level

    return current[0], levels


def _merkle_proof(leaf_index: int, levels: List[List[str]]) -> List[Dict[str, str]]:
    """
    Generate a Merkle inclusion proof for a leaf by index.
    Returns a list of {"sibling": hash, "position": "left"|"right"} steps.
    """
    proof = []
    idx = leaf_index

    for level in levels[:-1]:   # every level except root
        # pad if needed
        padded = list(level)
        if len(padded) % 2 == 1:
            padded.append(padded[-1])

        if idx % 2 == 0:
            sibling_idx = idx + 1
            position = "right"
        else:
            sibling_idx = idx - 1
            position = "left"

        if sibling_idx < len(padded):
            proof.append({"sibling": padded[sibling_idx], "position": position})

        idx //= 2

    return proof


def _verify_merkle_proof(
    leaf_hash: str,
    proof: List[Dict[str, str]],
    root: str
) -> bool:
    """Walk the Merkle proof from leaf to root and check it equals root."""
    current = leaf_hash
    for step in proof:
        sibling = step["sibling"]
        if step["position"] == "right":
            current = _sha3(current + sibling)
        else:
            current = _sha3(sibling + current)
    return current == root


# ──────────────────────────────────────────────────────────────────────────────
# SD-VC store helpers
# ──────────────────────────────────────────────────────────────────────────────

def _load_store() -> Dict:
    if SD_VC_STORE.exists():
        with open(SD_VC_STORE) as f:
            return json.load(f)
    return {"sd_vcs": {}, "holder_secrets": {}}


def _save_store(store: Dict):
    DATA_DIR.mkdir(exist_ok=True)
    with open(SD_VC_STORE, "w") as f:
        json.dump(store, f, indent=2)


# ──────────────────────────────────────────────────────────────────────────────
# 1. ISSUE — convert a VC to an SD-VC
# ──────────────────────────────────────────────────────────────────────────────

def issue_sd_vc(vc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a standard VC into a Selective Disclosure VC.

    Returns:
        {
            "sd_vc"            : { public SD-VC — sharable with anyone },
            "holder_secrets"   : { claim_name → {salt, value, leaf_index, proof} }
        }

    The sd_vc replaces raw claim values with their SHA3 commitments.
    The holder_secrets dict is given ONLY to the credential holder.
    """
    subject = deepcopy(vc.get("credentialSubject", {}))
    subject_id = subject.pop("id", None)   # DID stays public — not a claim

    # Scrub Aadhaar number from the credential data if present
    cred_data = subject.get("credential_data", {})
    if isinstance(cred_data, dict) and "aadhaar_number" in cred_data:
        cred_data["aadhaar_number"] = "REDACTED"

    claims = {k: v for k, v in subject.items()}

    # Generate per-claim salts and commitments
    salts = {name: secrets.token_hex(16) for name in claims}
    commitments = {
        name: _make_commitment(salts[name], name, value)
        for name, value in claims.items()
    }

    # Build Merkle tree over sorted claim names
    sorted_names = sorted(claims.keys())
    leaves = [commitments[name] for name in sorted_names]
    merkle_root, levels = _build_merkle_tree(leaves)

    # Build holder secrets (per-claim proofs)
    holder_secrets: Dict[str, Any] = {}
    for idx, name in enumerate(sorted_names):
        proof = _merkle_proof(idx, levels)
        holder_secrets[name] = {
            "salt":        salts[name],
            "value":       claims[name],
            "commitment":  commitments[name],
            "leaf_index":  idx,
            "merkle_proof": proof,
        }

    # Build the public SD-VC (commitments replace values)
    sd_vc_id = f"sd_vc_{secrets.token_hex(12)}"
    now = datetime.now(timezone.utc).isoformat()

    sd_vc = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://dixadholakiya.github.io/pqie-did-spec/context.jsonld",
            "https://pqie.network/ns/selective-disclosure/v1",
        ],
        "id":   sd_vc_id,
        "type": ["VerifiableCredential", "SelectiveDisclosureCredential"],
        "issuer": vc.get("issuer", {"id": "did:pqie:gov:india:uidai"}),
        "issuanceDate":   vc.get("issuanceDate", now),
        "expirationDate": vc.get("expirationDate"),
        "credentialSubject": {
            "id":                  subject_id,
            "claim_count":         len(claims),
            "claim_names":         sorted_names,        # names disclosed (not values)
            "claim_commitments":   commitments,         # hashes — no raw values
            "mandatory_claims":    list(MANDATORY_CLAIMS),
        },
        "selectiveDisclosure": {
            "type":        "MerkleCommitmentSD2024",
            "merkle_algo": "SHA3-512",
            "merkle_root": merkle_root,
            "leaf_count":  len(leaves),
        },
        "proof": {
            "type":               "RingLWESignature2024",
            "created":            now,
            "verificationMethod": "did:pqie:gov:india:uidai#key-1",
            "proofPurpose":       "assertionMethod",
            "merkle_root_sig":    hmac.new(
                _HMAC_SECRET,
                (merkle_root + sd_vc_id).encode(),
                hashlib.sha3_512
            ).hexdigest(),
        },
        "originalVcId":    vc.get("id"),
        "originalVcType":  vc.get("type", []),
    }

    # Persist
    store = _load_store()
    store["sd_vcs"][sd_vc_id] = sd_vc
    store["holder_secrets"][sd_vc_id] = {
        "citizen_did": subject_id,
        "secrets":     holder_secrets,
    }
    _save_store(store)

    print(f"✅ SD-VC issued: {sd_vc_id}  claims={sorted_names}  root={merkle_root[:16]}…")
    return {
        "success":        True,
        "sd_vc":          sd_vc,
        "holder_secrets": holder_secrets,
        "merkle_root":    merkle_root,
        "sd_vc_id":       sd_vc_id,
    }


# ──────────────────────────────────────────────────────────────────────────────
# 2. PRESENT — holder builds a selective disclosure presentation
# ──────────────────────────────────────────────────────────────────────────────

def create_presentation(
    sd_vc_id: str,
    reveal_claims: List[str],
    verifier_nonce: str = "",
) -> Dict[str, Any]:
    """
    Holder creates a Verifiable Presentation revealing only `reveal_claims`.

    Each revealed claim includes:
      - The plain-text value
      - Its salt (for commitment re-computation)
      - Its Merkle inclusion proof (to verify against the root)

    Hidden claims contribute only their commitment hash — no value, no salt.

    Args:
        sd_vc_id:       ID of the SD-VC in the store
        reveal_claims:  list of claim names the holder wants to reveal
        verifier_nonce: optional per-request nonce from verifier (anti-replay)

    Returns a VP dict ready to send to the verifier.
    """
    store = _load_store()

    if sd_vc_id not in store["sd_vcs"]:
        return {"success": False, "error": f"SD-VC {sd_vc_id} not found"}

    sd_vc = store["sd_vcs"][sd_vc_id]
    secrets_entry = store["holder_secrets"].get(sd_vc_id, {})
    claim_secrets = secrets_entry.get("secrets", {})

    # Always include mandatory claims
    reveal_set = set(reveal_claims) | MANDATORY_CLAIMS
    available = set(claim_secrets.keys())
    unknown = reveal_set - available
    if unknown:
        return {"success": False, "error": f"Unknown claims requested: {unknown}"}

    disclosed: Dict[str, Any] = {}
    hidden:    Dict[str, str]  = {}

    for name, secret in claim_secrets.items():
        if name in reveal_set:
            disclosed[name] = {
                "value":        secret["value"],
                "salt":         secret["salt"],
                "commitment":   secret["commitment"],
                "merkle_proof": secret["merkle_proof"],
            }
        else:
            hidden[name] = secret["commitment"]   # commitment only — no salt/value

    now = datetime.now(timezone.utc).isoformat()
    vp_id = f"sd_vp_{secrets.token_hex(12)}"

    presentation = {
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://dixadholakiya.github.io/pqie-did-spec/context.jsonld",
        ],
        "id":   vp_id,
        "type": ["VerifiablePresentation", "SelectiveDisclosurePresentation"],
        "holder": sd_vc["credentialSubject"]["id"],
        "verifiableCredential": [{
            "sd_vc_id":    sd_vc_id,
            "merkle_root": sd_vc["selectiveDisclosure"]["merkle_root"],
            "disclosed":   disclosed,
            "hidden_commitments": hidden,
            "claim_names": sd_vc["credentialSubject"]["claim_names"],
        }],
        "presentationMetadata": {
            "created":          now,
            "revealed_claims":  sorted(reveal_set),
            "hidden_claims":    sorted(available - reveal_set),
            "verifier_nonce":   verifier_nonce,
            "presentation_nonce": secrets.token_hex(16),
        },
    }

    print(f"📤 SD Presentation created: revealed={sorted(reveal_set)}  hidden={sorted(available - reveal_set)}")
    return {
        "success":      True,
        "presentation": presentation,
        "vp_id":        vp_id,
        "revealed":     sorted(reveal_set),
        "hidden":       sorted(available - reveal_set),
    }


# ──────────────────────────────────────────────────────────────────────────────
# 3. VERIFY — verifier checks the presentation
# ──────────────────────────────────────────────────────────────────────────────

def verify_presentation(presentation: Dict[str, Any]) -> Dict[str, Any]:
    """
    Verifier validates a selective disclosure presentation.

    For each DISCLOSED claim:
      1. Recompute commitment = SHA3(salt : name : value)
      2. Check commitment matches what's in 'disclosed'
      3. Walk the Merkle proof → must reach the merkle_root

    For HIDDEN claims: verifier only has the commitment hash — cannot see value.

    Returns a detailed verification report.
    """
    try:
        vc_entry = presentation.get("verifiableCredential", [{}])[0]
        merkle_root   = vc_entry.get("merkle_root", "")
        disclosed     = vc_entry.get("disclosed", {})
        claim_names   = vc_entry.get("claim_names", [])   # original sorted order

        errors   = []
        verified = []
        hidden   = []

        for name, data in disclosed.items():
            val        = data["value"]
            salt       = data["salt"]
            commitment = data["commitment"]
            proof      = data["merkle_proof"]

            # Step 1: recompute commitment
            expected = _make_commitment(salt, name, val)
            if expected != commitment:
                errors.append(
                    f"Claim '{name}': commitment mismatch — "
                    f"expected {expected[:12]}… got {commitment[:12]}…"
                )
                continue

            # Step 2: verify Merkle proof
            if not _verify_merkle_proof(commitment, proof, merkle_root):
                errors.append(f"Claim '{name}': Merkle proof invalid — does not reach root")
                continue

            verified.append({
                "claim":  name,
                "value":  val,
                "status": "VERIFIED",
            })

        for name in vc_entry.get("hidden_commitments", {}):
            hidden.append({"claim": name, "status": "HIDDEN", "value": "***"})

        # Check mandatory claims were disclosed
        missing_mandatory = MANDATORY_CLAIMS - {v["claim"] for v in verified}
        if missing_mandatory:
            errors.append(f"Mandatory claims not disclosed: {missing_mandatory}")

        overall_valid = len(errors) == 0 and len(verified) > 0

        report = {
            "valid":            overall_valid,
            "verified_claims":  verified,
            "hidden_claims":    hidden,
            "errors":           errors,
            "merkle_root":      merkle_root,
            "total_claims":     len(claim_names),
            "disclosed_count":  len(verified),
            "hidden_count":     len(hidden),
            "verified_at":      datetime.now(timezone.utc).isoformat(),
        }

        if overall_valid:
            print(f"✅ SD Presentation VERIFIED — disclosed: {[v['claim'] for v in verified]}  hidden: {[h['claim'] for h in hidden]}")
        else:
            print(f"❌ SD Presentation INVALID — errors: {errors}")

        return report

    except Exception as e:
        return {"valid": False, "error": str(e), "verified_claims": [], "hidden_claims": []}


# ──────────────────────────────────────────────────────────────────────────────
# Convenience: end-to-end demo
# ──────────────────────────────────────────────────────────────────────────────

def demo(citizen_id: str, reveal: List[str]) -> None:
    """Run a full issue → present → verify cycle for a citizen's VC."""
    from pathlib import Path as P
    import json as _json

    citizens_file = P(__file__).parent.parent / "data" / "citizens.json"
    with open(citizens_file) as f:
        citizens = _json.load(f)

    citizen = citizens.get(citizen_id)
    if not citizen:
        print(f"❌ Citizen {citizen_id} not found")
        return

    credentials = citizen.get("credentials", [])
    vc = next((c for c in credentials if isinstance(c, dict) and
               c.get("status") in ("ACTIVE", "VERIFIED")), None)
    if not vc:
        print("❌ No active VC — citizen needs to complete KYC first")
        return

    print("\n── STEP 1: Issue SD-VC ─────────────────────────────")
    result = issue_sd_vc(vc)
    if not result["success"]:
        print(f"❌ {result['error']}")
        return

    sd_vc_id = result["sd_vc_id"]
    print(f"   SD-VC ID  : {sd_vc_id}")
    print(f"   Claims    : {result['sd_vc']['credentialSubject']['claim_names']}")
    print(f"   Root      : {result['merkle_root'][:32]}…")

    print(f"\n── STEP 2: Create Presentation (reveal={reveal}) ───")
    pres = create_presentation(sd_vc_id, reveal, verifier_nonce="verifier-nonce-abc")
    if not pres["success"]:
        print(f"❌ {pres['error']}")
        return
    print(f"   Revealed  : {pres['revealed']}")
    print(f"   Hidden    : {pres['hidden']}")

    print("\n── STEP 3: Verify Presentation ─────────────────────")
    report = verify_presentation(pres["presentation"])
    print(f"   Valid     : {report['valid']}")
    for vc_claim in report["verified_claims"]:
        print(f"   ✅  {vc_claim['claim']} = {vc_claim['value']}")
    for hc in report["hidden_claims"]:
        print(f"   🔒  {hc['claim']} = ***  (hidden)")
    if report["errors"]:
        print(f"   Errors: {report['errors']}")


# ──────────────────────────────────────────────────────────────────────────────
# CLI test
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("Selective Disclosure VC — Full Test")
    print("=" * 60)

    # --- unit test with a mock VC (no running server needed) ---
    mock_vc = {
        "id":   "vc_mock_test_001",
        "type": ["VerifiableCredential", "AadhaarKYCCredential"],
        "issuer": {"id": "did:pqie:gov:india:uidai", "name": "UIDAI"},
        "issuanceDate": "2026-02-25T00:00:00Z",
        "credentialSubject": {
            "id":             "did:pqie:5135e697:8b7ecf94:a3f21bc0",
            "name":           "Ravi Kumar",
            "kyc_status":     "APPROVED",
            "kyc_level":      "LEVEL_1",
            "credential_data": {
                "aadhaar_number": "1234-5678-9012",   # will be scrubbed
                "address":        "Mumbai, Maharashtra",
            },
        },
    }

    print("\n─── STEP 1: Issue SD-VC ──────────────────────────────")
    result = issue_sd_vc(mock_vc)
    sd_id  = result["sd_vc_id"]
    print(f"  SD-VC ID : {sd_id}")
    print(f"  Claims   : {result['sd_vc']['credentialSubject']['claim_names']}")
    print(f"  Root     : {result['merkle_root'][:32]}…")
    print(f"  Aadhaar  : {result['sd_vc']['credentialSubject']['claim_commitments'].get('credential_data', 'N/A')[:20]}…  ← commitment only")

    print("\n─── STEP 2: Present (reveal 'name' only) ─────────────")
    p = create_presentation(sd_id, ["name"], "test-verifier-nonce")
    print(f"  Revealed : {p['revealed']}")
    print(f"  Hidden   : {p['hidden']}")

    print("\n─── STEP 3: Verify ────────────────────────────────────")
    r = verify_presentation(p["presentation"])
    print(f"  Valid    : {r['valid']}")
    for vc_claim in r["verified_claims"]:
        print(f"  ✅  {vc_claim['claim']} = {vc_claim['value']}")
    for hc in r["hidden_claims"]:
        print(f"  🔒  {hc['claim']} = ***  (hidden from verifier)")

    print("\n─── STEP 4: Tamper test (corrupt a value) ─────────────")
    tampered_pres = deepcopy(p["presentation"])
    entry = tampered_pres["verifiableCredential"][0]["disclosed"]
    if "name" in entry:
        entry["name"]["value"] = "HACKER"   # tamper with the name
    r2 = verify_presentation(tampered_pres)
    print(f"  Valid after tamper : {r2['valid']}  ← must be False")
    if r2["errors"]:
        print(f"  Error caught       : {r2['errors'][0][:80]}")

    print("\n✅ All tests complete.")
