/**
 * Citizen Portal - Dynamic JavaScript Implementation
 * Handles complete citizen workflow with dynamic content
 */

class CitizenPortal {
    constructor() {
        this.currentSession = null;
        this.currentCitizenId = null;
        this.userCitizens = [];
        this.hasApprovedAadhaarKYC = false;
        this.init();
    }

    init() {
        this.createHTMLStructure();
        this.bindEvents();
        this.checkExistingSession();
    }

    createHTMLStructure() {
        document.body.innerHTML = `
            <div class="container">
                <!-- Login/Register Section -->
                <div id="authSection">
                    <div class="header">
                        <h1>🇮🇳 Citizen Portal</h1>
                        <p>Aadhaar KYC & Government Services</p>
                    </div>
                    
                    <!-- Login Form -->
                    <div id="loginForm" class="login-container">
                        <div class="login-form">
                            <h2>Login</h2>
                            <p>Access your account to manage your digital identity</p>
                            
                            <form id="loginFormElement">
                                <div class="form-group">
                                    <label for="loginEmail">Email Address</label>
                                    <input type="email" id="loginEmail" name="email" required>
                                </div>
                                
                                <div class="form-group">
                                    <label for="loginPassword">Password</label>
                                    <input type="password" id="loginPassword" name="password" required>
                                </div>
                                
                                <button type="submit" class="btn">Login</button>
                            </form>
                            
                            <div class="form-toggle">
                                <p>Don't have an account? <a href="#" onclick="citizenPortal.showRegister()">Register here</a></p>
                            </div>
                            
                            <div id="loginResult" class="hidden"></div>
                        </div>
                    </div>
                    
                    <!-- Register Form -->
                    <div id="registerForm" class="login-container hidden">
                        <div class="register-form">
                            <h2>Register</h2>
                            <p>Create an account to manage your digital identity</p>
                            
                            <form id="registerFormElement">
                                <div class="form-group">
                                    <label for="registerName">Full Name</label>
                                    <input type="text" id="registerName" name="name" required>
                                </div>
                                
                                <div class="form-group">
                                    <label for="registerEmail">Email Address</label>
                                    <input type="email" id="registerEmail" name="email" required>
                                </div>
                                
                                <div class="form-group">
                                    <label for="registerPassword">Password</label>
                                    <input type="password" id="registerPassword" name="password" required>
                                </div>
                                
                                <button type="submit" class="btn btn-success">Register</button>
                            </form>
                            
                            <div class="form-toggle">
                                <p>Already have an account? <a href="#" onclick="citizenPortal.showLogin()">Login here</a></p>
                            </div>
                            
                            <div id="registerResult" class="hidden"></div>
                        </div>
                    </div>
                </div>
                
                <!-- Main Application Section -->
                <div id="mainApp" class="hidden">
                    <div class="header">
                        <h1>🇮🇳 Citizen Portal</h1>
                        <p>Aadhaar KYC & Government Services</p>
                        <div class="user-info">
                            <div class="user-name" id="userName">Welcome!</div>
                            <button class="logout-btn" onclick="citizenPortal.logout()">Logout</button>
                        </div>
                    </div>
                    
                    <div class="tabs">
                        <button class="tab active" onclick="citizenPortal.showTab('wallet')">Wallet</button>
                        ${!this.hasApprovedAadhaarKYC ? '<button class="tab" onclick="citizenPortal.showTab(\'aadhaar\')">Aadhaar KYC</button>' : ''}
                        ${this.hasApprovedAadhaarKYC ? '<button class="tab" onclick="citizenPortal.showTab(\'services\')">Government Services</button>' : ''}
                    </div>
                    
                    <!-- Dynamic Content Area -->
                    <div id="mainContent" class="tab-content active">
                        <!-- Content will be dynamically loaded here -->
                    </div>
                </div>
            </div>
        `;
    }

    bindEvents() {
        // Login Form
        document.addEventListener('submit', async (e) => {
            if (e.target.id === 'loginFormElement') {
                e.preventDefault();
                await this.handleLogin(e);
            } else if (e.target.id === 'registerFormElement') {
                e.preventDefault();
                await this.handleRegister(e);
            }
        });
    }

