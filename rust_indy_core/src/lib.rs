use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;
use std::fs;
use chrono::{DateTime, Utc};
use sha2::{Sha256, Digest};
use hex;
use rand::{Rng, RngCore};
use base58::ToBase58;
use ed25519_dalek::Keypair;
use anyhow::{Result, Context};
use std::sync::{Arc, Mutex};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct IndyTransaction {
    pub id: String,
    pub transaction_type: String,
    pub data: serde_json::Value,
    pub timestamp: DateTime<Utc>,
    pub hash: String,
    pub status: String,
    pub seq_no: u64,
    pub signature: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct IndyDID {
    pub did: String,
    pub verkey: String,
    pub role: String,
    pub created_at: DateTime<Utc>,
    pub status: String,
    pub transaction_hash: String,
    pub keypair: Option<String>, // Base58 encoded keypair
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct IndyCredential {
    pub citizen_did: String,
    pub credential_type: String,
    pub credential_data: serde_json::Value,
    pub created_at: DateTime<Utc>,
    pub status: String,
    pub transaction_hash: String,
    pub schema_id: Option<String>,
    pub cred_def_id: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct IndyPool {
    pub name: String,
    pub genesis_file: String,
    pub nodes: Vec<PoolNode>,
    pub created_at: DateTime<Utc>,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PoolNode {
    pub alias: String,
    pub ip: String,
    pub port: u16,
    pub client_port: u16,
    pub blskey: String,
    pub blskey_pop: String,
    pub services: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct IndyWallet {
    pub name: String,
    pub key: String,
    pub storage_type: String,
    pub created_at: DateTime<Utc>,
    pub status: String,
    pub dids: HashMap<String, IndyDID>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct IndyLedger {
    pub transactions: HashMap<String, IndyTransaction>,
    pub dids: HashMap<String, IndyDID>,
    pub credentials: HashMap<String, IndyCredential>,
    pub pools: HashMap<String, IndyPool>,
    pub wallets: HashMap<String, IndyWallet>,
    pub metadata: LedgerMetadata,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LedgerMetadata {
    pub created_at: DateTime<Utc>,
    pub version: String,
    pub ledger_type: String,
    pub last_updated: DateTime<Utc>,
    pub total_transactions: u64,
    pub total_dids: u64,
    pub total_credentials: u64,
}

pub struct IndyRustCore {
    ledger: Arc<Mutex<IndyLedger>>,
    ledger_file: String,
    current_wallet: Option<String>,
    current_pool: Option<String>,
}

impl IndyRustCore {
    pub fn new(ledger_file: &str) -> Result<Self> {
        let ledger = Self::load_or_create_ledger(ledger_file)?;
        
        Ok(Self {
            ledger: Arc::new(Mutex::new(ledger)),
            ledger_file: ledger_file.to_string(),
            current_wallet: None,
            current_pool: None,
        })
    }

    fn load_or_create_ledger(ledger_file: &str) -> Result<IndyLedger> {
        if Path::new(ledger_file).exists() {
            let content = fs::read_to_string(ledger_file)
                .context("Failed to read ledger file")?;
            let ledger: IndyLedger = serde_json::from_str(&content)
                .context("Failed to parse ledger file")?;
            Ok(ledger)
        } else {
            let ledger = IndyLedger {
                transactions: HashMap::new(),
                dids: HashMap::new(),
                credentials: HashMap::new(),
                pools: HashMap::new(),
                wallets: HashMap::new(),
                metadata: LedgerMetadata {
                    created_at: Utc::now(),
                    version: "2.0".to_string(),
                    ledger_type: "rust_indy_core".to_string(),
                    last_updated: Utc::now(),
                    total_transactions: 0,
                    total_dids: 0,
                    total_credentials: 0,
                },
            };
            ledger.save_to_file(ledger_file)?;
            Ok(ledger)
        }
    }

    pub async fn create_pool(&self, pool_name: &str, genesis_file: &str) -> Result<String> {
        let mut ledger = self.ledger.lock().unwrap();
        
        let pool = IndyPool {
            name: pool_name.to_string(),
            genesis_file: genesis_file.to_string(),
            nodes: vec![PoolNode {
                alias: "RustNode1".to_string(),
                ip: "127.0.0.1".to_string(),
                port: 9701,
                client_port: 9702,
                blskey: "4N8aUNHSgjQVgkpm8nhNEfDf6txHznoYREg9kirmJrkivgL4oSEimFF6nsQ6M41QvhM2Z33nves5vfSn9n1UwNFJBYtWVzHYTHnfcJBPQPgaWU44zBp2imUWiK7Arv4zfk2FhD6V8S8z9i2FjAGkL8QdXrY6nUwsZX2iZTz".to_string(),
                blskey_pop: "RahHYiCvoNCtPTrVtP7nMC5eTYrsUA8WjXbdhNc8debh1agE9bGiJxWBXYNFbnJXoXhWFMvyqhqhRoq737YQemH5ik9oL7R4LLTzb5XSu43pccd9eD7Ey48QqBihNn2U9zsk4q7yvLLb7y7t6WoF3NF9V8pkYkt8iyQ3d96e7bYf8".to_string(),
                services: vec!["VALIDATOR".to_string()],
            }],
            created_at: Utc::now(),
            status: "ACTIVE".to_string(),
        };

        ledger.pools.insert(pool_name.to_string(), pool);
        ledger.metadata.last_updated = Utc::now();
        ledger.save_to_file(&self.ledger_file)?;

        println!("✅ Created Rust Indy pool: {}", pool_name);
        Ok(pool_name.to_string())
    }

    pub async fn create_wallet(&self, wallet_name: &str, wallet_key: &str) -> Result<String> {
        let mut ledger = self.ledger.lock().unwrap();
        
        let wallet = IndyWallet {
            name: wallet_name.to_string(),
            key: wallet_key.to_string(),
            storage_type: "default".to_string(),
            created_at: Utc::now(),
            status: "ACTIVE".to_string(),
            dids: HashMap::new(),
        };

        ledger.wallets.insert(wallet_name.to_string(), wallet);
        ledger.metadata.last_updated = Utc::now();
        ledger.save_to_file(&self.ledger_file)?;

        println!("✅ Created Rust Indy wallet: {}", wallet_name);
        Ok(wallet_name.to_string())
    }

    pub async fn create_did(&self, wallet_name: &str, wallet_key: &str, seed: Option<&str>) -> Result<(String, String)> {
        let mut ledger = self.ledger.lock().unwrap();
        
        // Generate Ed25519 keypair
        let keypair = if let Some(seed_str) = seed {
            // Use seed to generate deterministic keypair
            let mut seed_bytes = [0u8; 32];
            let seed_hash = Sha256::digest(seed_str.as_bytes());
            seed_bytes.copy_from_slice(&seed_hash[..32]);
            Keypair::from_bytes(&seed_bytes)?
        } else {
            // Generate random keypair using a different approach
            let mut rng = rand::thread_rng();
            let mut seed_bytes = [0u8; 32];
            rng.fill(&mut seed_bytes);
            Keypair::from_bytes(&seed_bytes)?
        };

        // Generate DID from public key
        let public_key_bytes = keypair.public.to_bytes();
        let did = format!("did:rust:{}", hex::encode(&public_key_bytes[..16]));
        
        // Generate verkey
        let verkey = format!("~{}", keypair.public.to_bytes().to_base58());
        
        // Create DID entry
        let did_entry = IndyDID {
            did: did.clone(),
            verkey: verkey.clone(),
            role: "TRUST_ANCHOR".to_string(),
            created_at: Utc::now(),
            status: "ACTIVE".to_string(),
            transaction_hash: "pending".to_string(),
            keypair: Some(keypair.to_bytes().to_base58()),
        };

        // Store DID in wallet
        if let Some(wallet) = ledger.wallets.get_mut(wallet_name) {
            wallet.dids.insert(did.clone(), did_entry.clone());
        }

        // Store DID in ledger
        ledger.dids.insert(did.clone(), did_entry);
        ledger.metadata.total_dids += 1;
        ledger.metadata.last_updated = Utc::now();
        ledger.save_to_file(&self.ledger_file)?;

        println!("✅ Created Rust Indy DID: {}", did);
        println!("   Verkey: {}", verkey);
        Ok((did, verkey))
    }

    pub async fn write_nym_transaction(&self, transaction_data: serde_json::Value) -> Result<String> {
        let mut ledger = self.ledger.lock().unwrap();
        
        let dest = transaction_data["dest"].as_str()
            .context("Missing 'dest' field in transaction")?;
        let verkey = transaction_data["verkey"].as_str()
            .context("Missing 'verkey' field in transaction")?;
        let role = transaction_data["role"].as_str().unwrap_or("TRUST_ANCHOR");

        // Generate transaction hash
        let tx_data = serde_json::to_string(&transaction_data)?;
        let mut hasher = Sha256::new();
        hasher.update(tx_data.as_bytes());
        let hash = hex::encode(hasher.finalize());
        let transaction_id = format!("rust_txn_{}", &hash[..16]);

        // Create transaction
        let transaction = IndyTransaction {
            id: transaction_id.clone(),
            transaction_type: "NYM".to_string(),
            data: transaction_data.clone(),
            timestamp: Utc::now(),
            hash: hash.clone(),
            status: "COMMITTED".to_string(),
            seq_no: ledger.metadata.total_transactions + 1,
            signature: None,
        };

        // Update DID entry
        if let Some(did_entry) = ledger.dids.get_mut(dest) {
            did_entry.transaction_hash = transaction_id.clone();
            did_entry.status = "ACTIVE".to_string();
        }

        // Store transaction
        ledger.transactions.insert(transaction_id.clone(), transaction);
        ledger.metadata.total_transactions += 1;
        ledger.metadata.last_updated = Utc::now();

        // Save ledger
        ledger.save_to_file(&self.ledger_file)?;

        println!("✅ Written NYM transaction to Rust Indy ledger: {}", transaction_id);
        Ok(transaction_id)
    }

    pub async fn write_credential_transaction(&self, credential_data: serde_json::Value) -> Result<String> {
        let mut ledger = self.ledger.lock().unwrap();
        
        let citizen_did = credential_data["citizen_did"].as_str()
            .context("Missing 'citizen_did' field in credential")?;
        let credential_type = credential_data["credential_type"].as_str()
            .context("Missing 'credential_type' field in credential")?;

        // Generate transaction hash
        let tx_data = serde_json::to_string(&credential_data)?;
        let mut hasher = Sha256::new();
        hasher.update(tx_data.as_bytes());
        let hash = hex::encode(hasher.finalize());
        let transaction_id = format!("rust_cred_{}", &hash[..16]);

        // Create transaction
        let transaction = IndyTransaction {
            id: transaction_id.clone(),
            transaction_type: "CREDENTIAL".to_string(),
            data: credential_data.clone(),
            timestamp: Utc::now(),
            hash: hash.clone(),
            status: "COMMITTED".to_string(),
            seq_no: ledger.metadata.total_transactions + 1,
            signature: None,
        };

        // Create credential entry
        let credential_entry = IndyCredential {
            citizen_did: citizen_did.to_string(),
            credential_type: credential_type.to_string(),
            credential_data: credential_data.clone(),
            created_at: Utc::now(),
            status: "VERIFIED".to_string(),
            transaction_hash: transaction_id.clone(),
            schema_id: None,
            cred_def_id: None,
        };

        // Store transaction and credential
        ledger.transactions.insert(transaction_id.clone(), transaction);
        ledger.credentials.insert(citizen_did.to_string(), credential_entry);
        ledger.metadata.total_transactions += 1;
        ledger.metadata.total_credentials += 1;
        ledger.metadata.last_updated = Utc::now();

        // Save ledger
        ledger.save_to_file(&self.ledger_file)?;

        println!("✅ Written credential transaction to Rust Indy ledger: {}", transaction_id);
        Ok(transaction_id)
    }

    pub async fn verify_did(&self, did: &str) -> Result<serde_json::Value> {
        let ledger = self.ledger.lock().unwrap();
        
        if let Some(did_info) = ledger.dids.get(did) {
            Ok(serde_json::json!({
                "verified": true,
                "ledger": "rust_indy_core",
                "did_info": did_info,
                "status": "ACTIVE"
            }))
        } else {
            Ok(serde_json::json!({
                "verified": false,
                "ledger": "rust_indy_core",
                "status": "NOT_FOUND"
            }))
        }
    }

    pub fn get_ledger_stats(&self) -> serde_json::Value {
        let ledger = self.ledger.lock().unwrap();
        serde_json::json!({
            "total_transactions": ledger.metadata.total_transactions,
            "total_dids": ledger.metadata.total_dids,
            "total_credentials": ledger.metadata.total_credentials,
            "total_pools": ledger.pools.len(),
            "total_wallets": ledger.wallets.len(),
            "last_updated": ledger.metadata.last_updated,
            "ledger_type": "rust_indy_core"
        })
    }

    pub fn get_all_transactions(&self) -> HashMap<String, IndyTransaction> {
        let ledger = self.ledger.lock().unwrap();
        ledger.transactions.clone()
    }

    pub fn get_all_dids(&self) -> HashMap<String, IndyDID> {
        let ledger = self.ledger.lock().unwrap();
        ledger.dids.clone()
    }

    pub fn get_all_credentials(&self) -> HashMap<String, IndyCredential> {
        let ledger = self.ledger.lock().unwrap();
        ledger.credentials.clone()
    }

    pub fn get_all_pools(&self) -> HashMap<String, IndyPool> {
        let ledger = self.ledger.lock().unwrap();
        ledger.pools.clone()
    }

    pub fn get_all_wallets(&self) -> HashMap<String, IndyWallet> {
        let ledger = self.ledger.lock().unwrap();
        ledger.wallets.clone()
    }
}

impl IndyLedger {
    pub fn save_to_file(&self, file_path: &str) -> Result<()> {
        let content = serde_json::to_string_pretty(self)?;
        fs::write(file_path, content)
            .context("Failed to save ledger file")?;
        Ok(())
    }
}

// Python FFI bindings
use std::ffi::{CStr, CString};
use std::os::raw::c_char;

static mut INDY_CORE: Option<IndyRustCore> = None;

#[no_mangle]
pub extern "C" fn init_rust_indy_core(ledger_file: *const c_char) -> i32 {
    let ledger_file_cstr = unsafe { CStr::from_ptr(ledger_file) };
    let ledger_file_str = match ledger_file_cstr.to_str() {
        Ok(s) => s,
        Err(_) => return -1,
    };
    
    match IndyRustCore::new(ledger_file_str) {
        Ok(core) => {
            unsafe {
                INDY_CORE = Some(core);
            }
            0
        },
        Err(_) => -1,
    }
}

#[no_mangle]
pub extern "C" fn create_pool_rust(
    pool_name: *const c_char,
    genesis_file: *const c_char,
) -> *mut c_char {
    let pool_name_cstr = unsafe { CStr::from_ptr(pool_name) };
    let genesis_file_cstr = unsafe { CStr::from_ptr(genesis_file) };
    
    let pool_name_str = match pool_name_cstr.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };
    
    let genesis_file_str = match genesis_file_cstr.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };

    let core = unsafe {
        match &INDY_CORE {
            Some(c) => c,
            None => return std::ptr::null_mut(),
        }
    };

    let mut rt = tokio::runtime::Runtime::new().unwrap();
    
    match rt.block_on(core.create_pool(pool_name_str, genesis_file_str)) {
        Ok(result) => {
            match CString::new(result) {
                Ok(c_string) => c_string.into_raw(),
                Err(_) => std::ptr::null_mut(),
            }
        },
        Err(_) => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub extern "C" fn create_wallet_rust(
    wallet_name: *const c_char,
    wallet_key: *const c_char,
) -> *mut c_char {
    let wallet_name_cstr = unsafe { CStr::from_ptr(wallet_name) };
    let wallet_key_cstr = unsafe { CStr::from_ptr(wallet_key) };
    
    let wallet_name_str = match wallet_name_cstr.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };
    
    let wallet_key_str = match wallet_key_cstr.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };

    let core = unsafe {
        match &INDY_CORE {
            Some(c) => c,
            None => return std::ptr::null_mut(),
        }
    };

    let mut rt = tokio::runtime::Runtime::new().unwrap();
    
    match rt.block_on(core.create_wallet(wallet_name_str, wallet_key_str)) {
        Ok(result) => {
            match CString::new(result) {
                Ok(c_string) => c_string.into_raw(),
                Err(_) => std::ptr::null_mut(),
            }
        },
        Err(_) => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub extern "C" fn create_did_rust(
    wallet_name: *const c_char,
    wallet_key: *const c_char,
    seed: *const c_char,
) -> *mut c_char {
    let wallet_name_cstr = unsafe { CStr::from_ptr(wallet_name) };
    let wallet_key_cstr = unsafe { CStr::from_ptr(wallet_key) };
    let seed_cstr = unsafe { CStr::from_ptr(seed) };
    
    let wallet_name_str = match wallet_name_cstr.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };
    
    let wallet_key_str = match wallet_key_cstr.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };
    
    let seed_str = match seed_cstr.to_str() {
        Ok(s) => if s.is_empty() { None } else { Some(s) },
        Err(_) => None,
    };

    let core = unsafe {
        match &INDY_CORE {
            Some(c) => c,
            None => return std::ptr::null_mut(),
        }
    };

    let mut rt = tokio::runtime::Runtime::new().unwrap();
    
    match rt.block_on(core.create_did(wallet_name_str, wallet_key_str, seed_str)) {
        Ok((did, verkey)) => {
            let result = serde_json::json!({
                "did": did,
                "verkey": verkey
            });
            let json_str = match serde_json::to_string(&result) {
                Ok(s) => s,
                Err(_) => return std::ptr::null_mut(),
            };
            match CString::new(json_str) {
                Ok(c_string) => c_string.into_raw(),
                Err(_) => std::ptr::null_mut(),
            }
        },
        Err(_) => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub extern "C" fn write_nym_transaction_rust(
    transaction_json: *const c_char,
) -> *mut c_char {
    let transaction_cstr = unsafe { CStr::from_ptr(transaction_json) };
    let transaction_str = match transaction_cstr.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };
    
    let transaction_data: serde_json::Value = match serde_json::from_str(transaction_str) {
        Ok(data) => data,
        Err(_) => return std::ptr::null_mut(),
    };

    let core = unsafe {
        match &INDY_CORE {
            Some(c) => c,
            None => return std::ptr::null_mut(),
        }
    };

    let mut rt = tokio::runtime::Runtime::new().unwrap();
    
    match rt.block_on(core.write_nym_transaction(transaction_data)) {
        Ok(result) => {
            match CString::new(result) {
                Ok(c_string) => c_string.into_raw(),
                Err(_) => std::ptr::null_mut(),
            }
        },
        Err(_) => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub extern "C" fn verify_did_rust(did: *const c_char) -> *mut c_char {
    let did_cstr = unsafe { CStr::from_ptr(did) };
    let did_str = match did_cstr.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };

    let core = unsafe {
        match &INDY_CORE {
            Some(c) => c,
            None => return std::ptr::null_mut(),
        }
    };

    let mut rt = tokio::runtime::Runtime::new().unwrap();
    
    match rt.block_on(core.verify_did(did_str)) {
        Ok(result) => {
            let json_str = match serde_json::to_string(&result) {
                Ok(s) => s,
                Err(_) => return std::ptr::null_mut(),
            };
            match CString::new(json_str) {
                Ok(c_string) => c_string.into_raw(),
                Err(_) => std::ptr::null_mut(),
            }
        },
        Err(_) => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub extern "C" fn get_ledger_stats_rust() -> *mut c_char {
    let core = unsafe {
        match &INDY_CORE {
            Some(c) => c,
            None => return std::ptr::null_mut(),
        }
    };

    let stats = core.get_ledger_stats();
    
    let json_str = match serde_json::to_string(&stats) {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };
    match CString::new(json_str) {
        Ok(c_string) => c_string.into_raw(),
        Err(_) => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub extern "C" fn free_rust_string(s: *mut c_char) {
    if !s.is_null() {
        unsafe {
            let _ = CString::from_raw(s);
        }
    }
}
