# Manual Server Run Guide

## Step-by-Step Instructions to Run Servers Manually

### Prerequisites
- Python 3.7+ installed
- All dependencies installed (`pip install -r requirements.txt` if available)
- IPFS daemon running (optional, for IPFS features)

---

## Method 1: Run Individual Servers in Separate Terminals

### Terminal 1: Citizen Portal Server
```bash
cd /Users/user/DPC6_aadhaar-kyc-system
python3 server/citizen_portal_server.py
```
- **Port:** 8082
- **URL:** http://localhost:8082
- **Keep this terminal open**

### Terminal 2: Government Portal Server
```bash
cd /Users/user/DPC6_aadhaar-kyc-system
python3 server/government_portal_server.py
```
- **Port:** 8081
- **URL:** http://localhost:8081
- **Keep this terminal open**

### Terminal 3: Ledger Explorer Server
```bash
cd /Users/user/DPC6_aadhaar-kyc-system
python3 server/ledger_explorer_server.py
```
- **Port:** 8083
- **URL:** http://localhost:8083
- **Keep this terminal open**

### Terminal 4: SDIS Public Resolver (Optional)
```bash
cd /Users/user/DPC6_aadhaar-kyc-system
python3 server/sdis_public_resolver_perfect.py
```
- **Port:** 8085
- **URL:** http://localhost:8085
- **Keep this terminal open**

### Terminal 5: Auto Identity Token API (Optional)
```bash
cd /Users/user/DPC6_aadhaar-kyc-system
python3 server/auto_identity_token_integration_server.py
```
- **Port:** 8080
- **URL:** http://localhost:8080
- **Keep this terminal open**

---

## Method 2: Run in Background (Background Jobs)

### Run All Servers in Background
```bash
cd /Users/user/DPC6_aadhaar-kyc-system

# Start Citizen Portal (background)
python3 server/citizen_portal_server.py > /tmp/citizen_portal.log 2>&1 &

# Start Government Portal (background)
python3 server/government_portal_server.py > /tmp/gov_portal.log 2>&1 &

# Start Ledger Explorer (background)
python3 server/ledger_explorer_server.py > /tmp/ledger_explorer.log 2>&1 &

# Start SDIS Resolver (background)
python3 server/sdis_public_resolver_perfect.py > /tmp/sdis_resolver.log 2>&1 &

# Start Auto Token API (background)
python3 server/auto_identity_token_integration_server.py > /tmp/auto_token.log 2>&1 &
```

### Check Running Servers
```bash
ps aux | grep "python.*server" | grep -v grep
```

### View Logs
```bash
# View Citizen Portal logs
tail -f /tmp/citizen_portal.log

# View Government Portal logs
tail -f /tmp/gov_portal.log

# View Ledger Explorer logs
tail -f /tmp/ledger_explorer.log

# View SDIS Resolver logs
tail -f /tmp/sdis_resolver.log

# View Auto Token API logs
tail -f /tmp/auto_token.log
```

### Stop All Servers
```bash
pkill -f "python.*server"
```

---

## Method 3: Using the start_servers.py Script

### Run All Servers Together (Foreground)
```bash
cd /Users/user/DPC6_aadhaar-kyc-system
python3 start_servers.py
```

**Note:** This runs all servers in the foreground. Press `Ctrl+C` to stop all servers.

---

## Verification Steps

### 1. Check if Servers are Running
```bash
# Check all Python server processes
ps aux | grep "python.*server" | grep -v grep

# Check specific ports
lsof -i :8082  # Citizen Portal
lsof -i :8081  # Government Portal
lsof -i :8083  # Ledger Explorer
lsof -i :8085  # SDIS Resolver
lsof -i :8080  # Auto Token API
```

### 2. Test Server Endpoints
```bash
# Test Citizen Portal
curl http://localhost:8082/

# Test Government Portal
curl http://localhost:8081/

# Test Ledger Explorer
curl http://localhost:8083/

# Test Auto Token API Health
curl http://localhost:8080/health

# Test SDIS Resolver
curl http://localhost:8085/
```

### 3. Open in Browser
- **Citizen Portal:** http://localhost:8082
- **Government Portal:** http://localhost:8081
- **Ledger Explorer:** http://localhost:8083
- **VC Viewer:** http://localhost:8083/vc-viewer

---

## Troubleshooting

### Port Already in Use
If you get "Address already in use" error:
```bash
# Find process using the port
lsof -i :8082  # Replace with your port number

# Kill the process
kill -9 <PID>
```

### Server Won't Start
1. Check Python version: `python3 --version` (needs 3.7+)
2. Check dependencies: Ensure all required packages are installed
3. Check logs for errors:
   ```bash
   tail -f /tmp/citizen_portal.log
   ```

### Import Errors
```bash
# Make sure you're in the project directory
cd /Users/user/DPC6_aadhaar-kyc-system

# Install dependencies if needed
pip3 install aiohttp pathlib
```

---

## Quick Start Commands

### Minimum Required Servers (Core Functionality)
```bash
cd /Users/user/DPC6_aadhaar-kyc-system

# Terminal 1
python3 server/citizen_portal_server.py

# Terminal 2
python3 server/government_portal_server.py

# Terminal 3
python3 server/ledger_explorer_server.py
```

### All Servers (Full System)
```bash
cd /Users/user/DPC6_aadhaar-kyc-system

# Run in separate terminals or use background method
python3 server/citizen_portal_server.py
python3 server/government_portal_server.py
python3 server/ledger_explorer_server.py
python3 server/sdis_public_resolver_perfect.py
python3 server/auto_identity_token_integration_server.py
```

---

## Server Details

| Server | Port | File | Description |
|--------|------|------|-------------|
| Citizen Portal | 8082 | `server/citizen_portal_server.py` | Main citizen interface |
| Government Portal | 8081 | `server/government_portal_server.py` | Government approval interface |
| Ledger Explorer | 8083 | `server/ledger_explorer_server.py` | Ledger visualization |
| SDIS Resolver | 8085 | `server/sdis_public_resolver_perfect.py` | DID resolution service |
| Auto Token API | 8080 | `server/auto_identity_token_integration_server.py` | Token generation API |

---

## Notes

- **Order of Starting:** Start servers in any order, but wait 2-3 seconds between starts
- **Port Conflicts:** Each server needs its own port
- **Logs:** All logs are written to `/tmp/*.log` when run in background
- **Data Files:** All data is stored in `data/` directory
- **IPFS:** Optional but recommended for full functionality

