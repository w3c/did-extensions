#!/usr/bin/env python3
"""
PQIE Multi-Portal Server
Runs all PQIE services on different ports with unified management
"""

import asyncio
import json
import base64
import secrets
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from pqie_framework import PQIEFramework
    from ethereum_pqie_integration import EthereumPQIEIntegration, EthereumPQIEFramework
    PQIE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ PQIE modules not available: {e}")
    PQIE_AVAILABLE = False

# Configuration
PORTS = {
    "main": 8080,      # Main PQIE Portal
    "ethereum": 8081,  # Ethereum Integration Portal
    "admin": 8082,     # Admin Portal
    "api": 8083        # REST API Portal
}

class PQIEMultiPortalServer:
    """
    Multi-portal server for PQIE framework
    """
    
    def __init__(self):
        self.pqie_framework = None
        self.ethereum_integration = None
        self.ethereum_pqie = None
        self.servers = {}
        self.apps = {}
        self.running = False
        
        # Initialize PQIE if available
        if PQIE_AVAILABLE:
            try:
                self.pqie_framework = PQIEFramework()
                print("✅ PQIE Framework initialized")
                
                # Initialize Ethereum integration (optional)
                try:
                    self.ethereum_integration = EthereumPQIEIntegration(
                        web3_provider="http://localhost:8545"
                    )
                    self.ethereum_pqie = EthereumPQIEFramework(
                        self.pqie_framework, 
                        self.ethereum_integration
                    )
                    print("✅ Ethereum Integration initialized")
                except Exception as e:
                    print(f"⚠️ Ethereum integration failed: {e}")
                    
            except Exception as e:
                print(f"❌ PQIE Framework initialization failed: {e}")
        
        # Create Flask apps for each portal
        self._create_portal_apps()
    
    def _create_portal_apps(self):
        """Create Flask apps for each portal"""
        
        # Main Portal
        main_app = Flask("pqie_main")
        CORS(main_app)
        
        @main_app.route('/')
        def main_home():
            return render_template_string(MAIN_PORTAL_TEMPLATE)
        
        @main_app.route('/api/generate-identity', methods=['POST'])
        def generate_identity():
            if not self.pqie_framework:
                return jsonify({"error": "PQIE Framework not available"}), 500
            
            try:
                data = request.get_json()
                user_attributes = data.get('attributes', {})
                user_identifier = data.get('user_id')
                
                result = self.pqie_framework.generate_complete_identity_package(
                    user_attributes, user_identifier
                )
                
                return jsonify({
                    "success": True,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @main_app.route('/api/verify-identity', methods=['POST'])
        def verify_identity():
            if not self.pqie_framework:
                return jsonify({"error": "PQIE Framework not available"}), 500
            
            try:
                data = request.get_json()
                package = data.get('package')
                
                result = self.pqie_framework.verify_identity_package(package)
                
                return jsonify({
                    "success": True,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @main_app.route('/api/status')
        def main_status():
            return jsonify({
                "portal": "main",
                "status": "running",
                "pqie_available": self.pqie_framework is not None,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        self.apps["main"] = main_app
        
        # Ethereum Portal
        eth_app = Flask("pqie_ethereum")
        CORS(eth_app)
        
        @eth_app.route('/')
        def ethereum_home():
            return render_template_string(ETHEREUM_PORTAL_TEMPLATE)
        
        @eth_app.route('/api/register-ethereum', methods=['POST'])
        def register_ethereum():
            if not self.ethereum_pqie:
                return jsonify({"error": "Ethereum Integration not available"}), 500
            
            try:
                data = request.get_json()
                user_attributes = data.get('attributes', {})
                user_identifier = data.get('user_id')
                
                result = self.ethereum_pqie.generate_and_register_identity(
                    user_attributes, user_identifier
                )
                
                return jsonify({
                    "success": True,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @eth_app.route('/api/verify-ethereum', methods=['POST'])
        def verify_ethereum():
            if not self.ethereum_pqie:
                return jsonify({"error": "Ethereum Integration not available"}), 500
            
            try:
                data = request.get_json()
                did = data.get('did')
                
                result = self.ethereum_pqie.verify_ethereum_identity(did)
                
                return jsonify({
                    "success": True,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @eth_app.route('/api/ethereum-stats')
        def ethereum_stats():
            if not self.ethereum_integration:
                return jsonify({"error": "Ethereum Integration not available"}), 500
            
            try:
                stats = self.ethereum_integration.get_ethereum_stats()
                return jsonify({
                    "success": True,
                    "result": stats,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @eth_app.route('/api/status')
        def ethereum_status():
            return jsonify({
                "portal": "ethereum",
                "status": "running",
                "ethereum_available": self.ethereum_pqie is not None,
                "timestamp": datetime.utcnow().isoformat()
            })
        
        self.apps["ethereum"] = eth_app
        
        # Admin Portal
        admin_app = Flask("pqie_admin")
        CORS(admin_app)
        
        @admin_app.route('/')
        def admin_home():
            return render_template_string(ADMIN_PORTAL_TEMPLATE)
        
        @admin_app.route('/api/framework-stats')
        def framework_stats():
            if not self.pqie_framework:
                return jsonify({"error": "PQIE Framework not available"}), 500
            
            try:
                stats = self.pqie_framework.get_framework_performance()
                return jsonify({
                    "success": True,
                    "result": stats,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @admin_app.route('/api/system-status')
        def system_status():
            return jsonify({
                "portal": "admin",
                "status": "running",
                "servers": list(self.servers.keys()),
                "ports": PORTS,
                "pqie_available": self.pqie_framework is not None,
                "ethereum_available": self.ethereum_pqie is not None,
                "uptime": time.time() - getattr(self, 'start_time', time.time()),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        @admin_app.route('/api/stop-server', methods=['POST'])
        def stop_server():
            try:
                data = request.get_json()
                portal = data.get('portal')
                
                if portal in self.servers:
                    # Stop specific server
                    self.servers[portal].shutdown()
                    del self.servers[portal]
                    return jsonify({"success": True, "message": f"Server {portal} stopped"})
                else:
                    return jsonify({"error": f"Server {portal} not found"}), 404
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        self.apps["admin"] = admin_app
        
        # API Portal
        api_app = Flask("pqie_api")
        CORS(api_app)
        
        @api_app.route('/')
        def api_home():
            return render_template_string(API_PORTAL_TEMPLATE)
        
        @api_app.route('/api/endpoints')
        def api_endpoints():
            return jsonify({
                "main_portal": f"http://localhost:{PORTS['main']}",
                "ethereum_portal": f"http://localhost:{PORTS['ethereum']}",
                "admin_portal": f"http://localhost:{PORTS['admin']}",
                "api_portal": f"http://localhost:{PORTS['api']}",
                "endpoints": {
                    "identity": {
                        "generate": f"POST http://localhost:{PORTS['main']}/api/generate-identity",
                        "verify": f"POST http://localhost:{PORTS['main']}/api/verify-identity"
                    },
                    "ethereum": {
                        "register": f"POST http://localhost:{PORTS['ethereum']}/api/register-ethereum",
                        "verify": f"POST http://localhost:{PORTS['ethereum']}/api/verify-ethereum",
                        "stats": f"GET http://localhost:{PORTS['ethereum']}/api/ethereum-stats"
                    },
                    "admin": {
                        "stats": f"GET http://localhost:{PORTS['admin']}/api/framework-stats",
                        "status": f"GET http://localhost:{PORTS['admin']}/api/system-status"
                    }
                }
            })
        
        @api_app.route('/api/health')
        def api_health():
            health_status = {
                "overall": "healthy",
                "services": {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for portal, port in PORTS.items():
                health_status["services"][portal] = {
                    "port": port,
                    "status": "running" if portal in self.servers else "stopped"
                }
            
            return jsonify(health_status)
        
        self.apps["api"] = api_app
    
    def start_server(self, portal: str, port: int):
        """Start individual server in separate thread"""
        if portal not in self.apps:
            print(f"❌ Portal {portal} not found")
            return
        
        app = self.apps[portal]
        
        def run_server():
            try:
                app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
            except Exception as e:
                print(f"❌ Error starting {portal} server: {e}")
        
        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()
        self.servers[portal] = app
        
        print(f"🚀 {portal.title()} Portal started on http://localhost:{port}")
    
    def start_all_servers(self):
        """Start all portal servers"""
        print("🌟 Starting PQIE Multi-Portal Server...")
        print("=" * 50)
        
        self.start_time = time.time()
        
        # Start all servers
        for portal, port in PORTS.items():
            self.start_server(portal, port)
            time.sleep(1)  # Small delay between startups
        
        print("\n✅ All servers started!")
        print(f"📱 Main Portal: http://localhost:{PORTS['main']}")
        print(f"🔗 Ethereum Portal: http://localhost:{PORTS['ethereum']}")
        print(f"⚙️ Admin Portal: http://localhost:{PORTS['admin']}")
        print(f"📡 API Portal: http://localhost:{PORTS['api']}")
        print("\nPress Ctrl+C to stop all servers")
        
        try:
            self.running = True
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all servers...")
            self.stop_all_servers()
    
    def stop_all_servers(self):
        """Stop all running servers"""
        self.running = False
        
        for portal, app in self.servers.items():
            try:
                # Note: Flask doesn't have clean shutdown, but we'll try
                print(f"🛑 Stopping {portal} server...")
            except Exception as e:
                print(f"❌ Error stopping {portal}: {e}")
        
        print("✅ All servers stopped")

# HTML Templates
MAIN_PORTAL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PQIE Main Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #2980b9; }
        textarea { width: 100%; height: 100px; margin: 10px 0; }
        .result { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 PQIE Main Portal</h1>
        
        <div class="section">
            <h2>Generate Identity</h2>
            <textarea id="userAttributes" placeholder='{"name": "Alice Johnson", "email": "alice@example.com"}'></textarea>
            <input type="text" id="userId" placeholder="User ID (optional)">
            <br>
            <button class="btn" onclick="generateIdentity()">Generate Identity</button>
            <div id="generateResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>Verify Identity</h2>
            <textarea id="identityPackage" placeholder="Paste identity package JSON here"></textarea>
            <br>
            <button class="btn" onclick="verifyIdentity()">Verify Identity</button>
            <div id="verifyResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>Portal Links</h2>
            <a href="http://localhost:8081" class="btn">Ethereum Portal</a>
            <a href="http://localhost:8082" class="btn">Admin Portal</a>
            <a href="http://localhost:8083" class="btn">API Portal</a>
        </div>
    </div>

    <script>
        async function generateIdentity() {
            const attributes = document.getElementById('userAttributes').value;
            const userId = document.getElementById('userId').value;
            
            try {
                const response = await fetch('/api/generate-identity', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        attributes: JSON.parse(attributes),
                        user_id: userId
                    })
                });
                
                const result = await response.json();
                document.getElementById('generateResult').style.display = 'block';
                document.getElementById('generateResult').innerHTML = 
                    '<h3>Result:</h3><pre>' + JSON.stringify(result, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('generateResult').innerHTML = 'Error: ' + error.message;
            }
        }
        
        async function verifyIdentity() {
            const package = document.getElementById('identityPackage').value;
            
            try {
                const response = await fetch('/api/verify-identity', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        package: JSON.parse(package)
                    })
                });
                
                const result = await response.json();
                document.getElementById('verifyResult').style.display = 'block';
                document.getElementById('verifyResult').innerHTML = 
                    '<h3>Result:</h3><pre>' + JSON.stringify(result, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('verifyResult').innerHTML = 'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
"""

ETHEREUM_PORTAL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ethereum PQIE Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #27ae60; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #229954; }
        textarea { width: 100%; height: 100px; margin: 10px 0; }
        .result { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔗 Ethereum PQIE Portal</h1>
        
        <div class="section">
            <h2>Register Identity on Ethereum</h2>
            <textarea id="userAttributes" placeholder='{"name": "Alice Johnson", "email": "alice@example.com"}'></textarea>
            <input type="text" id="userId" placeholder="User ID (optional)">
            <br>
            <button class="btn" onclick="registerEthereum()">Register on Ethereum</button>
            <div id="registerResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>Verify Ethereum Identity</h2>
            <input type="text" id="did" placeholder="DID (e.g., did:pqie:abc123)">
            <br>
            <button class="btn" onclick="verifyEthereum()">Verify on Ethereum</button>
            <div id="verifyResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>Ethereum Stats</h2>
            <button class="btn" onclick="getEthereumStats()">Get Stats</button>
            <div id="statsResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>Portal Links</h2>
            <a href="http://localhost:8080" class="btn">Main Portal</a>
            <a href="http://localhost:8082" class="btn">Admin Portal</a>
            <a href="http://localhost:8083" class="btn">API Portal</a>
        </div>
    </div>

    <script>
        async function registerEthereum() {
            const attributes = document.getElementById('userAttributes').value;
            const userId = document.getElementById('userId').value;
            
            try {
                const response = await fetch('/api/register-ethereum', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        attributes: JSON.parse(attributes),
                        user_id: userId
                    })
                });
                
                const result = await response.json();
                document.getElementById('registerResult').style.display = 'block';
                document.getElementById('registerResult').innerHTML = 
                    '<h3>Result:</h3><pre>' + JSON.stringify(result, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('registerResult').innerHTML = 'Error: ' + error.message;
            }
        }
        
        async function verifyEthereum() {
            const did = document.getElementById('did').value;
            
            try {
                const response = await fetch('/api/verify-ethereum', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({did: did})
                });
                
                const result = await response.json();
                document.getElementById('verifyResult').style.display = 'block';
                document.getElementById('verifyResult').innerHTML = 
                    '<h3>Result:</h3><pre>' + JSON.stringify(result, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('verifyResult').innerHTML = 'Error: ' + error.message;
            }
        }
        
        async function getEthereumStats() {
            try {
                const response = await fetch('/api/ethereum-stats');
                const result = await response.json();
                document.getElementById('statsResult').style.display = 'block';
                document.getElementById('statsResult').innerHTML = 
                    '<h3>Ethereum Stats:</h3><pre>' + JSON.stringify(result, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('statsResult').innerHTML = 'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
"""

ADMIN_PORTAL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PQIE Admin Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #e74c3c; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #c0392b; }
        .result { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
        .status { display: inline-block; padding: 5px 10px; border-radius: 3px; margin: 2px; }
        .running { background: #27ae60; color: white; }
        .stopped { background: #e74c3c; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚙️ PQIE Admin Portal</h1>
        
        <div class="section">
            <h2>System Status</h2>
            <button class="btn" onclick="getSystemStatus()">Get System Status</button>
            <div id="systemStatus" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>Framework Statistics</h2>
            <button class="btn" onclick="getFrameworkStats()">Get Framework Stats</button>
            <div id="frameworkStats" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>Server Management</h2>
            <button class="btn" onclick="stopServer('main')">Stop Main Server</button>
            <button class="btn" onclick="stopServer('ethereum')">Stop Ethereum Server</button>
            <button class="btn" onclick="stopServer('admin')">Stop Admin Server</button>
            <button class="btn" onclick="stopServer('api')">Stop API Server</button>
            <div id="serverResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>Portal Links</h2>
            <a href="http://localhost:8080" class="btn">Main Portal</a>
            <a href="http://localhost:8081" class="btn">Ethereum Portal</a>
            <a href="http://localhost:8083" class="btn">API Portal</a>
        </div>
    </div>

    <script>
        async function getSystemStatus() {
            try {
                const response = await fetch('/api/system-status');
                const result = await response.json();
                document.getElementById('systemStatus').style.display = 'block';
                
                let html = '<h3>System Status:</h3>';
                html += '<p><strong>Overall Status:</strong> ' + result.status + '</p>';
                html += '<p><strong>Uptime:</strong> ' + Math.round(result.uptime) + ' seconds</p>';
                html += '<p><strong>PQIE Available:</strong> ' + result.pqie_available + '</p>';
                html += '<p><strong>Ethereum Available:</strong> ' + result.ethereum_available + '</p>';
                html += '<h4>Servers:</h4>';
                
                for (const [portal, port] of Object.entries(result.ports)) {
                    const isRunning = result.servers.includes(portal);
                    html += '<span class="status ' + (isRunning ? 'running' : 'stopped') + '">';
                    html += portal + ' (Port ' + port + '): ' + (isRunning ? 'Running' : 'Stopped');
                    html += '</span> ';
                }
                
                document.getElementById('systemStatus').innerHTML = html;
            } catch (error) {
                document.getElementById('systemStatus').innerHTML = 'Error: ' + error.message;
            }
        }
        
        async function getFrameworkStats() {
            try {
                const response = await fetch('/api/framework-stats');
                const result = await response.json();
                document.getElementById('frameworkStats').style.display = 'block';
                document.getElementById('frameworkStats').innerHTML = 
                    '<h3>Framework Statistics:</h3><pre>' + JSON.stringify(result, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('frameworkStats').innerHTML = 'Error: ' + error.message;
            }
        }
        
        async function stopServer(portal) {
            if (!confirm('Are you sure you want to stop the ' + portal + ' server?')) {
                return;
            }
            
            try {
                const response = await fetch('/api/stop-server', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({portal: portal})
                });
                
                const result = await response.json();
                document.getElementById('serverResult').style.display = 'block';
                document.getElementById('serverResult').innerHTML = 
                    '<h3>Server Stop Result:</h3><pre>' + JSON.stringify(result, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('serverResult').innerHTML = 'Error: ' + error.message;
            }
        }
        
        // Auto-refresh system status every 30 seconds
        setInterval(getSystemStatus, 30000);
    </script>
</body>
</html>
"""

API_PORTAL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>PQIE API Portal</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #8e44ad; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #7d3c98; }
        .result { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
        pre { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; overflow-x: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 PQIE API Portal</h1>
        
        <div class="section">
            <h2>API Endpoints</h2>
            <button class="btn" onclick="getEndpoints()">Get All Endpoints</button>
            <div id="endpointsResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>Health Check</h2>
            <button class="btn" onclick="getHealth()">Check Health</button>
            <div id="healthResult" class="result" style="display:none;"></div>
        </div>
        
        <div class="section">
            <h2>Portal Links</h2>
            <a href="http://localhost:8080" class="btn">Main Portal</a>
            <a href="http://localhost:8081" class="btn">Ethereum Portal</a>
            <a href="http://localhost:8082" class="btn">Admin Portal</a>
        </div>
        
        <div class="section">
            <h2>API Documentation</h2>
            <h3>Identity Management</h3>
            <pre>
POST /api/generate-identity
Content-Type: application/json
{
    "attributes": {"name": "Alice", "email": "alice@example.com"},
    "user_id": "optional_user_id"
}

POST /api/verify-identity
Content-Type: application/json
{
    "package": {...identity_package...}
}
            </pre>
            
            <h3>Ethereum Integration</h3>
            <pre>
POST /api/register-ethereum
Content-Type: application/json
{
    "attributes": {"name": "Alice", "email": "alice@example.com"},
    "user_id": "optional_user_id"
}

POST /api/verify-ethereum
Content-Type: application/json
{
    "did": "did:pqie:abc123..."
}
            </pre>
            
            <h3>Admin Operations</h3>
            <pre>
GET /api/framework-stats
GET /api/system-status

POST /api/stop-server
Content-Type: application/json
{
    "portal": "main|ethereum|admin|api"
}
            </pre>
        </div>
    </div>

    <script>
        async function getEndpoints() {
            try {
                const response = await fetch('/api/endpoints');
                const result = await response.json();
                document.getElementById('endpointsResult').style.display = 'block';
                document.getElementById('endpointsResult').innerHTML = 
                    '<h3>Available Endpoints:</h3><pre>' + JSON.stringify(result, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('endpointsResult').innerHTML = 'Error: ' + error.message;
            }
        }
        
        async function getHealth() {
            try {
                const response = await fetch('/api/health');
                const result = await response.json();
                document.getElementById('healthResult').style.display = 'block';
                
                let html = '<h3>Health Status:</h3>';
                html += '<p><strong>Overall:</strong> ' + result.overall + '</p>';
                html += '<h4>Services:</h4>';
                
                for (const [service, info] of Object.entries(result.services)) {
                    html += '<p><strong>' + service + ':</strong> Port ' + info.port + ' - ' + info.status + '</p>';
                }
                
                document.getElementById('healthResult').innerHTML = html;
            } catch (error) {
                document.getElementById('healthResult').innerHTML = 'Error: ' + error.message;
            }
        }
        
        // Auto-refresh health every 10 seconds
        setInterval(getHealth, 10000);
    </script>
</body>
</html>
"""

def main():
    """Main function to start all portals"""
    print("🌟 PQIE Multi-Portal Server")
    print("=" * 50)
    print("Starting all PQIE portals on different ports...")
    print()
    
    # Check dependencies
    missing_deps = []
    try:
        import flask
    except ImportError:
        missing_deps.append("flask")
    
    try:
        import flask_cors
    except ImportError:
        missing_deps.append("flask-cors")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstall with: pip install " + " ".join(missing_deps))
        return
    
    # Start multi-portal server
    try:
        server = PQIEMultiPortalServer()
        server.start_all_servers()
    except KeyboardInterrupt:
        print("\n🛑 Servers stopped by user")
    except Exception as e:
        print(f"❌ Error starting servers: {e}")

if __name__ == "__main__":
    main()
