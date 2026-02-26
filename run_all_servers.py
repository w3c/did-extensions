#!/usr/bin/env python3
"""
Unified Server Startup Script
Runs all Aadhaar KYC System servers from a single file
Just run: python3 run_all_servers.py
"""

import asyncio
import sys
import os
from pathlib import Path
import signal
import time
import threading
from aiohttp import web

# Add project root and server to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'server'))


class UnifiedServer:
    """Unified server that runs all services"""
    
    def __init__(self):
        self.running = True
        self.loops = []
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(sig, frame):
            print("\n🛑 Shutting down all servers...")
            self.running = False
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def start_citizen_portal(self):
        """Start Citizen Portal Server"""
        try:
            from server.citizen_portal_server import CitizenPortalServer
            server = CitizenPortalServer()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loops.append(loop)
            
            async def run():
                runner = web.AppRunner(server.app)
                await runner.setup()
                site = web.TCPSite(runner, '0.0.0.0', 8082)
                await site.start()
                print("✅ Citizen Portal Server: http://localhost:8082")
                while self.running:
                    await asyncio.sleep(1)
                await runner.cleanup()
            
            loop.run_until_complete(run())
        except Exception as e:
            print(f"❌ Citizen Portal failed: {e}")
    
    def start_government_portal(self):
        """Start Government Portal Server"""
        try:
            from server.government_portal_server import GovernmentPortalServer
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loops.append(loop)
            
            async def run():
                server = GovernmentPortalServer()
                await server.initialize()
                
                runner = web.AppRunner(server.app)
                await runner.setup()
                site = web.TCPSite(runner, '0.0.0.0', 8081)
                await site.start()
                print("✅ Government Portal Server: http://localhost:8081")
                while self.running:
                    await asyncio.sleep(1)
                await runner.cleanup()
            
            loop.run_until_complete(run())
        except Exception as e:
            print(f"❌ Government Portal failed: {e}")
    
    def start_ledger_explorer(self):
        """Start Ledger Explorer Server"""
        try:
            from server.ledger_explorer_server import LedgerExplorerServer
            server = LedgerExplorerServer()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loops.append(loop)
            
            async def run():
                runner = web.AppRunner(server.app)
                await runner.setup()
                site = web.TCPSite(runner, '0.0.0.0', 8083)
                await site.start()
                print("✅ Ledger Explorer Server: http://localhost:8083")
                while self.running:
                    await asyncio.sleep(1)
                await runner.cleanup()
            
            loop.run_until_complete(run())
        except Exception as e:
            print(f"❌ Ledger Explorer failed: {e}")
    
    def start_sdis_resolver(self):
        """Start SDIS Public Resolver"""
        try:
            from server.sdis_public_resolver_perfect import SDISPublicResolver
            server = SDISPublicResolver()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loops.append(loop)
            
            async def run():
                runner = web.AppRunner(server.app)
                await runner.setup()
                site = web.TCPSite(runner, '0.0.0.0', 8085)
                await site.start()
                print("✅ SDIS Public Resolver: http://localhost:8085")
                while self.running:
                    await asyncio.sleep(1)
                await runner.cleanup()
            
            loop.run_until_complete(run())
        except Exception as e:
            print(f"⚠️ SDIS Resolver failed (optional): {e}")
    
    def start_auto_token_api(self):
        """Start Auto Identity Token API"""
        try:
            from server.auto_identity_token_integration_server import AutoIdentityTokenIntegrationServer
            server = AutoIdentityTokenIntegrationServer()
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.loops.append(loop)
            
            async def run():
                runner = web.AppRunner(server.app)
                await runner.setup()
                site = web.TCPSite(runner, '0.0.0.0', 8080)
                await site.start()
                print("✅ Auto Identity Token API: http://localhost:8080")
                while self.running:
                    await asyncio.sleep(1)
                await runner.cleanup()
            
            loop.run_until_complete(run())
        except Exception as e:
            print(f"⚠️ Auto Token API failed (optional): {e}")
    
    def start_all_servers(self):
        """Start all servers in separate threads"""
        self.setup_signal_handlers()
        
        print("=" * 70)
        print("🎯 Starting Aadhaar KYC System - All Servers")
        print("=" * 70)
        print()
        print("🚀 Starting servers...")
        print()
        
        # Start each server in a separate thread
        threads = []
        
        # Thread 1: Citizen Portal
        t1 = threading.Thread(target=self.start_citizen_portal, daemon=True, name="CitizenPortal")
        t1.start()
        threads.append(t1)
        time.sleep(2)
        
        # Thread 2: Government Portal
        t2 = threading.Thread(target=self.start_government_portal, daemon=True, name="GovernmentPortal")
        t2.start()
        threads.append(t2)
        time.sleep(2)
        
        # Thread 3: Ledger Explorer
        t3 = threading.Thread(target=self.start_ledger_explorer, daemon=True, name="LedgerExplorer")
        t3.start()
        threads.append(t3)
        time.sleep(2)
        
        # Thread 4: SDIS Resolver (optional)
        t4 = threading.Thread(target=self.start_sdis_resolver, daemon=True, name="SDISResolver")
        t4.start()
        threads.append(t4)
        time.sleep(2)
        
        # Thread 5: Auto Token API (optional)
        t5 = threading.Thread(target=self.start_auto_token_api, daemon=True, name="AutoTokenAPI")
        t5.start()
        threads.append(t5)
        time.sleep(2)
        
        print()
        print("=" * 70)
        print("✅ ALL SERVERS STARTED!")
        print("=" * 70)
        print()
        print("🔗 Quick Links:")
        print("📱 Citizen Portal:      http://localhost:8082")
        print("🏛️ Government Portal:   http://localhost:8081")
        print("🔍 Ledger Explorer:     http://localhost:8083")
        print("🌐 SDIS Resolver:       http://localhost:8085")
        print("🎫 Auto Token API:      http://localhost:8080")
        print("📋 VC Viewer:           http://localhost:8083/vc-viewer")
        print()
        print("=" * 70)
        print("🔄 Servers running... Press Ctrl+C to stop")
        print("=" * 70)
        print()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
                alive = sum(1 for t in threads if t.is_alive())
                if alive == 0:
                    print("❌ All server threads stopped")
                    break
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self.running = False


def main():
    """Main entry point"""
    server = UnifiedServer()
    server.start_all_servers()


if __name__ == "__main__":
    main()

