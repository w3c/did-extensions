#!/usr/bin/env python3
"""
PQIE Flask Frontend System
3 Portals: Citizen, Government, and Ledger with modern UI
"""

import asyncio
import json
import base64
import secrets
import threading
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
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
    "citizen": 8080,    # Citizen Portal
    "government": 8081,  # Government Portal  
    "ledger": 8082       # Ledger Portal
}

class PQIEFlaskFrontend:
    """
    Flask Frontend with 3 specialized portals
    """
    
    def __init__(self):
        self.pqie_framework = None
        self.ethereum_integration = None
        self.ethereum_pqie = None
        self.servers = {}
        self.apps = {}
        self.running = False
        self.users_db = {}  # Simple user database
        self.identities_db = {}  # Identity storage
        self.government_verifications = {}  # Government verification records
        
        # Initialize PQIE if available
        if PQIE_AVAILABLE:
            try:
                self.pqie_framework = PQIEFramework()
                print("✅ PQIE Framework initialized")
                
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
        """Create Flask apps for each specialized portal"""
        
        # Citizen Portal
        citizen_app = Flask("citizen_portal")
        citizen_app.secret_key = secrets.token_hex(16)
        CORS(citizen_app)
        
        @citizen_app.route('/')
        def citizen_home():
            return render_template_string(CITIZEN_PORTAL_TEMPLATE)
        
        @citizen_app.route('/login', methods=['POST'])
        def citizen_login():
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            # Simple authentication
            if username in self.users_db and self.users_db[username]['password'] == password:
                session['user'] = username
                session['user_type'] = 'citizen'
                return jsonify({"success": True, "redirect": "/dashboard"})
            else:
                return jsonify({"success": False, "error": "Invalid credentials"})
        
        @citizen_app.route('/dashboard')
        def citizen_dashboard():
            if 'user' not in session or session.get('user_type') != 'citizen':
                return redirect(url_for('citizen_home'))
            return render_template_string(CITIZEN_DASHBOARD_TEMPLATE)
        
        @citizen_app.route('/create-identity', methods=['POST'])
        def create_citizen_identity():
            if 'user' not in session:
                return jsonify({"error": "Not logged in"}), 401
            
            try:
                data = request.get_json()
                user_attributes = data.get('attributes', {})
                
                if not self.pqie_framework:
                    return jsonify({"error": "PQIE Framework not available"}), 500
                
                # Generate identity
                identity_package = self.pqie_framework.generate_complete_identity_package(
                    user_attributes, session['user']
                )
                
                # Store identity
                self.identities_db[identity_package['did']] = {
                    'package': identity_package,
                    'owner': session['user'],
                    'created_at': datetime.utcnow().isoformat(),
                    'status': 'pending_verification'
                }
                
                return jsonify({
                    "success": True,
                    "identity": identity_package,
                    "message": "Identity created successfully. Pending government verification."
                })
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @citizen_app.route('/my-identities')
        def my_identities():
            if 'user' not in session:
                return redirect(url_for('citizen_home'))
            
            user_identities = [
                {'did': did, **data} 
                for did, data in self.identities_db.items() 
                if data['owner'] == session['user']
            ]
            
            return render_template_string(MY_IDENTITIES_TEMPLATE, identities=user_identities)
        
        @citizen_app.route('/logout')
        def citizen_logout():
            session.clear()
            return redirect(url_for('citizen_home'))
        
        self.apps["citizen"] = citizen_app
        
        # Government Portal
        gov_app = Flask("government_portal")
        gov_app.secret_key = secrets.token_hex(16)
        CORS(gov_app)
        
        @gov_app.route('/')
        def gov_home():
            return render_template_string(GOVERNMENT_PORTAL_TEMPLATE)
        
        @gov_app.route('/login', methods=['POST'])
        def gov_login():
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            
            # Government authentication
            if username == 'admin' and password == 'gov123':
                session['user'] = username
                session['user_type'] = 'government'
                return jsonify({"success": True, "redirect": "/dashboard"})
            else:
                return jsonify({"success": False, "error": "Invalid credentials"})
        
        @gov_app.route('/dashboard')
        def gov_dashboard():
            if 'user' not in session or session.get('user_type') != 'government':
                return redirect(url_for('gov_home'))
            return render_template_string(GOV_DASHBOARD_TEMPLATE)
        
        @gov_app.route('/pending-identities')
        def pending_identities():
            if 'user' not in session or session.get('user_type') != 'government':
                return redirect(url_for('gov_home'))
            
            pending = [
                {'did': did, **data} 
                for did, data in self.identities_db.items() 
                if data['status'] == 'pending_verification'
            ]
            
            return render_template_string(PENDING_IDENTITIES_TEMPLATE, identities=pending)
        
        @gov_app.route('/verify-identity/<did>', methods=['POST'])
        def verify_identity(did):
            if 'user' not in session or session.get('user_type') != 'government':
                return jsonify({"error": "Unauthorized"}), 401
            
            try:
                data = request.get_json()
                action = data.get('action')  # 'approve' or 'reject'
                reason = data.get('reason', '')
                
                if did not in self.identities_db:
                    return jsonify({"error": "Identity not found"}), 404
                
                # Update identity status
                if action == 'approve':
                    self.identities_db[did]['status'] = 'verified'
                    self.identities_db[did]['verified_at'] = datetime.utcnow().isoformat()
                    
                    # Record government verification
                    self.government_verifications[did] = {
                        'verified_by': session['user'],
                        'verified_at': datetime.utcnow().isoformat(),
                        'status': 'approved'
                    }
                    
                    return jsonify({"success": True, "message": "Identity approved"})
                    
                elif action == 'reject':
                    self.identities_db[did]['status'] = 'rejected'
                    self.identities_db[did]['rejected_at'] = datetime.utcnow().isoformat()
                    self.identities_db[did]['rejection_reason'] = reason
                    
                    self.government_verifications[did] = {
                        'verified_by': session['user'],
                        'verified_at': datetime.utcnow().isoformat(),
                        'status': 'rejected',
                        'reason': reason
                    }
                    
                    return jsonify({"success": True, "message": "Identity rejected"})
                    
                else:
                    return jsonify({"error": "Invalid action"}), 400
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @gov_app.route('/logout')
        def gov_logout():
            session.clear()
            return redirect(url_for('gov_home'))
        
        self.apps["government"] = gov_app
        
        # Ledger Portal
        ledger_app = Flask("ledger_portal")
        ledger_app.secret_key = secrets.token_hex(16)
        CORS(ledger_app)
        
        @ledger_app.route('/')
        def ledger_home():
            return render_template_string(LEDGER_PORTAL_TEMPLATE)
        
        @ledger_app.route('/explorer')
        def ledger_explorer():
            return render_template_string(LEDGER_EXPLORER_TEMPLATE, identities=self.identities_db)
        
        @ledger_app.route('/search', methods=['POST'])
        def search_ledger():
            try:
                data = request.get_json()
                search_term = data.get('search_term', '').lower()
                
                results = []
                for did, identity_data in self.identities_db.items():
                    if search_term in did.lower():
                        results.append({
                            'did': did,
                            'owner': identity_data['owner'],
                            'status': identity_data['status'],
                            'created_at': identity_data['created_at']
                        })
                
                return jsonify({"success": True, "results": results})
                
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @ledger_app.route('/identity/<did>')
        def identity_details(did):
            if did not in self.identities_db:
                return render_template_string(IDENTITY_NOT_FOUND_TEMPLATE, did=did)
            
            identity_data = self.identities_db[did]
            verification_data = self.government_verifications.get(did, {})
            
            return render_template_string(IDENTITY_DETAILS_TEMPLATE, 
                                   did=did, 
                                   identity=identity_data, 
                                   verification=verification_data)
        
        @ledger_app.route('/api/stats')
        def ledger_stats():
            stats = {
                'total_identities': len(self.identities_db),
                'verified_identities': len([i for i in self.identities_db.values() if i['status'] == 'verified']),
                'pending_identities': len([i for i in self.identities_db.values() if i['status'] == 'pending_verification']),
                'rejected_identities': len([i for i in self.identities_db.values() if i['status'] == 'rejected']),
                'total_verifications': len(self.government_verifications)
            }
            return jsonify(stats)
        
        self.apps["ledger"] = ledger_app
    
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
        print("🌟 Starting PQIE Flask Frontend System...")
        print("=" * 50)
        
        # Add sample users
        self.users_db = {
            'alice': {'password': 'password123', 'name': 'Alice Johnson', 'type': 'citizen'},
            'bob': {'password': 'password123', 'name': 'Bob Smith', 'type': 'citizen'},
            'admin': {'password': 'gov123', 'name': 'Government Admin', 'type': 'government'}
        }
        
        self.start_time = time.time()
        
        # Start all servers
        for portal, port in PORTS.items():
            self.start_server(portal, port)
            time.sleep(1)
        
        print("\n✅ All servers started!")
        print(f"👥 Citizen Portal: http://localhost:{PORTS['citizen']}")
        print(f"🏛️ Government Portal: http://localhost:{PORTS['government']}")
        print(f"📊 Ledger Portal: http://localhost:{PORTS['ledger']}")
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
        print("✅ All servers stopped")

