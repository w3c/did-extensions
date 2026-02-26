# Government Dashboard Template
GOV_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Government Dashboard - PQIE</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
        .actions { background: white; border-radius: 15px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }
        .btn { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 12px 25px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; text-decoration: none; display: inline-block; margin: 10px 5px; transition: transform 0.2s; }
        .btn:hover { transform: translateY(-2px); }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">🏛️ Government Portal</div>
            <div class="nav-links">
                <a href="/dashboard">Dashboard</a>
                <a href="/pending-identities">Pending Verifications</a>
                <a href="/logout">Logout</a>
            </div>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="pendingCount">0</div>
                <div class="stat-label">Pending Verifications</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="verifiedCount">0</div>
                <div class="stat-label">Verified Identities</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="rejectedCount">0</div>
                <div class="stat-label">Rejected Applications</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="totalCount">0</div>
                <div class="stat-label">Total Applications</div>
            </div>
        </div>
        
        <div class="actions">
            <h3>Quick Actions</h3>
            <a href="/pending-identities" class="btn">Review Pending Applications</a>
            <a href="/explorer" class="btn">View All Identities</a>
        </div>
    </div>

    <script>
        // Load statistics
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('pendingCount').textContent = stats.pending_identities;
                document.getElementById('verifiedCount').textContent = stats.verified_identities;
                document.getElementById('rejectedCount').textContent = stats.rejected_identities;
                document.getElementById('totalCount').textContent = stats.total_identities;
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }
        
        loadStats();
        setInterval(loadStats, 30000); // Refresh every 30 seconds
    </script>
</body>
</html>
"""

# Ledger Portal Template
LEDGER_PORTAL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Ledger Portal - PQIE</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
        .btn { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 12px 25px; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; text-decoration: none; display: inline-block; margin: 10px 5px; }
    </style>
</head>
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
            <form class="search-form" id="searchForm">
                <input type="text" class="search-input" id="searchInput" placeholder="Enter DID or search term...">
                <button type="submit" class="search-btn">Search</button>
            </form>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number" id="totalIdentities">0</div>
                    <div class="stat-label">Total Identities</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="verifiedIdentities">0</div>
                    <div class="stat-label">Verified</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="pendingIdentities">0</div>
                    <div class="stat-label">Pending</div>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="/explorer" class="btn">View All Identities</a>
            </div>
        </div>
    </div>

    <script>
        document.getElementById('searchForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const searchTerm = document.getElementById('searchInput').value;
            
            if (searchTerm.trim()) {
                // Redirect to explorer with search
                window.location.href = `/explorer?search=${encodeURIComponent(searchTerm)}`;
            }
        });
        
        // Load stats
        async function loadStats() {
            try {
                const response = await fetch('/api/stats');
                const stats = await response.json();
                
                document.getElementById('totalIdentities').textContent = stats.total_identities;
                document.getElementById('verifiedIdentities').textContent = stats.verified_identities;
                document.getElementById('pendingIdentities').textContent = stats.pending_identities;
            } catch (error) {
                console.error('Failed to load stats:', error);
            }
        }
        
        loadStats();
    </script>
</body>
</html>
"""

# Additional templates would continue here...
print("Templates added to pqie_flask_frontend.py")
