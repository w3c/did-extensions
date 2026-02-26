use indy_rust_core::IndyRustCore;
use serde_json::{json, Value};
use std::collections::HashMap;
use std::fs;
use std::process;

#[tokio::main]
async fn main() {
    let args: Vec<String> = std::env::args().collect();
    
    if args.len() < 2 {
        println!("Usage: unified-ledger <command> [args...]");
        println!("Commands:");
        println!("  show-all                    - Show all ledgers and data");
        println!("  show-dids                   - Show all DIDs");
        println!("  show-credentials            - Show all credentials");
        println!("  show-transactions           - Show all transactions");
        println!("  show-stats                  - Show comprehensive statistics");
        println!("  add-did <did> <data>        - Add DID to registry");
        println!("  add-credential <data>       - Add credential to ledger");
        println!("  verify-did <did>            - Verify DID");
        println!("  search <query>              - Search across all data");
        println!("  export <format>              - Export all data (json/csv)");
        process::exit(1);
    }

    let ledger_file = "data/unified_indy_ledger.json";
    let core = match IndyRustCore::new(ledger_file) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("Failed to initialize Unified Indy Ledger: {}", e);
            process::exit(1);
        }
    };

    match args[1].as_str() {
        "show-all" => {
            show_all_ledgers(&core).await;
        },
        "show-dids" => {
            show_all_dids(&core).await;
        },
        "show-credentials" => {
            show_all_credentials(&core).await;
        },
        "show-transactions" => {
            show_all_transactions(&core).await;
        },
        "show-stats" => {
            show_comprehensive_stats(&core).await;
        },
        "add-did" => {
            if args.len() < 4 {
                eprintln!("Usage: unified-ledger add-did <did> <data>");
                process::exit(1);
            }
            let did = &args[2];
            let data = &args[3];
            add_did_to_registry(&core, did, data).await;
        },
        "add-credential" => {
            if args.len() < 3 {
                eprintln!("Usage: unified-ledger add-credential <data>");
                process::exit(1);
            }
            let data = &args[2];
            add_credential_to_ledger(&core, data).await;
        },
        "verify-did" => {
            if args.len() < 3 {
                eprintln!("Usage: unified-ledger verify-did <did>");
                process::exit(1);
            }
            let did = &args[2];
            verify_did(&core, did).await;
        },
        "search" => {
            if args.len() < 3 {
                eprintln!("Usage: unified-ledger search <query>");
                process::exit(1);
            }
            let query = &args[2];
            search_all_data(&core, query).await;
        },
        "export" => {
            if args.len() < 3 {
                eprintln!("Usage: unified-ledger export <format>");
                process::exit(1);
            }
            let format = &args[2];
            export_all_data(&core, format).await;
        },
        _ => {
            eprintln!("Unknown command: {}", args[1]);
            process::exit(1);
        }
    }
}

async fn show_all_ledgers(core: &IndyRustCore) {
    println!("🔗 UNIFIED INDY LEDGER - ALL DATA");
    println!("{}", "=".repeat(60));
    
    // Load all ledger data
    let ledger_data = load_ledger_data(core).await;
    
    // Show DIDs
    println!("\n📋 DID REGISTRY:");
    println!("{}", "-".repeat(40));
    if let Some(dids) = ledger_data.get("dids") {
        for (did, data) in dids.as_object().unwrap() {
            println!("🔑 DID: {}", did);
            if let Some(status) = data.get("status") {
                println!("   Status: {}", status);
            }
            if let Some(created_at) = data.get("created_at") {
                println!("   Created: {}", created_at);
            }
            println!();
        }
    } else {
        println!("   No DIDs found");
    }
    
    // Show Credentials
    println!("\n🎫 CREDENTIALS:");
    println!("{}", "-".repeat(40));
    if let Some(credentials) = ledger_data.get("credentials") {
        for (citizen_did, data) in credentials.as_object().unwrap() {
            println!("👤 Citizen: {}", citizen_did);
            if let Some(cred_type) = data.get("credential_type") {
                println!("   Type: {}", cred_type);
            }
            if let Some(status) = data.get("status") {
                println!("   Status: {}", status);
            }
            if let Some(created_at) = data.get("created_at") {
                println!("   Created: {}", created_at);
            }
            println!();
        }
    } else {
        println!("   No credentials found");
    }
    
    // Show Transactions
    println!("\n📊 TRANSACTIONS:");
    println!("{}", "-".repeat(40));
    if let Some(transactions) = ledger_data.get("transactions") {
        for (tx_id, data) in transactions.as_object().unwrap() {
            println!("🔄 Transaction: {}", tx_id);
            if let Some(tx_type) = data.get("transaction_type") {
                println!("   Type: {}", tx_type);
            }
            if let Some(status) = data.get("status") {
                println!("   Status: {}", status);
            }
            if let Some(timestamp) = data.get("timestamp") {
                println!("   Time: {}", timestamp);
            }
            println!();
        }
    } else {
        println!("   No transactions found");
    }
    
    // Show Statistics
    println!("\n📈 STATISTICS:");
    println!("{}", "-".repeat(40));
    if let Some(metadata) = ledger_data.get("metadata") {
        println!("{}", serde_json::to_string_pretty(metadata).unwrap());
    }
}