# HTML Templates
CITIZEN_PORTAL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Citizen Portal - PQIE</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); padding: 40px; max-width: 400px; width: 90%; }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { color: #667eea; font-size: 2.5em; margin-bottom: 10px; }
        .logo p { color: #666; font-size: 1.1em; }
        .form-group { margin-bottom: 25px; }
        .form-group label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; }
        .form-group input { width: 100%; padding: 15px; border: 2px solid #e1e1e1; border-radius: 10px; font-size: 16px; transition: all 0.3s; }
        .form-group input:focus { border-color: #667eea; outline: none; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
        .btn { width: 100%; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: 600; cursor: pointer; transition: transform 0.2s; }
        .btn:hover { transform: translateY(-2px); }
        .btn:active { transform: translateY(0); }
        .register-link { text-align: center; margin-top: 20px; }
        .register-link a { color: #667eea; text-decoration: none; font-weight: 600; }
        .register-link a:hover { text-decoration: underline; }
        .error { background: #fee; color: #c33; padding: 10px; border-radius: 5px; margin-bottom: 15px; display: none; }
        .success { background: #efe; color: #3c3; padding: 10px; border-radius: 5px; margin-bottom: 15px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>👥</h1>
            <p>Citizen Portal</p>
        </div>
        
        <div class="error" id="error"></div>
        <div class="success" id="success"></div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn">Sign In</button>
        </form>
        
        <div class="register-link">
            <p>New user? <a href="#" onclick="showRegistration()">Register here</a></p>
        </div>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('success').style.display = 'block';
                    document.getElementById('success').textContent = 'Login successful! Redirecting...';
                    setTimeout(() => window.location.href = result.redirect, 1500);
                } else {
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('error').textContent = result.error;
                }
            } catch (error) {
                document.getElementById('error').style.display = 'block';
                document.getElementById('error').textContent = 'Login failed: ' + error.message;
            }
        });
        
        function showRegistration() {
            alert('Registration feature coming soon! For now, use: alice/password123 or bob/password123');
        }
    </script>
</body>
</html>
"""

CITIZEN_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Citizen Dashboard - PQIE</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
        .logo { font-size: 1.5em; font-weight: bold; }
        .nav-links a { color: white; text-decoration: none; margin-left: 20px; font-weight: 500; }
        .container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 30px; margin-bottom: 40px; }
        .card { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); transition: transform 0.3s; }
        .card:hover { transform: translateY(-5px); }
        .card h3 { color: #333; margin-bottom: 15px; font-size: 1.3em; }
        .card p { color: #666; line-height: 1.6; }
        .btn { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 25px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; text-decoration: none; display: inline-block; margin-top: 15px; transition: transform 0.2s; }
        .btn:hover { transform: translateY(-2px); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; }
        .form-group input, .form-group textarea { width: 100%; padding: 12px; border: 2px solid #e1e1e1; border-radius: 8px; font-size: 14px; }
        .form-group textarea { height: 100px; resize: vertical; }
        .message { padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">👥 Citizen Portal</div>
            <div class="nav-links">
                <a href="/dashboard">Dashboard</a>
                <a href="/my-identities">My Identities</a>
                <a href="/logout">Logout</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="dashboard-grid">
            <div class="card">
                <h3>🆔 Create New Identity</h3>
                <p>Generate a new post-quantum digital identity with advanced cryptographic protection.</p>
                <button class="btn" onclick="showIdentityForm()">Create Identity</button>
            </div>
            
            <div class="card">
                <h3>📋 My Identities</h3>
                <p>View and manage all your digital identities and their verification status.</p>
                <a href="/my-identities" class="btn">View Identities</a>
            </div>
            
            <div class="card">
                <h3>🔐 Security Status</h3>
                <p>Your identities are protected with post-quantum cryptography.</p>
                <p><strong>Security Level:</strong> 128-bit Post-Quantum</p>
                <p><strong>Algorithm:</strong> Ring-LWE</p>
            </div>
        </div>
        
        <div id="identityForm" style="display: none;">
            <div class="card">
                <h3>Create New Digital Identity</h3>
                <div id="formMessage"></div>
                
                <form id="createIdentityForm">
                    <div class="form-group">
                        <label for="fullName">Full Name</label>
                        <input type="text" id="fullName" name="fullName" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email Address</label>
                        <input type="email" id="email" name="email" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="phone">Phone Number</label>
                        <input type="tel" id="phone" name="phone" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="address">Residential Address</label>
                        <textarea id="address" name="address" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="dob">Date of Birth</label>
                        <input type="date" id="dob" name="dob" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="nationalId">National ID Number</label>
                        <input type="text" id="nationalId" name="nationalId" required>
                    </div>
                    
                    <button type="submit" class="btn">Generate Identity</button>
                    <button type="button" class="btn" onclick="hideIdentityForm()" style="background: #6c757d; margin-left: 10px;">Cancel</button>
                </form>
            </div>
        </div>
    </div>

    <script>
        function showIdentityForm() {
            document.getElementById('identityForm').style.display = 'block';
            document.getElementById('identityForm').scrollIntoView({ behavior: 'smooth' });
        }
        
        function hideIdentityForm() {
            document.getElementById('identityForm').style.display = 'none';
        }
        
        function showMessage(message, type) {
            const messageDiv = document.getElementById('formMessage');
            messageDiv.className = 'message ' + type;
            messageDiv.textContent = message;
            messageDiv.style.display = 'block';
            
            setTimeout(() => {
                messageDiv.style.display = 'none';
            }, 5000);
        }
        
        document.getElementById('createIdentityForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const attributes = {
                fullName: formData.get('fullName'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                address: formData.get('address'),
                dob: formData.get('dob'),
                nationalId: formData.get('nationalId')
            };
            
            try {
                const response = await fetch('/create-identity', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({attributes})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showMessage(result.message, 'success');
                    e.target.reset();
                    hideIdentityForm();
                } else {
                    showMessage(result.error, 'error');
                }
            } catch (error) {
                showMessage('Failed to create identity: ' + error.message, 'error');
            }
        });
    </script>
</body>
</html>
"""

GOVERNMENT_PORTAL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Government Portal - PQIE</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); padding: 40px; max-width: 400px; width: 90%; }
        .logo { text-align: center; margin-bottom: 30px; }
        .logo h1 { color: #f093fb; font-size: 2.5em; margin-bottom: 10px; }
        .logo p { color: #666; font-size: 1.1em; }
        .form-group { margin-bottom: 25px; }
        .form-group label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; }
        .form-group input { width: 100%; padding: 15px; border: 2px solid #e1e1e1; border-radius: 10px; font-size: 16px; transition: all 0.3s; }
        .form-group input:focus { border-color: #f093fb; outline: none; box-shadow: 0 0 0 3px rgba(240, 147, 251, 0.1); }
        .btn { width: 100%; padding: 15px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border: none; border-radius: 10px; font-size: 18px; font-weight: 600; cursor: pointer; transition: transform 0.2s; }
        .btn:hover { transform: translateY(-2px); }
        .btn:active { transform: translateY(0); }
        .security-notice { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 0.9em; }
        .error { background: #fee; color: #c33; padding: 10px; border-radius: 5px; margin-bottom: 15px; display: none; }
        .success { background: #efe; color: #3c3; padding: 10px; border-radius: 5px; margin-bottom: 15px; display: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">
            <h1>🏛️</h1>
            <p>Government Portal</p>
        </div>
        
        <div class="security-notice">
            <strong>🔒 Authorized Access Only</strong><br>
            This portal is for government officials only. Unauthorized access is prohibited and will be prosecuted.
        </div>
        
        <div class="error" id="error"></div>
        <div class="success" id="success"></div>
        
        <form id="loginForm">
            <div class="form-group">
                <label for="username">Official Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Official Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <button type="submit" class="btn">Access Government Portal</button>
        </form>
    </div>

    <script>
        document.getElementById('loginForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({username, password})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('success').style.display = 'block';
                    document.getElementById('success').textContent = 'Authentication successful! Redirecting...';
                    setTimeout(() => window.location.href = result.redirect, 1500);
                } else {
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('error').textContent = result.error;
                }
            } catch (error) {
                document.getElementById('error').style.display = 'block';
                document.getElementById('error').textContent = 'Authentication failed: ' + error.message;
            }
        });
    </script>
</body>
</html>
"""

def main():
    """Main function to start all portals"""
    print("🌟 PQIE Flask Frontend System")
    print("=" * 50)
    print("Starting 3 specialized portals...")
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
    
    # Start frontend system
    try:
        frontend = PQIEFlaskFrontend()
        frontend.start_all_servers()
    except KeyboardInterrupt:
        print("\n🛑 Servers stopped by user")
    except Exception as e:
        print(f"❌ Error starting servers: {e}")

if __name__ == "__main__":
    main()