    checkExistingSession() {
        const savedSession = localStorage.getItem('citizen_session');
        if (savedSession) {
            try {
                this.currentSession = JSON.parse(savedSession);
                this.showMainApp();
                this.checkUserDIDStatus();
            } catch (e) {
                localStorage.removeItem('citizen_session');
            }
        }
    }

    async handleLogin(e) {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentSession = {
                    session_id: result.session_id,
                    user_id: result.user_id,
                    name: result.name
                };
                
                localStorage.setItem('citizen_session', JSON.stringify(this.currentSession));
                this.showMainApp();
                this.checkUserDIDStatus();
            } else {
                this.showLoginError(result.error);
            }
        } catch (error) {
            this.showLoginError('Login failed: ' + error.message);
        }
    }

    async handleRegister(e) {
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showRegisterSuccess(result);
            } else {
                this.showRegisterError(result.error);
            }
        } catch (error) {
            this.showRegisterError('Registration failed: ' + error.message);
        }
    }

    showMainApp() {
        document.getElementById('authSection').classList.add('hidden');
        document.getElementById('mainApp').classList.remove('hidden');
        document.getElementById('userName').textContent = `Welcome, ${this.currentSession.name}!`;
    }

    async checkUserDIDStatus() {
        try {
            const response = await fetch('/api/citizen/check-did-status', {
                method: 'GET',
                headers: {
                    'X-Session-ID': this.currentSession.session_id
                }
            });
            
            if (response.status === 401) {
                // Session expired, redirect to login
                console.log('Session expired, redirecting to login');
                localStorage.removeItem('citizen_session');
                this.currentSession = null;
                this.showLogin();
                return;
            }
            
            const result = await response.json();
            
            if (result.has_did) {
                this.currentCitizenId = result.citizen_id;
                this.hasApprovedAadhaarKYC = result.has_approved_aadhaar_kyc;
                this.showWalletEntries();
            } else {
                this.showDIDGenerationPrompt();
            }
        } catch (error) {
            console.error('Error checking DID status:', error);
            this.showDIDGenerationPrompt();
        }
    }

    showDIDGenerationPrompt() {
        // Hide registration tab and show DID generation content
        this.hideTab('register');
        
        // Update the tab content to show DID generation
        document.getElementById('mainContent').innerHTML = `
            <div class="workflow-step">
                <div class="step-header">
                    <h2>🆔 Generate Your Digital Identity (DID)</h2>
                    <p>Create your blockchain-based digital identity to access government services</p>
                </div>
                <div class="step-content">
                    <div class="alert alert-info">
                        <h3>🔗 Blockchain Digital Identity</h3>
                        <p>Your DID will be stored on the Hyperledger Indy blockchain with IPFS CID</p>
                    </div>
                    <div class="form-group">
                        <button class="btn btn-primary btn-large" onclick="citizenPortal.showUserDetailsForm()">
                            🚀 Generate My Blockchain DID
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Make sure the main content is visible
        document.getElementById('mainContent').classList.add('active');
    }

    showWalletEntries() {
        // Hide registration tab if it exists
        this.hideTab('register');
        
        // Activate the wallet tab
        const walletTab = document.querySelector('[onclick="citizenPortal.showTab(\'wallet\')"]');
        if (walletTab) {
            walletTab.classList.add('active');
        }
        
        // Load wallet content
        this.loadWalletContent();
        this.loadWalletData();
        
        // Make sure main content is visible
        document.getElementById('mainContent').classList.add('active');
    }

    hideTab(tabName) {
        const tabElement = document.querySelector(`[onclick="citizenPortal.showTab('${tabName}')"]`);
        if (tabElement) {
            tabElement.style.display = 'none';
            tabElement.classList.remove('active');
        }
        
        // Also hide the corresponding tab content
        const tabContent = document.getElementById(tabName);
        if (tabContent) {
            tabContent.classList.remove('active');
            tabContent.style.display = 'none';
        }
    }

    showTab(tabName) {
        // Remove active class from all tabs
        const tabs = document.querySelectorAll('.tab');
        tabs.forEach(tab => tab.classList.remove('active'));
        
        // Add active class to clicked tab
        if (event && event.target) {
            event.target.classList.add('active');
        } else {
            // If called programmatically, find the tab by onclick attribute
            const targetTab = document.querySelector(`[onclick="citizenPortal.showTab('${tabName}')"]`);
            if (targetTab) {
                targetTab.classList.add('active');
            }
        }
        
        // Load tab-specific content
        this.loadTabContent(tabName);
        
        // Make sure main content is visible
        document.getElementById('mainContent').classList.add('active');
    }

    loadTabContent(tabName) {
        switch(tabName) {
            case 'wallet':
                this.loadWalletContent();
                break;
            case 'aadhaar':
                this.loadAadhaarContent();
                break;
            case 'services':
                this.loadGovernmentServicesContent();
                break;
            default:
                console.log('Unknown tab:', tabName);
        }
    }

    loadWalletContent() {
        document.getElementById('mainContent').innerHTML = `
            <div class="wallet-section">
                <h3>🆔 Your Digital Identity (DID)</h3>
                <div id="didInfo" class="card">
                    <p>Loading DID information...</p>
                </div>
            </div>
            
            <div class="wallet-section">
                <h3>📄 DID Document</h3>
                <div id="didDocument" class="card">
                    <p>Loading DID document...</p>
                </div>
                <div class="wallet-actions">
                    <button class="btn btn-primary" onclick="citizenPortal.resolveDID()" id="resolveBtn" disabled>
                        🔍 Resolve DID
                    </button>
                </div>
            </div>
            
            <div class="wallet-section">
                <h3>🔗 Blockchain Status</h3>
                <div id="blockchainStatus" class="card">
                    <p>Loading blockchain status...</p>
                </div>
            </div>
        `;
        
        this.loadWalletData();
    }

    loadGovernmentServicesContent() {
        document.getElementById('mainContent').innerHTML = `
            <div class="services-section">
                <h3>🏛️ Government Services</h3>
                <p class="services-intro">Access government services with your verified Aadhaar KYC</p>
                <div id="servicesList" class="services-grid">
                    <div class="loading">
                        <div class="spinner"></div>
                        Loading government services...
                    </div>
                </div>
            </div>
        `;
        
        this.loadGovernmentServices();
    }

    async loadGovernmentServices() {
        try {
            console.log('Loading government services...');
            const response = await fetch('/api/citizen/government-services');
            console.log('Response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Parsed result:', result);
            
            if (result.success) {
                this.displayGovernmentServices(result.services);
            } else {
                document.getElementById('servicesList').innerHTML = `
                    <div class="error">
                        ❌ Failed to load government services: ${result.error}
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading government services:', error);
            document.getElementById('servicesList').innerHTML = `
                <div class="error">
                    ❌ Network error loading government services: ${error.message}
                </div>
            `;
        }
    }

    displayGovernmentServices(services) {
        const servicesContainer = document.getElementById('servicesList');
        
        if (!services || Object.keys(services).length === 0) {
            servicesContainer.innerHTML = `
                <div class="no-services">
                    <h4>📭 No Services Available</h4>
                    <p>No government services are currently available.</p>
                </div>
            `;
            return;
        }
        
        const servicesHTML = Object.values(services).map(service => `
            <div class="service-card">
                <div class="service-header">
                    <span class="service-icon">${service.icon}</span>
                    <h4 class="service-name">${service.service_name}</h4>
                </div>
                <div class="service-body">
                    <p class="service-description">${service.description}</p>
                    <div class="service-details">
                        <div class="service-detail">
                            <strong>Category:</strong> ${service.category}
                        </div>
                        <div class="service-detail">
                            <strong>Processing Time:</strong> ${service.processing_time}
                        </div>
                        <div class="service-detail">
                            <strong>Fee:</strong> ${service.fee}
                        </div>
                    </div>
                    <div class="service-requirements">
                        <strong>Requirements:</strong>
                        <ul>
                            ${service.requirements.map(req => `<li>${req}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                <div class="service-footer">
                    <button class="btn btn-primary" onclick="citizenPortal.applyForService('${service.service_id}')">
                        Apply Now
                    </button>
                </div>
            </div>
        `).join('');
        
        servicesContainer.innerHTML = servicesHTML;
    }

    applyForService(serviceId) {
        alert(`Application for service ${serviceId} would be processed here. This is a demo implementation.`);
    }
        document.getElementById('mainContent').innerHTML = `
            <h2>Aadhaar e-KYC Request</h2>
            <p>Request Aadhaar e-KYC verification</p>
            
            <form id="aadhaarForm">
                <div class="form-group">
                    <label for="aadhaarNumber">Aadhaar Number *</label>
                    <input type="text" id="aadhaarNumber" name="aadhaar_number" 
                           pattern="[0-9]{12}" maxlength="12" required>
                </div>
                
                <div class="form-group">
                    <label for="otp">OTP *</label>
                    <input type="text" id="otp" name="otp" 
                           pattern="[0-9]{6}" maxlength="6" required>
                </div>
                
                <button type="submit" class="btn btn-warning">Request Aadhaar e-KYC</button>
            </form>
            
            <div id="aadhaarStatus" class="hidden"></div>
        `;
        
        // Bind Aadhaar form
        document.getElementById('aadhaarForm').addEventListener('submit', (e) => {
            this.handleAadhaarRequest(e);
        });
    }

    loadServicesContent() {
        document.getElementById('mainContent').innerHTML = `
            <h2>Available Government Services</h2>
            <p>Access government services after Aadhaar e-KYC approval</p>
            
            <div id="servicesContent">
                <div class="alert alert-info">
                    Please complete Aadhaar e-KYC first to access government services
                </div>
            </div>
        `;
        
        this.loadServices();
    }

    loadRegistrationContent() {
        document.getElementById('mainContent').innerHTML = `
            <h2>Register New Citizen</h2>
            <p>Register a new citizen with personal details to get DID stored on Indy ledger</p>
            
            <form id="registrationForm">
                <div class="form-group">
                    <label for="name">Full Name *</label>
                    <input type="text" id="name" name="name" required>
                </div>
                
                <div class="form-group">
                    <label for="email">Email Address *</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="phone">Phone Number *</label>
                    <input type="tel" id="phone" name="phone" required>
                </div>
                
                <div class="form-group">
                    <label for="address">Address *</label>
                    <input type="text" id="address" name="address" required>
                </div>
                
                <div class="form-group">
                    <label for="dob">Date of Birth *</label>
                    <input type="date" id="dob" name="dob" required>
                </div>
                
                <div class="form-group">
                    <label for="gender">Gender *</label>
                    <select id="gender" name="gender" required>
                        <option value="">Select Gender</option>
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="occupation">Occupation</label>
                    <input type="text" id="occupation" name="occupation">
                </div>
                
                <button type="submit" class="btn btn-primary">Register Citizen</button>
            </form>
            
            <div id="registrationResult" class="result-message" style="display: none;"></div>
        `;
        
        // Bind registration form
        document.getElementById('registrationForm').addEventListener('submit', (e) => {
            this.handleRegistration(e);
        });
    }

    showUserDetailsForm() {
        const mainContent = document.getElementById('mainContent');
        mainContent.innerHTML = `
            <div class="user-details-form">
                <div class="header">
                    <h2>📝 Personal Details for DID Generation</h2>
                    <p>Please provide your personal information to generate your blockchain digital identity</p>
                </div>
                
                <form id="userDetailsForm" class="form-container">
                    <div class="form-group">
                        <label for="fullName">Full Name *</label>
                        <input type="text" id="fullName" name="name" required placeholder="Enter your full name">
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email Address *</label>
                        <input type="email" id="email" name="email" required placeholder="Enter your email address">
                    </div>
                    
                    <div class="form-group">
                        <label for="phone">Phone Number *</label>
                        <input type="tel" id="phone" name="phone" required placeholder="Enter your phone number">
                    </div>
                    
                    <div class="form-group">
                        <label for="address">Address *</label>
                        <textarea id="address" name="address" required placeholder="Enter your complete address" rows="3"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="dob">Date of Birth *</label>
                        <input type="date" id="dob" name="dob" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="gender">Gender *</label>
                        <select id="gender" name="gender" required>
                            <option value="">Select Gender</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                            <option value="Other">Other</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="aadhaarNumber">Aadhaar Number (Optional)</label>
                        <input type="text" id="aadhaarNumber" name="aadhaar_number" placeholder="Enter your Aadhaar number">
                    </div>
                    
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="citizenPortal.showDIDGenerationPrompt()">
                            ← Back
                        </button>
                        <button type="submit" class="btn btn-primary">
                            🚀 Generate DID
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        // Bind form submission
        document.getElementById('userDetailsForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.generateDID();
        });
    }

    async generateDID() {
        try {
            // Get form data
            const formData = new FormData(document.getElementById('userDetailsForm'));
            const personalDetails = {
                name: formData.get('name'),
                email: formData.get('email'),
                phone: formData.get('phone'),
                address: formData.get('address'),
                dob: formData.get('dob'),
                gender: formData.get('gender'),
                aadhaar_number: formData.get('aadhaar_number') || null
            };
            
            // Show loading
            const submitBtn = document.querySelector('#userDetailsForm button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '⏳ Generating DID...';
            submitBtn.disabled = true;
            
            const response = await fetch('/api/citizen/generate-did', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': this.currentSession.session_id
                },
                body: JSON.stringify(personalDetails)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentCitizenId = result.citizen_id;
                
                // Show success message first
                this.showDIDSuccess(result);
                
                // Then redirect to wallet after a short delay
                setTimeout(() => {
                    this.showWalletEntries();
                }, 2000);
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('DID generation failed: ' + error.message);
        } finally {
            // Restore button
            const submitBtn = document.querySelector('#userDetailsForm button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '🚀 Generate DID';
                submitBtn.disabled = false;
            }
        }
    }

    showDIDSuccess(result) {
        document.getElementById('mainContent').innerHTML = `
            <div class="workflow-step">
                <div class="step-header">
                    <h2>✅ DID Generated Successfully!</h2>
                    <p>Your blockchain digital identity has been created and stored on the Rust Indy ledger</p>
                </div>
                <div class="step-content">
                    <div class="alert alert-success">
                        <h3>🆔 Your Digital Identity</h3>
                        <p><strong>DID:</strong> ${result.did}</p>
                        <p><strong>Citizen ID:</strong> ${result.citizen_id}</p>
                        <p><strong>Blockchain:</strong> ${result.ledger_type || 'Rust Indy Ledger'}</p>
                        <p><strong>Status:</strong> <span class="badge badge-success">STORED ON LEDGER</span></p>
                    </div>
                    <div class="form-group">
                        <button class="btn btn-success btn-large" onclick="citizenPortal.showWalletEntries()">
                            ➡️ Go to Wallet
                        </button>
                        <p class="text-muted">Redirecting to wallet in 2 seconds...</p>
                    </div>
                </div>
            </div>
        `;
    }

    async loadWalletData() {
        try {
            const response = await fetch('/api/citizen/check-did-status', {
                method: 'GET',
                headers: {
                    'X-Session-ID': this.currentSession.session_id
                }
            });
            
            if (response.status === 401) {
                // Session expired, redirect to login
                console.log('Session expired, redirecting to login');
                localStorage.removeItem('citizen_session');
                this.currentSession = null;
                this.showLogin();
                return;
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            
            if (result.success && result.has_did) {
                document.getElementById('didInfo').innerHTML = `
                    <div class="did-display">
                        <h4>🆔 Your Digital Identity (DID)</h4>
                        <div class="did-value">
                            <strong>${result.did}</strong>
                        </div>
                        <div class="did-meta">
                            <span class="badge badge-success">${result.status || 'ACTIVE'}</span>
                            <span class="badge badge-info">${result.ledger_type || 'Rust Indy Ledger'}</span>
                            <span class="badge badge-warning">STORED ON LEDGER</span>
                        </div>
                        <div class="did-details">
                            <div class="detail-item">
                                <strong>Citizen ID:</strong> ${result.citizen_id || 'N/A'}
                            </div>
                            <div class="detail-item">
                                <strong>Transaction ID:</strong> 
                                <code class="transaction-code">${result.transaction_hash || result.ledger_hash || 'N/A'}</code>
                            </div>
                            <div class="detail-item">
                                <strong>IPFS Hash:</strong> 
                                <code class="ipfs-code">${result.ipfs_cid || result.cloud_hash || 'N/A'}</code>
                            </div>
                        </div>
                    </div>
                `;
                
                // Safely display DID document
                let didDocHtml = '<p>No DID document available.</p>';
                if (result.did_document && typeof result.did_document === 'object') {
                    try {
                        didDocHtml = `
                            <div class="did-document">
                                <h5>DID Document Details:</h5>
                                <div class="document-info">
                                    <p><strong>ID:</strong> ${result.did_document.id || result.did}</p>
                                    <p><strong>Verification Method:</strong> ${result.did_document.verificationMethod?.[0]?.type || 'Ed25519VerificationKey2018'}</p>
                                    <p><strong>Created:</strong> ${result.did_document.created_at || 'N/A'}</p>
                                </div>
                                <details>
                                    <summary>View Full Document</summary>
                                    <pre>${JSON.stringify(result.did_document, null, 2)}</pre>
                                </details>
                            </div>
                        `;
                    } catch (e) {
                        didDocHtml = `<p>DID document available but cannot be displayed.</p>`;
                    }
                }
                document.getElementById('didDocument').innerHTML = didDocHtml;
                
                // Enable resolve button
                const resolveBtn = document.getElementById('resolveBtn');
                if (resolveBtn) {
                    resolveBtn.disabled = false;
                    resolveBtn.setAttribute('data-did', result.did);
                }
                
                document.getElementById('blockchainStatus').innerHTML = `
                    <div class="blockchain-info">
                        <h4>🔗 Blockchain Status</h4>
                        <div class="status-grid">
                            <div class="status-item">
                                <strong>Ledger:</strong> ${result.ledger_type || 'Rust Indy Ledger'}
                            </div>
                            <div class="status-item">
                                <strong>Transaction ID:</strong> 
                                <span class="transaction-id">${result.transaction_hash || result.ledger_hash || 'N/A'}</span>
                            </div>
                            <div class="status-item">
                                <strong>IPFS Hash:</strong> 
                                <span class="ipfs-hash">${result.ipfs_cid || result.cloud_hash || 'N/A'}</span>
                            </div>
                            <div class="status-item">
                                <strong>Cloud Provider:</strong> ${result.cloud_provider || 'IPFS + Rust Ledger'}
                            </div>
                            <div class="status-item">
                                <strong>Storage Status:</strong> 
                                <span class="badge badge-success">STORED ON LEDGER</span>
                            </div>
                        </div>
                        ${result.cloud_url ? `
                            <div class="ipfs-link">
                                <strong>IPFS Link:</strong> 
                                <a href="${result.cloud_url}" target="_blank" class="ipfs-url">${result.cloud_url}</a>
                            </div>
                        ` : ''}
                        ${result.transaction_hash || result.ledger_hash ? `
                            <div class="transaction-link">
                                <strong>Ledger Transaction:</strong> 
                                <span class="transaction-url">${result.transaction_hash || result.ledger_hash}</span>
                            </div>
                        ` : ''}
                    </div>
                `;
            } else {
                document.getElementById('didInfo').innerHTML = `
                    <p>No DID found. Please complete registration first.</p>
                `;
                
                document.getElementById('didDocument').innerHTML = `
                    <p>No DID document available.</p>
                `;
                
                document.getElementById('blockchainStatus').innerHTML = `
                    <p>No blockchain data available.</p>
                `;
            }
        } catch (error) {
            console.error('Wallet data loading error:', error);
            document.getElementById('didInfo').innerHTML = `
                <p>Error loading DID information: ${error.message}</p>
            `;
            document.getElementById('didDocument').innerHTML = `
                <p>Error loading DID document.</p>
            `;
            document.getElementById('blockchainStatus').innerHTML = `
                <p>Error loading blockchain status.</p>
            `;
        }
    }

    async handleAadhaarRequest(e) {
        e.preventDefault();
        
        if (!this.currentCitizenId) {
            alert('Please generate DID first');
            return;
        }
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        try {
            const response = await fetch(`/api/citizen/${this.currentCitizenId}/aadhaar-request`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': this.currentSession.session_id
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showAadhaarSuccess(result);
            } else if (response.status === 429) {
                // Handle cooldown period
                this.showAadhaarCooldownError(result);
            } else {
                this.showAadhaarError(result.error || 'Aadhaar request failed');
            }
        } catch (error) {
            console.error('Aadhaar request error:', error);
            this.showAadhaarError('Aadhaar request failed: ' + error.message);
        }
    }

    showAadhaarSuccess(result) {
        const statusDiv = document.getElementById('aadhaarStatus');
        statusDiv.innerHTML = `
            <div class="alert alert-success">
                <h3>✅ Aadhaar e-KYC Request Submitted!</h3>
                <p><strong>Request ID:</strong> ${result.request_id}</p>
                <p><strong>Status:</strong> <span class="status-badge status-pending">${result.status}</span></p>
                <p>Your request has been submitted to the government portal for approval.</p>
            </div>
        `;
        statusDiv.classList.remove('hidden');
    }

    showAadhaarError(message) {
        const statusDiv = document.getElementById('aadhaarStatus');
        statusDiv.innerHTML = `
            <div class="alert alert-warning">
                <h3>❌ Error</h3>
                <p>${message}</p>
            </div>
        `;
        statusDiv.classList.remove('hidden');
    }

    showAadhaarCooldownError(result) {
        const statusDiv = document.getElementById('aadhaarStatus');
        const cooldownDate = new Date(result.cooldown_until).toLocaleDateString();
        statusDiv.innerHTML = `
            <div class="alert alert-warning">
                <h3>⏰ Request on Cooldown</h3>
                <p><strong>${result.error}</strong></p>
                <p><strong>Days Remaining:</strong> ${result.days_remaining} days</p>
                <p><strong>Next Request Available:</strong> ${cooldownDate}</p>
                <p><strong>Last Approved:</strong> ${new Date(result.last_approved).toLocaleDateString()}</p>
                <div class="cooldown-info">
                    <p>📋 <strong>Cooldown Policy:</strong> Citizens can only make one Aadhaar e-KYC request every 3 months (90 days) after approval.</p>
                </div>
            </div>
        `;
        statusDiv.classList.remove('hidden');
    }

    async loadServices() {
        if (!this.currentCitizenId) {
            document.getElementById('servicesContent').innerHTML = `
                <div class="alert alert-info">
                    Please generate DID first
                </div>
            `;
            return;
        }
        
        try {
            const response = await fetch(`/api/citizen/${this.currentCitizenId}/services`, {
                headers: {
                    'X-Session-ID': this.currentSession.session_id
                }
            });
            
            const result = await response.json();
            
            if (result.services && result.services.length > 0) {
                const servicesHTML = result.services.map(service => `
                    <div class="service-card">
                        <h4>${service.name}</h4>
                        <p>${service.description}</p>
                        <button class="btn btn-success">Apply Now</button>
                    </div>
                `).join('');
                
                document.getElementById('servicesContent').innerHTML = `
                    <div class="alert alert-success">
                        <h3>✅ Aadhaar e-KYC Approved!</h3>
                        <p>You can now access government services</p>
                    </div>
                    <div class="services-grid">
                        ${servicesHTML}
                    </div>
                `;
            } else {
                document.getElementById('servicesContent').innerHTML = `
                    <div class="alert alert-info">
                        <h3>ℹ️ ${result.message}</h3>
                        <p>Please complete Aadhaar e-KYC first to access government services</p>
                    </div>
                `;
            }
        } catch (error) {
            document.getElementById('servicesContent').innerHTML = `
                <div class="alert alert-warning">
                    <h3>❌ Error</h3>
                    <p>Failed to load services: ${error.message}</p>
                </div>
            `;
        }
    }

    async handleRegistration(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);
        
        try {
            const response = await fetch('/api/citizen/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': this.currentSession.session_id
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.currentCitizenId = result.citizen_id;
                this.showRegistrationSuccess(result);
            } else {
                this.showError(result.error);
            }
        } catch (error) {
            this.showError('Registration failed: ' + error.message);
        }
    }

    showRegistrationSuccess(result) {
        const resultDiv = document.getElementById('registrationResult');
        resultDiv.innerHTML = `
            <div class="alert alert-success">
                <h3>✅ Registration Successful!</h3>
                <p><strong>Citizen ID:</strong> ${result.citizen_id}</p>
                <p><strong>DID:</strong> ${result.did}</p>
                <p><strong>Status:</strong> DID stored permanently on Indy ledger</p>
            </div>
        `;
        resultDiv.classList.remove('hidden');
    }

    showLogin() {
        document.getElementById('loginForm').classList.remove('hidden');
        document.getElementById('registerForm').classList.add('hidden');
    }

    showRegister() {
        document.getElementById('loginForm').classList.add('hidden');
        document.getElementById('registerForm').classList.remove('hidden');
    }

    showLoginError(message) {
        const resultDiv = document.getElementById('loginResult');
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <h3>❌ Login Failed</h3>
                <p>${message}</p>
            </div>
        `;
        resultDiv.classList.remove('hidden');
    }

    showRegisterSuccess(result) {
        const resultDiv = document.getElementById('registerResult');
        resultDiv.innerHTML = `
            <div class="alert alert-success">
                <h3>✅ Registration Successful!</h3>
                <p>User ID: ${result.user_id}</p>
                <p>Please login to continue</p>
            </div>
        `;
        resultDiv.classList.remove('hidden');
        
        setTimeout(() => {
            this.showLogin();
        }, 2000);
    }

    showRegisterError(message) {
        const resultDiv = document.getElementById('registerResult');
        resultDiv.innerHTML = `
            <div class="alert alert-danger">
                <h3>❌ Registration Failed</h3>
                <p>${message}</p>
            </div>
        `;
        resultDiv.classList.remove('hidden');
    }

    showError(message) {
        const resultDiv = document.getElementById('registrationResult');
        resultDiv.innerHTML = `
            <div class="alert alert-warning">
                <h3>❌ Error</h3>
                <p>${message}</p>
            </div>
        `;
        resultDiv.classList.remove('hidden');
    }

    async logout() {
        console.log('Logout button clicked');
        try {
            if (!this.currentSession) {
                console.log('No current session, clearing local data');
                this.currentSession = null;
                this.currentCitizenId = null;
                this.userCitizens = [];
                localStorage.removeItem('citizen_session');
                document.getElementById('authSection').classList.remove('hidden');
                document.getElementById('mainApp').classList.add('hidden');
                this.showLogin();
                return;
            }
            
            console.log('Sending logout request...');
            const response = await fetch('/api/auth/logout', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ session_id: this.currentSession.session_id })
            });
            
            console.log('Logout response:', response.status);
            const result = await response.json();
            console.log('Logout result:', result);
            
            this.currentSession = null;
            this.currentCitizenId = null;
            this.userCitizens = [];
            
            localStorage.removeItem('citizen_session');
            
            document.getElementById('authSection').classList.remove('hidden');
            document.getElementById('mainApp').classList.add('hidden');
            this.showLogin();
        } catch (error) {
            console.error('Logout error:', error);
            // Even if logout fails, clear local session
            this.currentSession = null;
            this.currentCitizenId = null;
            this.userCitizens = [];
            localStorage.removeItem('citizen_session');
            document.getElementById('authSection').classList.remove('hidden');
            document.getElementById('mainApp').classList.add('hidden');
            this.showLogin();
        }
    }
    
    resolveDID() {
        const resolveBtn = document.getElementById('resolveBtn');
        const did = resolveBtn.getAttribute('data-did');
        
        if (did) {
            // For now, just show an alert - backend implementation can be added later
            alert(`Resolving DID: ${did}\n\nThis feature will be implemented in the backend to verify the DID on the blockchain ledger.`);
            
            // You can add actual DID resolution logic here later
            console.log('Resolving DID:', did);
        }
    }
}

// Initialize the portal when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the portal
    window.citizenPortal = new CitizenPortal();
});
