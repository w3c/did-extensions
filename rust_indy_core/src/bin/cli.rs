use indy_rust_core::IndyRustCore;
use std::env;
use std::process;

#[tokio::main]
async fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() < 2 {
        println!("Usage: indy-rust-cli <command> [args...]");
        println!("Commands:");
        println!("  pool create <name> <genesis_file>");
        println!("  wallet create <name> <key>");
        println!("  did create <wallet_name> <wallet_key> [seed]");
        println!("  ledger nym <dest> <verkey> [role]");
        println!("  ledger verify <did>");
        println!("  stats");
        process::exit(1);
    }

    let ledger_file = "data/rust_indy_core_ledger.json";
    let core = match IndyRustCore::new(ledger_file) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("Failed to initialize Indy Rust Core: {}", e);
            process::exit(1);
        }
    };

    match args[1].as_str() {
        "pool" => {
            if args.len() < 4 {
                eprintln!("Usage: pool create <name> <genesis_file>");
                process::exit(1);
            }
            
            match args[2].as_str() {
                "create" => {
                    let pool_name = &args[3];
                    let genesis_file = &args[4];
                    
                    match core.create_pool(pool_name, genesis_file).await {
                        Ok(_) => println!("✅ Pool '{}' created successfully", pool_name),
                        Err(e) => {
                            eprintln!("❌ Failed to create pool: {}", e);
                            process::exit(1);
                        }
                    }
                },
                _ => {
                    eprintln!("Unknown pool command: {}", args[2]);
                    process::exit(1);
                }
            }
        },
        "wallet" => {
            if args.len() < 4 {
                eprintln!("Usage: wallet create <name> <key>");
                process::exit(1);
            }
            
            match args[2].as_str() {
                "create" => {
                    let wallet_name = &args[3];
                    let wallet_key = &args[4];
                    
                    match core.create_wallet(wallet_name, wallet_key).await {
                        Ok(_) => println!("✅ Wallet '{}' created successfully", wallet_name),
                        Err(e) => {
                            eprintln!("❌ Failed to create wallet: {}", e);
                            process::exit(1);
                        }
                    }
                },
                _ => {
                    eprintln!("Unknown wallet command: {}", args[2]);
                    process::exit(1);
                }
            }
        },
        "did" => {
            if args.len() < 4 {
                eprintln!("Usage: did create <wallet_name> <wallet_key> [seed]");
                process::exit(1);
            }
            
            match args[2].as_str() {
                "create" => {
                    let wallet_name = &args[3];
                    let wallet_key = &args[4];
                    let seed = if args.len() > 5 { Some(args[5].as_str()) } else { None };
                    
                    match core.create_did(wallet_name, wallet_key, seed).await {
                        Ok((did, verkey)) => {
                            println!("✅ DID created successfully");
                            println!("   DID: {}", did);
                            println!("   Verkey: {}", verkey);
                        },
                        Err(e) => {
                            eprintln!("❌ Failed to create DID: {}", e);
                            process::exit(1);
                        }
                    }
                },
                _ => {
                    eprintln!("Unknown did command: {}", args[2]);
                    process::exit(1);
                }
            }
        },
        "ledger" => {
            if args.len() < 3 {
                eprintln!("Usage: ledger <nym|verify> [args...]");
                process::exit(1);
            }
            
            match args[2].as_str() {
                "nym" => {
                    if args.len() < 5 {
                        eprintln!("Usage: ledger nym <dest> <verkey> [role]");
                        process::exit(1);
                    }
                    
                    let dest = &args[3];
                    let verkey = &args[4];
                    let role = if args.len() > 5 { args[5].as_str() } else { "TRUST_ANCHOR" };
                    
                    let transaction = serde_json::json!({
                        "dest": dest,
                        "verkey": verkey,
                        "role": role
                    });
                    
                    match core.write_nym_transaction(transaction).await {
                        Ok(tx_id) => {
                            println!("✅ NYM transaction written successfully");
                            println!("   Transaction ID: {}", tx_id);
                        },
                        Err(e) => {
                            eprintln!("❌ Failed to write NYM transaction: {}", e);
                            process::exit(1);
                        }
                    }
                },
                "verify" => {
                    if args.len() < 4 {
                        eprintln!("Usage: ledger verify <did>");
                        process::exit(1);
                    }
                    
                    let did = &args[3];
                    
                    match core.verify_did(did).await {
                        Ok(result) => {
                            println!("✅ DID verification result:");
                            println!("{}", serde_json::to_string_pretty(&result).unwrap());
                        },
                        Err(e) => {
                            eprintln!("❌ Failed to verify DID: {}", e);
                            process::exit(1);
                        }
                    }
                },
                _ => {
                    eprintln!("Unknown ledger command: {}", args[2]);
                    process::exit(1);
                }
            }
        },
        "stats" => {
            let stats = core.get_ledger_stats();
            println!("📊 Indy Rust Core Statistics:");
            println!("{}", serde_json::to_string_pretty(&stats).unwrap());
        },
        _ => {
            eprintln!("Unknown command: {}", args[1]);
            process::exit(1);
        }
    }
}
