import requests, json, io
from typing import Dict, Any, Optional

IPFS_API = "http://127.0.0.1:5001/api/v0"


def upload_to_ipfs_bytes(data_bytes, filename="file.json"):
    """
    Upload raw bytes to IPFS.
    Handles 405 Method Not Allowed by forcing POST.
    """
    files = {"file": (filename, io.BytesIO(data_bytes))}
    try:
        res = requests.post(f"{IPFS_API}/add", files=files, timeout=15)
        if res.status_code == 405:  # Fallback
            print("⚠️ Got 405, retrying with POST explicitly...")
            res = requests.request("POST", f"{IPFS_API}/add", files=files, timeout=15)
        res.raise_for_status()
        cid = res.json()["Hash"]
        print(f"✅ Uploaded to IPFS, CID = {cid}")
        return cid
    except Exception as e:
        print(f"❌ IPFS upload failed: {e}")
        return None


def upload_json_to_ipfs(data_dict, filename="did.json"):
    """
    Upload a Python dict as JSON to IPFS.
    """
    data_bytes = json.dumps(data_dict, indent=4).encode("utf-8")
    return upload_to_ipfs_bytes(data_bytes, filename)


def cat_json_from_ipfs(cid):
    """
    Retrieve JSON back from IPFS.
    """
    try:
        res = requests.post(f"{IPFS_API}/cat?arg={cid}", timeout=15)
        if res.status_code == 405:
            print("⚠️ Got 405, retrying with POST explicitly...")
            res = requests.request("POST", f"{IPFS_API}/cat?arg={cid}", timeout=15)
        res.raise_for_status()
        return json.loads(res.content.decode("utf-8"))
    except Exception as e:
        print(f"❌ IPFS fetch failed: {e}")
        return None


def is_ipfs_available():
    """Check if IPFS is available"""
    try:
        res = requests.post(f"{IPFS_API}/version", timeout=5)
        return res.status_code == 200
    except:
        return False


def upload_to_ipfs(data: Dict[Any, Any], filename: Optional[str] = None) -> Optional[str]:
    """Legacy wrapper for upload_json_to_ipfs"""
    return upload_json_to_ipfs(data, filename or "data.json")


def download_from_ipfs(ipfs_hash: str) -> Optional[Dict[Any, Any]]:
    """Legacy wrapper for cat_json_from_ipfs"""
    return cat_json_from_ipfs(ipfs_hash)


def get_ipfs_link(cid: str) -> str:
    """Generate IPFS link from CID"""
    return f"https://ipfs.io/ipfs/{cid}"