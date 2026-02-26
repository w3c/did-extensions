#!/usr/bin/env python3
"""
Start both Citizen Portal and Government Portal servers
"""

import asyncio
import subprocess
import sys
import time
from pathlib import Path

def start_server(script_name, port, description):
    """Start a server script"""
    print(f"🚀 Starting {description} on port {port}...")
    
    try:
        process = subprocess.Popen([
            sys.executable, script_name
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f"✅ {description} started with PID {process.pid}")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start {description}: {e}")
        return None

def main():
    """Main function to start all servers"""
    print("🎯 Starting Aadhaar KYC System Servers")
    print("=" * 50)
    
    # Start Citizen Portal Server
    citizen_process = start_server(
        "server/citizen_portal_server.py", 
        8082, 
        "Citizen Portal Server"
    )
    
    if not citizen_process:
        print("❌ Failed to start Citizen Portal Server")
        return
    
    time.sleep(2)  # Wait a bit
    
    # Start Government Portal Server
    government_process = start_server(
        "server/government_portal_server.py", 
        8081, 
        "Government Portal Server"
    )
    
    if not government_process:
        print("❌ Failed to start Government Portal Server")
        citizen_process.terminate()
        return
    
    time.sleep(2)  # Wait a bit
    
    # Start Ledger Explorer Server
    ledger_process = start_server(
        "server/ledger_explorer_server.py", 
        8083, 
        "Ledger Explorer Server"
    )
    
    if not ledger_process:
        print("❌ Failed to start Ledger Explorer Server")
        citizen_process.terminate()
        government_process.terminate()
        return
    
    time.sleep(2)  # Wait a bit
    
    # Start SDIS Public Resolver Service
    resolver_process = start_server(
        "server/sdis_public_resolver_perfect.py", 
        8085, 
        "SDIS Public Resolver Service (Perfect Logic)"
    )
    
    if not resolver_process:
        print("❌ Failed to start SDIS Public Resolver Service")
        citizen_process.terminate()
        government_process.terminate()
        ledger_process.terminate()
        return
    
    time.sleep(2)  # Wait a bit
    
    # Start Auto Identity Token Integration Server
    auto_token_process = start_server(
        "server/auto_identity_token_integration_server.py", 
        8080, 
        "Auto Identity Token Integration Server"
    )
    
    if not auto_token_process:
        print("❌ Failed to start Auto Identity Token Integration Server")
        citizen_process.terminate()
        government_process.terminate()
        ledger_process.terminate()
        resolver_process.terminate()
        return
    
    print("\n🎉 All servers started successfully!")
    print("=" * 50)
    print("📱 Citizen Portal: http://localhost:8082")
    print("🏛️ Government Portal: http://localhost:8081")
    print("🔍 Ledger Explorer: http://localhost:8083")
    print("🌐 SDIS Public Resolver: http://localhost:8085")
    print("🎫 Auto Identity Token API: http://localhost:8080")
    print("\n📋 Features:")
    print("✅ User login/registration")
    print("✅ DID generation and storage on Indy ledger")
    print("✅ Aadhaar e-KYC workflow")
    print("✅ Government approval system")
    print("✅ Government services access")
    print("✅ Unified ledger explorer")
    print("✅ Real-time ledger monitoring")
    print("✅ W3C-compliant DID resolution")
    print("✅ Universal Resolver integration")
    print("✅ Rust VC Credential Manager")
    print("✅ DID Registry System")
    print("✅ Credential Ledger System")
    print("✅ Auto Identity Token Generation")
    print("✅ DID Retrieval and Resolution")
    print("✅ VC Integration over Indy Ledger")
    print("✅ Multi-blockchain interoperability")
    print("✅ Verifiable Credentials over Indy Ledger")
    print("✅ Ethereum blockchain integration")
    print("✅ Cross-chain identity bridging")
    
    print("\n🔄 Servers are running... Press Ctrl+C to stop")
    
    try:
        # Wait for processes
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if citizen_process.poll() is not None:
                print("❌ Citizen Portal Server stopped")
                break
                
            if government_process.poll() is not None:
                print("❌ Government Portal Server stopped")
                break
                
            if ledger_process.poll() is not None:
                print("❌ Ledger Explorer Server stopped")
                break
                
            if resolver_process.poll() is not None:
                print("❌ SDIS Public Resolver Service stopped")
                break
                
            if auto_token_process.poll() is not None:
                print("❌ Auto Identity Token Integration Server stopped")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        
        # Terminate processes
        citizen_process.terminate()
        government_process.terminate()
        ledger_process.terminate()
        resolver_process.terminate()
        auto_token_process.terminate()
        
        # Wait for graceful shutdown
        citizen_process.wait()
        government_process.wait()
        ledger_process.wait()
        resolver_process.wait()
        auto_token_process.wait()
        
        print("✅ All servers stopped")

if __name__ == "__main__":
    main()
