# PQIE Multi-Portal System

## Overview

The PQIE Multi-Portal System provides a unified interface to run all PQIE services on different ports with comprehensive web interfaces.

## Portal Structure

### 📱 Main Portal (Port 8080)
- **URL**: http://localhost:8080
- **Features**: 
  - Generate PQIE identities
  - Verify identity packages
  - Access to other portals
- **API Endpoints**:
  - `POST /api/generate-identity` - Generate new identity
  - `POST /api/verify-identity` - Verify existing identity
  - `GET /api/status` - Portal status

### 🔗 Ethereum Portal (Port 8081)
- **URL**: http://localhost:8081
- **Features**:
  - Register identities on Ethereum blockchain
  - Verify Ethereum-based identities
  - View Ethereum statistics
- **API Endpoints**:
  - `POST /api/register-ethereum` - Register identity on Ethereum
  - `POST /api/verify-ethereum` - Verify Ethereum identity
  - `GET /api/ethereum-stats` - Get blockchain statistics
  - `GET /api/status` - Portal status

### ⚙️ Admin Portal (Port 8082)
- **URL**: http://localhost:8082
- **Features**:
  - System monitoring and status
  - Framework statistics
  - Server management (start/stop individual portals)
  - Performance metrics
- **API Endpoints**:
  - `GET /api/framework-stats` - Get PQIE framework statistics
  - `GET /api/system-status` - Get system-wide status
  - `POST /api/stop-server` - Stop specific server
  - `GET /api/status` - Portal status

### 📡 API Portal (Port 8083)
- **URL**: http://localhost:8083
- **Features**:
  - Complete API documentation
  - Health check for all services
  - Endpoint discovery
  - Real-time service status
- **API Endpoints**:
  - `GET /api/endpoints` - Get all available endpoints
  - `GET /api/health` - Health check for all services
  - `GET /api/status` - Portal status

## Quick Start

### Method 1: Using Startup Script (Recommended)
```bash
./start_pqie_portals.sh
```

### Method 2: Manual Start
```bash
# Install dependencies
pip install -r requirements_pqie.txt

# Start all portals
python3 pqie_multi_portal.py
```

## Dependencies

Required Python packages (included in `requirements_pqie.txt`):
- `numpy>=1.21.0` - Numerical computations
- `cryptography>=3.4.8` - Cryptographic operations
- `web3>=5.31.0` - Ethereum Web3 integration
- `eth-account>=0.8.0` - Ethereum account management
- `solc>=0.8.0` - Solidity compiler
- `flask>=2.3.0` - Web framework
- `flask-cors>=4.0.0` - Cross-origin resource sharing

## Usage Examples

### Generate Identity via Main Portal
```bash
curl -X POST http://localhost:8080/api/generate-identity \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "name": "Alice Johnson",
      "email": "alice@example.com",
      "phone": "+1234567890"
    },
    "user_id": "alice_123"
  }'
```

### Register on Ethereum via Ethereum Portal
```bash
curl -X POST http://localhost:8081/api/register-ethereum \
  -H "Content-Type: application/json" \
  -d '{
    "attributes": {
      "name": "Alice Johnson",
      "email": "alice@example.com"
    },
    "user_id": "alice_ethereum"
  }'
```

### Get System Status via Admin Portal
```bash
curl http://localhost:8082/api/system-status
```

### Check Health via API Portal
```bash
curl http://localhost:8083/api/health
```

## Features

### 🔐 Security
- Post-quantum cryptography (Ring-LWE)
- Ethereum blockchain integration
- Identity verification and validation
- Secure token generation

### 📊 Monitoring
- Real-time system status
- Performance metrics
- Service health checks
- Transaction tracking

### 🎛️ Management
- Individual server control
- Dynamic configuration
- Error handling and recovery
- Graceful shutdown

### 🔗 Integration
- RESTful APIs
- Cross-origin support
- JSON data format
- Web-based interfaces

## Configuration

### Port Configuration
Ports can be modified in `pqie_multi_portal.py`:
```python
PORTS = {
    "main": 8080,      # Main PQIE Portal
    "ethereum": 8081,  # Ethereum Integration Portal
    "admin": 8082,     # Admin Portal
    "api": 8083        # REST API Portal
}
```

### Ethereum Configuration
Update Ethereum settings in `ethereum_pqie_integration.py`:
```python
eth_integration = EthereumPQIEIntegration(
    web3_provider="http://localhost:8545",  # Your Ethereum node
    private_key="your_private_key_here"        # Your private key
)
```

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8080
   
   # Kill the process
   kill -9 <PID>
   ```

2. **Missing Dependencies**
   ```bash
   # Install all dependencies
   pip install -r requirements_pqie.txt
   ```

3. **Ethereum Connection Failed**
   - Ensure Ethereum node is running on specified port
   - Check private key format
   - Verify network connectivity

4. **PQIE Framework Not Available**
   - Check if all required packages are installed
   - Verify numpy installation
   - Check import paths

### Logs
Each portal logs to console with:
- 🚀 Server startup messages
- ✅ Success indicators
- ❌ Error messages
- 📊 Status updates

### Performance Tips
- Use virtual environment for isolation
- Monitor system resources
- Adjust timeout settings for large operations
- Use HTTPS in production

## Development

### Adding New Portals
1. Create new Flask app in `_create_portal_apps()`
2. Add port configuration to `PORTS` dict
3. Implement routes and templates
4. Start server in `start_server()`

### Extending APIs
1. Add new route handlers
2. Update API documentation
3. Add error handling
4. Test with curl/Postman

### Custom Templates
HTML templates are embedded in the Python file. To modify:
1. Edit template strings in `pqie_multi_portal.py`
2. Restart servers
3. Clear browser cache

## Production Deployment

### Security Considerations
- Use HTTPS with SSL certificates
- Implement authentication for admin portal
- Rate limiting for API endpoints
- Input validation and sanitization
- Environment variables for sensitive data

### Performance Optimization
- Use production WSGI server (Gunicorn)
- Enable caching
- Load balancing
- Database optimization
- Monitor resource usage

### Monitoring
- Set up logging
- Health check endpoints
- Metrics collection
- Alert systems
- Backup procedures

## Support

For issues and support:
1. Check console logs for error messages
2. Verify all dependencies are installed
3. Ensure ports are available
4. Test individual components
5. Review API documentation

---

**PQIE Multi-Portal System** - Complete post-quantum identity management with web interfaces.