async fn show_all_dids(core: &IndyRustCore) {
    println!("🔑 ALL DIDs IN REGISTRY");
    println!("{}", "=".repeat(50));
    
    let ledger_data = load_ledger_data(core).await;
    
    if let Some(dids) = ledger_data.get("dids") {
        for (did, data) in dids.as_object().unwrap() {
            println!("🔑 DID: {}", did);
            println!("{}", serde_json::to_string_pretty(data).unwrap());
            println!("{}", "-".repeat(50));
        }
    } else {
        println!("No DIDs found in registry");
    }
}

async fn show_all_credentials(core: &IndyRustCore) {
    println!("🎫 ALL CREDENTIALS IN LEDGER");
    println!("{}", "=".repeat(50));
    
    let ledger_data = load_ledger_data(core).await;
    
    if let Some(credentials) = ledger_data.get("credentials") {
        for (citizen_did, data) in credentials.as_object().unwrap() {
            println!("👤 Citizen DID: {}", citizen_did);
            println!("{}", serde_json::to_string_pretty(data).unwrap());
            println!("{}", "-".repeat(50));
        }
    } else {
        println!("No credentials found in ledger");
    }
}

async fn show_all_transactions(core: &IndyRustCore) {
    println!("🔄 ALL TRANSACTIONS IN LEDGER");
    println!("{}", "=".repeat(50));
    
    let ledger_data = load_ledger_data(core).await;
    
    if let Some(transactions) = ledger_data.get("transactions") {
        for (tx_id, data) in transactions.as_object().unwrap() {
            println!("🔄 Transaction: {}", tx_id);
            println!("{}", serde_json::to_string_pretty(data).unwrap());
            println!("{}", "-".repeat(50));
        }
    } else {
        println!("No transactions found in ledger");
    }
}

async fn show_comprehensive_stats(core: &IndyRustCore) {
    println!("📊 COMPREHENSIVE LEDGER STATISTICS");
    println!("{}", "=".repeat(60));
    
    let ledger_data = load_ledger_data(core).await;
    
    // Basic stats
    let total_dids = ledger_data.get("dids").map_or(0, |d| d.as_object().unwrap().len());
    let total_credentials = ledger_data.get("credentials").map_or(0, |c| c.as_object().unwrap().len());
    let total_transactions = ledger_data.get("transactions").map_or(0, |t| t.as_object().unwrap().len());
    
    println!("📈 OVERVIEW:");
    println!("   Total DIDs: {}", total_dids);
    println!("   Total Credentials: {}", total_credentials);
    println!("   Total Transactions: {}", total_transactions);
    
    // DID Status Distribution
    if let Some(dids) = ledger_data.get("dids") {
        let mut status_count: HashMap<String, usize> = HashMap::new();
        for (_, data) in dids.as_object().unwrap() {
            if let Some(status) = data.get("status").and_then(|s| s.as_str()) {
                *status_count.entry(status.to_string()).or_insert(0) += 1;
            }
        }
        
        println!("\n🔑 DID STATUS DISTRIBUTION:");
        for (status, count) in status_count {
            println!("   {}: {}", status, count);
        }
    }
    
    // Credential Type Distribution
    if let Some(credentials) = ledger_data.get("credentials") {
        let mut type_count: HashMap<String, usize> = HashMap::new();
        for (_, data) in credentials.as_object().unwrap() {
            if let Some(cred_type) = data.get("credential_type").and_then(|t| t.as_str()) {
                *type_count.entry(cred_type.to_string()).or_insert(0) += 1;
            }
        }
        
        println!("\n🎫 CREDENTIAL TYPE DISTRIBUTION:");
        for (cred_type, count) in type_count {
            println!("   {}: {}", cred_type, count);
        }
    }
    
    // Transaction Type Distribution
    if let Some(transactions) = ledger_data.get("transactions") {
        let mut tx_type_count: HashMap<String, usize> = HashMap::new();
        for (_, data) in transactions.as_object().unwrap() {
            if let Some(tx_type) = data.get("transaction_type").and_then(|t| t.as_str()) {
                *tx_type_count.entry(tx_type.to_string()).or_insert(0) += 1;
            }
        }
        
        println!("\n🔄 TRANSACTION TYPE DISTRIBUTION:");
        for (tx_type, count) in tx_type_count {
            println!("   {}: {}", tx_type, count);
        }
    }
    
    // Metadata
    if let Some(metadata) = ledger_data.get("metadata") {
        println!("\n📋 LEDGER METADATA:");
        println!("{}", serde_json::to_string_pretty(metadata).unwrap());
    }
}

