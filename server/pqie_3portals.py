#!/usr/bin/env python3
"""
Simple PQIE Flask Frontend - 3 Portals: Citizen, Government, Ledger
"""

from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from flask_cors import CORS
import secrets
import json
from datetime import datetime

# Configuration
PORTS = {"citizen": 8080, "government": 8081, "ledger": 8082}

# Sample data
users_db = {
    'alice': {'password': 'password123', 'name': 'Alice Johnson', 'type': 'citizen'},
    'bob': {'password': 'password123', 'name': 'Bob Smith', 'type': 'citizen'},
    'admin': {'password': 'gov123', 'name': 'Government Admin', 'type': 'government'}
}

identities_db = {}
government_verifications = {}

# Citizen Portal
citizen_app = Flask("citizen_portal")
citizen_app.secret_key = secrets.token_hex(16)
CORS(citizen_app)

@citizen_app.route('/')
def citizen_home():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>Citizen Portal - PQIE</title>
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
.error { background: #fee; color: #c33; padding: 10px; border-radius: 5px; margin-bottom: 15px; display: none; }
.success { background: #efe; color: #3c3; padding: 10px; border-radius: 5px; margin-bottom: 15px; display: none; }
</style></head>
<body>
<div class="container">
<div class="logo"><h1>👥</h1><p>Citizen Portal</p></div>
<div class="error" id="error"></div>
<div class="success" id="success"></div>
<form id="loginForm">
<div class="form-group"><label for="username">Username</label><input type="text" id="username" name="username" required></div>
<div class="form-group"><label for="password">Password</label><input type="password" id="password" name="password" required></div>
<button type="submit" class="btn">Sign In</button>
</form>
<div style="text-align: center; margin-top: 20px;"><p>Demo users: alice/password123, bob/password123</p></div>
</div>
<script>
document.getElementById('loginForm').addEventListener('submit', async function(e) {
e.preventDefault();
const username = document.getElementById('username').value;
const password = document.getElementById('password').value;
try {
const response = await fetch('/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username, password})});
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
</script></body></html>
''')

@citizen_app.route('/login', methods=['POST'])
def citizen_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username in users_db and users_db[username]['password'] == password:
        session['user'] = username
        session['user_type'] = 'citizen'
        return jsonify({"success": True, "redirect": "/dashboard"})
    else:
        return jsonify({"success": False, "error": "Invalid credentials"})

@citizen_app.route('/dashboard')
def citizen_dashboard():
    if 'user' not in session or session.get('user_type') != 'citizen':
        return redirect(url_for('citizen_home'))
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>Citizen Dashboard - PQIE</title>
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
</style></head>
<body>
<div class="header">
<div class="header-content">
<div class="logo">👥 Citizen Portal</div>
<div class="nav-links">
<a href="/dashboard">Dashboard</a>
<a href="/logout">Logout</a>
</div>
</div>
</div>
<div class="container">
<div class="dashboard-grid">
<div class="card">
<h3>🆔 Create Digital Identity</h3>
<p>Generate a new post-quantum digital identity with advanced cryptographic protection.</p>
<button class="btn" onclick="alert('Identity creation feature coming soon!')">Create Identity</button>
</div>
<div class="card">
<h3>📋 My Identities</h3>
<p>View and manage all your digital identities and their verification status.</p>
<button class="btn" onclick="alert('My identities feature coming soon!')">View Identities</button>
</div>
<div class="card">
<h3>🔐 Security Status</h3>
<p>Your identities are protected with post-quantum cryptography.</p>
<p><strong>Security Level:</strong> 128-bit Post-Quantum</p>
<p><strong>Algorithm:</strong> Ring-LWE</p>
</div>
</div>
</div>
</body></html>
''')

@citizen_app.route('/logout')
def citizen_logout():
    session.clear()
    return redirect(url_for('citizen_home'))

# Government Portal
gov_app = Flask("government_portal")
gov_app.secret_key = secrets.token_hex(16)
CORS(gov_app)

@gov_app.route('/')
def gov_home():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>Government Portal - PQIE</title>
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
.security-notice { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-size: 0.9em; }
.error { background: #fee; color: #c33; padding: 10px; border-radius: 5px; margin-bottom: 15px; display: none; }
</style></head>
<body>
<div class="container">
<div class="logo"><h1>🏛️</h1><p>Government Portal</p></div>
<div class="security-notice"><strong>🔒 Authorized Access Only</strong><br>This portal is for government officials only.</div>
<div class="error" id="error"></div>
<form id="loginForm">
<div class="form-group"><label for="username">Official Username</label><input type="text" id="username" name="username" required></div>
<div class="form-group"><label for="password">Official Password</label><input type="password" id="password" name="password" required></div>
<button type="submit" class="btn">Access Government Portal</button>
</form>
<div style="text-align: center; margin-top: 20px;"><p>Demo: admin/gov123</p></div>
</div>
<script>
document.getElementById('loginForm').addEventListener('submit', async function(e) {
e.preventDefault();
const username = document.getElementById('username').value;
const password = document.getElementById('password').value;
try {
const response = await fetch('/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username, password})});
const result = await response.json();
if (result.success) {
document.getElementById('success').style.display = 'block';
document.getElementById('success').textContent = 'Authentication successful!';
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
</script></body></html>
''')

@gov_app.route('/login', methods=['POST'])
def gov_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
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
    
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>Government Dashboard - PQIE</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; }
.header { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
.logo { font-size: 1.5em; font-weight: bold; }
.nav-links a { color: white; text-decoration: none; margin-left: 20px; font-weight: 500; }
.container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }
.stat-card { background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; }
.stat-number { font-size: 2.5em; font-weight: bold; color: #f093fb; margin-bottom: 10px; }
.stat-label { color: #666; font-size: 1.1em; }
</style></head>
<body>
<div class="header">
<div class="header-content">
<div class="logo">🏛️ Government Portal</div>
<div class="nav-links">
<a href="/dashboard">Dashboard</a>
<a href="/logout">Logout</a>
</div>
</div>
</div>
<div class="container">
<div class="stats-grid">
<div class="stat-card"><div class="stat-number">0</div><div class="stat-label">Pending Verifications</div></div>
<div class="stat-card"><div class="stat-number">0</div><div class="stat-label">Verified Identities</div></div>
<div class="stat-card"><div class="stat-number">0</div><div class="stat-label">Rejected Applications</div></div>
<div class="stat-card"><div class="stat-number">0</div><div class="stat-label">Total Applications</div></div>
</div>
</div>
</body></html>
''')

@gov_app.route('/logout')
def gov_logout():
    session.clear()
    return redirect(url_for('gov_home'))

# Ledger Portal
ledger_app = Flask("ledger_portal")
ledger_app.secret_key = secrets.token_hex(16)
CORS(ledger_app)

@ledger_app.route('/')
def ledger_home():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head><title>Ledger Portal - PQIE</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); min-height: 100vh; }
.header { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); color: white; padding: 20px 0; }
.header-content { max-width: 1200px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }
.logo { font-size: 1.5em; font-weight: bold; }
.container { max-width: 1200px; margin: 0 auto; padding: 40px 20px; }
.hero { text-align: center; color: white; margin-bottom: 50px; }
.hero h1 { font-size: 3em; margin-bottom: 20px; }
.hero p { font-size: 1.2em; opacity: 0.9; }
.search-section { background: rgba(255,255,255,0.95); border-radius: 20px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); margin-bottom: 40px; }
.search-form { display: flex; gap: 15px; margin-bottom: 20px; }
.search-input { flex: 1; padding: 15px; border: 2px solid #e1e1e1; border-radius: 10px; font-size: 16px; }
.search-btn { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 15px 30px; border: none; border-radius: 10px; cursor: pointer; font-weight: 600; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
.stat-card { background: rgba(255,255,255,0.9); border-radius: 15px; padding: 25px; text-align: center; }
.stat-number { font-size: 2em; font-weight: bold; color: #11998e; }
.stat-label { color: #666; margin-top: 5px; }
</style></head>
<body>
<div class="header">
<div class="header-content">
<div class="logo">📊 Ledger Portal</div>
</div>
</div>
<div class="container">
<div class="hero">
<h1>🔍 Blockchain Explorer</h1>
<p>Search and verify digital identities on the PQIE blockchain</p>
</div>
<div class="search-section">
<h3>Search Identities</h3>
<form class="search-form">
<input type="text" class="search-input" placeholder="Enter DID or search term...">
<button type="submit" class="search-btn">Search</button>
</form>
<div class="stats">
<div class="stat-card"><div class="stat-number">0</div><div class="stat-label">Total Identities</div></div>
<div class="stat-card"><div class="stat-number">0</div><div class="stat-label">Verified</div></div>
<div class="stat-card"><div class="stat-number">0</div><div class="stat-label">Pending</div></div>
</div>
</div>
</div>
</body></html>
''')

if __name__ == "__main__":
    import threading
    import time
    
    print("🌟 Starting PQIE 3-Portal System...")
    print("=" * 50)
    
    def run_app(app, port, name):
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
        print(f"🚀 {name} Portal started on http://localhost:{port}")
    
    # Start all portals
    threads = []
    for app, port, name in [
        (citizen_app, PORTS['citizen'], 'Citizen'),
        (gov_app, PORTS['government'], 'Government'),
        (ledger_app, PORTS['ledger'], 'Ledger')
    ]:
        thread = threading.Thread(target=run_app, args=(app, port, name), daemon=True)
        thread.start()
        threads.append(thread)
        time.sleep(1)
    
    print(f"\n✅ All portals started!")
    print(f"👥 Citizen Portal: http://localhost:{PORTS['citizen']}")
    print(f"🏛️ Government Portal: http://localhost:{PORTS['government']}")
    print(f"📊 Ledger Portal: http://localhost:{PORTS['ledger']}")
    print("\nPress Ctrl+C to stop all servers")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Servers stopped by user")
