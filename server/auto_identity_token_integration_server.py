#!/usr/bin/env python3
"""
Auto Identity Token Integration Server
RESTful API server for Auto Identity Token generation, verification, and management
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from aiohttp import web, web_request

# Import the Auto Identity Token Generator
from auto_identity_token_generator import AutoIdentityTokenGenerator

class AutoIdentityTokenServer:
    """Auto Identity Token Integration Server"""
    
    def __init__(self):
        self.app = web.Application()
        self.token_generator = AutoIdentityTokenGenerator()
        
        # Setup routes
        self.setup_routes()
        
        # Add CORS headers manually
        @web.middleware
        async def cors_middleware(request, handler):
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        
        self.app.middlewares.append(cors_middleware)
    
    def setup_routes(self):
        """Setup all API routes"""
        
        # Token generation routes
        self.app.router.add_post('/api/tokens/generate', self.generate_token)
        self.app.router.add_post('/api/tokens/generate/{token_type}', self.generate_specific_token)
        
        # Token verification routes
        self.app.router.add_post('/api/tokens/verify', self.verify_token)
        self.app.router.add_get('/api/tokens/verify/{token_id}', self.verify_token_by_id)
        
        # Token management routes
        self.app.router.add_post('/api/tokens/{token_id}/revoke', self.revoke_token)
        self.app.router.add_get('/api/tokens/statistics', self.get_token_statistics)
        self.app.router.add_get('/api/tokens/by-did/{citizen_did}', self.get_tokens_by_did)
        
        # DID and VC integration routes
        self.app.router.add_get('/api/did/{citizen_did}/retrieve', self.retrieve_did)
        self.app.router.add_get('/api/did/{citizen_did}/resolve', self.resolve_did)
        self.app.router.add_get('/api/did/{citizen_did}/credentials', self.get_did_credentials)
        
        # Health and status routes
        self.app.router.add_get('/health', self.health_check)
        self.app.router.add_get('/status', self.status_check)
        self.app.router.add_get('/', self.serve_index)
        
        # Static files
        self.app.router.add_static('/static', Path(__file__).parent.parent / 'static', name='static')
    
    async def initialize(self):
        """Initialize the server"""
        try:
            print("🚀 Initializing Auto Identity Token Server...")
            await self.token_generator.initialize()
            print("✅ Auto Identity Token Server initialized successfully!")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize Auto Identity Token Server: {e}")
            return False
    
    async def serve_index(self, request):
        """Serve the main index page"""
        try:
            return web.Response(
                text="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auto Identity Token API</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }
        .method { font-weight: bold; color: #e74c3c; }
        .path { font-family: monospace; color: #2c3e50; }
        .description { color: #7f8c8d; margin-top: 5px; }
        .status { text-align: center; color: #27ae60; font-weight: bold; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎫 Auto Identity Token API</h1>
        <div class="status">✅ Server is running and ready!</div>
        
        <h2>📋 Available Endpoints</h2>
        
        <div class="endpoint">
            <div class="method">POST</div>
            <div class="path">/api/tokens/generate</div>
            <div class="description">Generate auto identity token with DID retrieval, resolution, and VC integration</div>
        </div>
        
        <div class="endpoint">
            <div class="method">POST</div>
            <div class="path">/api/tokens/generate/{token_type}</div>
            <div class="description">Generate specific type of token (identity_token, access_token, service_token, refresh_token)</div>
        </div>
        
        <div class="endpoint">
            <div class="method">POST</div>
            <div class="path">/api/tokens/verify</div>
            <div class="description">Verify auto identity token</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="path">/api/tokens/verify/{token_id}</div>
            <div class="description">Verify token by ID</div>
        </div>
        
        <div class="endpoint">
            <div class="method">POST</div>
            <div class="path">/api/tokens/{token_id}/revoke</div>
            <div class="description">Revoke auto identity token</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="path">/api/tokens/statistics</div>
            <div class="description">Get token statistics</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="path">/api/did/{citizen_did}/retrieve</div>
            <div class="description">Retrieve DID data from registry</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="path">/api/did/{citizen_did}/resolve</div>
            <div class="description">Resolve DID using SDIS Public Resolver</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="path">/api/did/{citizen_did}/credentials</div>
            <div class="description">Get VC credentials for DID</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="path">/health</div>
            <div class="description">Health check endpoint</div>
        </div>
        
        <div class="endpoint">
            <div class="method">GET</div>
            <div class="path">/status</div>
            <div class="description">Detailed status information</div>
        </div>
    </div>
</body>
</html>
                """,
                content_type='text/html'
            )
        except Exception as e:
            return web.Response(text=f"Error: {e}", status=500)
    
    # Token Generation Endpoints
    
    async def generate_token(self, request):
        """Generate auto identity token"""
        try:
            data = await request.json()
            citizen_did = data.get('citizen_did')
            token_type = data.get('token_type', 'identity_token')
            additional_claims = data.get('additional_claims', {})
            
            if not citizen_did:
                return web.json_response({'error': 'citizen_did is required'}, status=400)
            
            result = await self.token_generator.generate_auto_identity_token(
                citizen_did, token_type, additional_claims
            )
            
            if result['success']:
                return web.json_response({
                    'success': True,
                    'token_id': result['token_id'],
                    'token': result['token'],
                    'token_type': result['token_type'],
                    'expires_at': result['expires_at'],
                    'generated_at': datetime.now().isoformat()
                })
            else:
                return web.json_response({'error': result['error']}, status=400)
                
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def generate_specific_token(self, request):
        """Generate specific type of token"""
        try:
            token_type = request.match_info['token_type']
            data = await request.json()
            citizen_did = data.get('citizen_did')
            additional_claims = data.get('additional_claims', {})
            
            if not citizen_did:
                return web.json_response({'error': 'citizen_did is required'}, status=400)
            
            result = await self.token_generator.generate_auto_identity_token(
                citizen_did, token_type, additional_claims
            )
            
            if result['success']:
                return web.json_response({
                    'success': True,
                    'token_id': result['token_id'],
                    'token': result['token'],
                    'token_type': result['token_type'],
                    'expires_at': result['expires_at'],
                    'generated_at': datetime.now().isoformat()
                })
            else:
                return web.json_response({'error': result['error']}, status=400)
                
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    # Token Verification Endpoints
    
    async def verify_token(self, request):
        """Verify auto identity token"""
        try:
            data = await request.json()
            token = data.get('token')
            
            if not token:
                return web.json_response({'error': 'token is required'}, status=400)
            
            result = await self.token_generator.verify_auto_identity_token(token)
            
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def verify_token_by_id(self, request):
        """Verify token by ID"""
        try:
            token_id = request.match_info['token_id']
            
            # Load token from ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'auto_identity_tokens.json'
            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    ledger = json.load(f)
                
                if token_id in ledger.get('tokens', {}):
                    token_entry = ledger['tokens'][token_id]
                    
                    return web.json_response({
                        'success': True,
                        'token_id': token_id,
                        'token_entry': token_entry,
                        'verified_at': datetime.now().isoformat()
                    })
                else:
                    return web.json_response({'error': 'Token not found'}, status=404)
            else:
                return web.json_response({'error': 'Token ledger not found'}, status=500)
                
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    # Token Management Endpoints
    
    async def revoke_token(self, request):
        """Revoke auto identity token"""
        try:
            token_id = request.match_info['token_id']
            data = await request.json()
            reason = data.get('reason', 'Manual revocation')
            
            result = await self.token_generator.revoke_auto_identity_token(token_id, reason)
            
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_token_statistics(self, request):
        """Get token statistics"""
        try:
            result = await self.token_generator.get_token_statistics()
            return web.json_response(result)
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_tokens_by_did(self, request):
        """Get all tokens for a citizen DID"""
        try:
            citizen_did = request.match_info['citizen_did']
            
            # Load token ledger
            ledger_file = Path(__file__).parent.parent / 'data' / 'auto_identity_tokens.json'
            if ledger_file.exists():
                with open(ledger_file, 'r') as f:
                    ledger = json.load(f)
                
                # Find tokens for this citizen
                citizen_tokens = []
                for token_id, token_entry in ledger.get('tokens', {}).items():
                    if token_entry.get('citizen_did') == citizen_did:
                        citizen_tokens.append({
                            'token_id': token_id,
                            'token_type': token_entry.get('token_type'),
                            'status': token_entry.get('status'),
                            'created_at': token_entry.get('created_at'),
                            'expires_at': token_entry.get('expires_at')
                        })
                
                return web.json_response({
                    'success': True,
                    'citizen_did': citizen_did,
                    'tokens': citizen_tokens,
                    'count': len(citizen_tokens)
                })
            else:
                return web.json_response({'error': 'Token ledger not found'}, status=500)
                
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    # DID and VC Integration Endpoints
    
    async def retrieve_did(self, request):
        """Retrieve DID data from registry"""
        try:
            citizen_did = request.match_info['citizen_did']
            
            result = await self.token_generator._retrieve_did_data(citizen_did)
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def resolve_did(self, request):
        """Resolve DID using SDIS Public Resolver"""
        try:
            citizen_did = request.match_info['citizen_did']
            
            result = await self.token_generator._resolve_did(citizen_did)
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_did_credentials(self, request):
        """Get VC credentials for DID"""
        try:
            citizen_did = request.match_info['citizen_did']
            
            result = await self.token_generator._get_vc_credentials(citizen_did)
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)
    
    # Health and Status Endpoints
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({
            'status': 'healthy',
            'service': 'Auto Identity Token API',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    
    async def status_check(self, request):
        """Detailed status information"""
        try:
            # Get token statistics
            token_stats = await self.token_generator.get_token_statistics()
            
            return web.json_response({
                'status': 'operational',
                'service': 'Auto Identity Token API',
                'timestamp': datetime.now().isoformat(),
                'version': '1.0.0',
                'features': [
                    'Auto Identity Token Generation',
                    'DID Retrieval',
                    'DID Resolution',
                    'VC Integration over Indy Ledger',
                    'Token Verification',
                    'Token Management',
                    'Multi-token Support'
                ],
                'token_statistics': token_stats,
                'endpoints': {
                    'token_generation': '/api/tokens/generate',
                    'token_verification': '/api/tokens/verify',
                    'token_management': '/api/tokens/{token_id}/revoke',
                    'did_retrieval': '/api/did/{citizen_did}/retrieve',
                    'did_resolution': '/api/did/{citizen_did}/resolve',
                    'vc_credentials': '/api/did/{citizen_did}/credentials'
                }
            })
        except Exception as e:
            return web.json_response({'error': str(e)}, status=500)

def create_app():
    """Create and return the web application"""
    server = AutoIdentityTokenServer()
    return server.app

async def main():
    """Main function to start the server"""
    app = create_app()
    
    # Initialize the server
    server_instance = AutoIdentityTokenServer()
    await server_instance.initialize()
    
    print("🚀 Starting Auto Identity Token Integration Server...")
    print("📡 Server will be available at: http://localhost:8080")
    print("🎫 Auto Identity Token API ready!")
    
    # Start the server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    
    print("✅ Auto Identity Token Integration Server started successfully!")
    print("🌐 Access the API at: http://localhost:8080")
    
    # Keep the server running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Auto Identity Token Integration Server...")
        await runner.cleanup()

if __name__ == '__main__':
    asyncio.run(main())