async fn add_did_to_registry(core: &IndyRustCore, did: &str, data: &str) {
    println!("🔑 Adding DID to registry: {}", did);
    
    let did_data: Value = match serde_json::from_str(data) {
        Ok(data) => data,
        Err(e) => {
            eprintln!("❌ Invalid JSON data: {}", e);
            return;
        }
    };
    
    // Create DID transaction
    let transaction_data = json!({
        "did": did,
        "data": did_data,
        "transaction_type": "DID_REGISTRATION"
    });
    
    match core.write_nym_transaction(transaction_data).await {
        Ok(tx_id) => {
            println!("✅ DID registered successfully");
            println!("   Transaction ID: {}", tx_id);
        },
        Err(e) => {
            eprintln!("❌ Failed to register DID: {}", e);
        }
    }
}

async fn add_credential_to_ledger(core: &IndyRustCore, data: &str) {
    println!("🎫 Adding credential to ledger");
    
    let credential_data: Value = match serde_json::from_str(data) {
        Ok(data) => data,
        Err(e) => {
            eprintln!("❌ Invalid JSON data: {}", e);
            return;
        }
    };
    
    match core.write_credential_transaction(credential_data).await {
        Ok(tx_id) => {
            println!("✅ Credential added successfully");
            println!("   Transaction ID: {}", tx_id);
        },
        Err(e) => {
            eprintln!("❌ Failed to add credential: {}", e);
        }
    }
}

async fn verify_did(core: &IndyRustCore, did: &str) {
    println!("🔍 Verifying DID: {}", did);
    
    match core.verify_did(did).await {
        Ok(result) => {
            println!("✅ DID verification result:");
            println!("{}", serde_json::to_string_pretty(&result).unwrap());
        },
        Err(e) => {
            eprintln!("❌ Failed to verify DID: {}", e);
        }
    }
}

async fn search_all_data(core: &IndyRustCore, query: &str) {
    println!("🔍 Searching for: {}", query);
    
    let ledger_data = load_ledger_data(core).await;
    let mut results = Vec::new();
    
    // Search in DIDs
    if let Some(dids) = ledger_data.get("dids") {
        for (did, data) in dids.as_object().unwrap() {
            if did.contains(query) || data.to_string().to_lowercase().contains(&query.to_lowercase()) {
                results.push(format!("DID: {} - {}", did, data));
            }
        }
    }
    
    // Search in Credentials
    if let Some(credentials) = ledger_data.get("credentials") {
        for (citizen_did, data) in credentials.as_object().unwrap() {
            if citizen_did.contains(query) || data.to_string().to_lowercase().contains(&query.to_lowercase()) {
                results.push(format!("Credential: {} - {}", citizen_did, data));
            }
        }
    }
    
    // Search in Transactions
    if let Some(transactions) = ledger_data.get("transactions") {
        for (tx_id, data) in transactions.as_object().unwrap() {
            if tx_id.contains(query) || data.to_string().to_lowercase().contains(&query.to_lowercase()) {
                results.push(format!("Transaction: {} - {}", tx_id, data));
            }
        }
    }
    
    if results.is_empty() {
        println!("No results found for: {}", query);
    } else {
        println!("Found {} results:", results.len());
        for result in results {
            println!("  {}", result);
        }
    }
}

async fn export_all_data(core: &IndyRustCore, format: &str) {
    println!("📤 Exporting all data in {} format", format);
    
    let ledger_data = load_ledger_data(core).await;
    
    match format {
        "json" => {
            let filename = "exported_ledger_data.json";
            if let Ok(json_str) = serde_json::to_string_pretty(&ledger_data) {
                if let Err(e) = fs::write(filename, json_str) {
                    eprintln!("❌ Failed to write file: {}", e);
                } else {
                    println!("✅ Data exported to {}", filename);
                }
            }
        },
        "csv" => {
            let filename = "exported_ledger_data.csv";
            let mut csv_data = String::new();
            csv_data.push_str("Type,ID,Data\n");
            
            // Export DIDs
            if let Some(dids) = ledger_data.get("dids") {
                for (did, data) in dids.as_object().unwrap() {
                    csv_data.push_str(&format!("DID,{},{}\n", did, data));
                }
            }
            
            // Export Credentials
            if let Some(credentials) = ledger_data.get("credentials") {
                for (citizen_did, data) in credentials.as_object().unwrap() {
                    csv_data.push_str(&format!("Credential,{},{}\n", citizen_did, data));
                }
            }
            
            // Export Transactions
            if let Some(transactions) = ledger_data.get("transactions") {
                for (tx_id, data) in transactions.as_object().unwrap() {
                    csv_data.push_str(&format!("Transaction,{},{}\n", tx_id, data));
                }
            }
            
            if let Err(e) = fs::write(filename, csv_data) {
                eprintln!("❌ Failed to write file: {}", e);
            } else {
                println!("✅ Data exported to {}", filename);
            }
        },
        _ => {
            eprintln!("❌ Unsupported format: {}. Use 'json' or 'csv'", format);
        }
    }
}

async fn load_ledger_data(core: &IndyRustCore) -> Value {
    // This would normally load from the actual ledger file
    // For now, we'll use the core's internal data
    let stats = core.get_ledger_stats();
    
    // Convert stats to a more comprehensive format
    json!({
        "metadata": stats,
        "dids": {},
        "credentials": {},
        "transactions": {}
    })
}
