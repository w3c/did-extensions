package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

// DIDDocument represents a W3C DID Document
type DIDDocument struct {
	Context            []interface{} `json:"@context"`
	ID                 string        `json:"id"`
	VerificationMethod []interface{} `json:"verificationMethod,omitempty"`
	Authentication     []interface{} `json:"authentication,omitempty"`
	AssertionMethod    []interface{} `json:"assertionMethod,omitempty"`
	Service            []interface{} `json:"service,omitempty"`
	Created            string        `json:"created,omitempty"`
	Updated            string        `json:"updated,omitempty"`
}

// ResolutionResult represents the result of DID resolution
type ResolutionResult struct {
	DIDDocument         *DIDDocument `json:"didDocument,omitempty"`
	ResolutionMetadata  interface{}  `json:"resolutionMetadata,omitempty"`
	DocumentMetadata    interface{}  `json:"documentMetadata,omitempty"`
}

// SDISResolver handles resolution of did:sdis DIDs
type SDISResolver struct {
	IndyLedgerURL string
	IPFSGateway   string
	RustCoreURL   string
}

// NewSDISResolver creates a new SDIS resolver instance
func NewSDISResolver() *SDISResolver {
	return &SDISResolver{
		IndyLedgerURL: "http://localhost:8083/api/ledger",
		IPFSGateway:   "https://ipfs.io/ipfs/",
		RustCoreURL:   "http://localhost:8083/api/rust-core",
	}
}

// ResolveDID resolves a did:sdis DID
func (r *SDISResolver) ResolveDID(did string) (*ResolutionResult, error) {
	// Parse DID to extract components
	parts := strings.Split(did, ":")
	if len(parts) != 4 || parts[0] != "did" || parts[1] != "sdis" {
		return nil, fmt.Errorf("invalid did:sdis format")
	}

	primaryHash := parts[2]
	secondaryHash := parts[3]

	// Step 1: Query Indy ledger for DID metadata
	ledgerData, err := r.queryIndyLedger(primaryHash, secondaryHash)
	if err != nil {
		return nil, fmt.Errorf("failed to query ledger: %v", err)
	}

	// Step 2: Retrieve DID document from IPFS
	didDocument, err := r.retrieveFromIPFS(ledgerData.IPFSCID)
	if err != nil {
		return nil, fmt.Errorf("failed to retrieve from IPFS: %v", err)
	}

	// Step 3: Validate DID document
	if err := r.validateDIDDocument(didDocument, did); err != nil {
		return nil, fmt.Errorf("invalid DID document: %v", err)
	}

	// Step 4: Create resolution result
	result := &ResolutionResult{
		DIDDocument: didDocument,
		ResolutionMetadata: map[string]interface{}{
			"contentType": "application/did+ld+json",
			"resolvedAt":  time.Now().UTC().Format(time.RFC3339),
			"resolver":    "sdis-resolver-v1.0.0",
		},
		DocumentMetadata: map[string]interface{}{
			"ledgerTransaction": ledgerData.TransactionHash,
			"ipfsCID":          ledgerData.IPFSCID,
			"created":          ledgerData.CreatedAt,
			"updated":          ledgerData.UpdatedAt,
			"status":           ledgerData.Status,
		},
	}

	return result, nil
}

// LedgerData represents data retrieved from Indy ledger
type LedgerData struct {
	DID              string `json:"did"`
	Verkey           string `json:"verkey"`
	IPFSCID          string `json:"ipfs_cid"`
	TransactionHash  string `json:"transaction_hash"`
	CreatedAt        string `json:"created_at"`
	UpdatedAt        string `json:"updated_at"`
	Status           string `json:"status"`
}

// queryIndyLedger queries the Indy ledger for DID information
func (r *SDISResolver) queryIndyLedger(primaryHash, secondaryHash string) (*LedgerData, error) {
	// Try Rust core first
	rustData, err := r.queryRustCore(primaryHash, secondaryHash)
	if err == nil && rustData != nil {
		return rustData, nil
	}

	// Fallback to Indy ledger API
	url := fmt.Sprintf("%s/did/sdis:%s:%s", r.IndyLedgerURL, primaryHash, secondaryHash)
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("ledger query failed with status %d", resp.StatusCode)
	}

	var ledgerData LedgerData
	if err := json.NewDecoder(resp.Body).Decode(&ledgerData); err != nil {
		return nil, err
	}

	return &ledgerData, nil
}

// queryRustCore queries the Rust core for DID information
func (r *SDISResolver) queryRustCore(primaryHash, secondaryHash string) (*LedgerData, error) {
	url := fmt.Sprintf("%s/did/sdis:%s:%s", r.RustCoreURL, primaryHash, secondaryHash)
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("rust core query failed with status %d", resp.StatusCode)
	}

	var ledgerData LedgerData
	if err := json.NewDecoder(resp.Body).Decode(&ledgerData); err != nil {
		return nil, err
	}

	return &ledgerData, nil
}

// retrieveFromIPFS retrieves DID document from IPFS
func (r *SDISResolver) retrieveFromIPFS(ipfsCID string) (*DIDDocument, error) {
	url := r.IPFSGateway + ipfsCID
	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("IPFS retrieval failed with status %d", resp.StatusCode)
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var didDocument DIDDocument
	if err := json.Unmarshal(body, &didDocument); err != nil {
		return nil, err
	}

	return &didDocument, nil
}

// validateDIDDocument validates the DID document
func (r *SDISResolver) validateDIDDocument(doc *DIDDocument, expectedDID string) error {
	// Check if DID matches
	if doc.ID != expectedDID {
		return fmt.Errorf("DID mismatch: expected %s, got %s", expectedDID, doc.ID)
	}

	// Check required fields
	if len(doc.Context) == 0 {
		return fmt.Errorf("missing @context")
	}

	// Validate context
	contextValid := false
	for _, ctx := range doc.Context {
		if ctxStr, ok := ctx.(string); ok && ctxStr == "https://www.w3.org/ns/did/v1" {
			contextValid = true
			break
		}
	}
	if !contextValid {
		return fmt.Errorf("invalid @context")
	}

	return nil
}

// ErrorResponse represents an error response
type ErrorResponse struct {
	Error            string      `json:"error"`
	ResolutionError  interface{} `json:"resolutionError,omitempty"`
	ResolutionMetadata interface{} `json:"resolutionMetadata,omitempty"`
}

func main() {
	// Initialize resolver
	resolver := NewSDISResolver()

	// Setup Gin router
	r := gin.Default()

	// Add CORS middleware
	r.Use(func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")
		
		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}
		
		c.Next()
	})

	// Health check endpoint
	r.GET("/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status":    "healthy",
			"resolver":  "sdis-resolver-v1.0.0",
			"timestamp": time.Now().UTC().Format(time.RFC3339),
		})
	})

	// DID resolution endpoint
	r.GET("/1.0/identifiers/*did", func(c *gin.Context) {
		did := c.Param("did")
		if !strings.HasPrefix(did, "/") {
			c.JSON(http.StatusBadRequest, ErrorResponse{
				Error: "Invalid DID format",
			})
			return
		}
		
		// Remove leading slash
		did = did[1:]
		
		// Check if it's a did:sdis DID
		if !strings.HasPrefix(did, "did:sdis:") {
			c.JSON(http.StatusBadRequest, ErrorResponse{
				Error: "Only did:sdis DIDs are supported",
			})
			return
		}

		// Resolve DID
		result, err := resolver.ResolveDID(did)
		if err != nil {
			c.JSON(http.StatusNotFound, ErrorResponse{
				Error: fmt.Sprintf("DID resolution failed: %v", err),
				ResolutionError: map[string]interface{}{
					"code":    "notFound",
					"message": fmt.Sprintf("DID not found: %s", did),
				},
				ResolutionMetadata: map[string]interface{}{
					"resolver": "sdis-resolver-v1.0.0",
					"error":    err.Error(),
				},
			})
			return
		}

		// Return successful resolution
		c.Header("Content-Type", "application/did+ld+json")
		c.JSON(http.StatusOK, result)
	})

	// Method info endpoint
	r.GET("/1.0/methods/sdis", func(c *gin.Context) {
		methodInfo := map[string]interface{}{
			"methodName": "sdis",
			"description": "Simulated Decentralized Identity System",
			"version": "1.0.0",
			"supportedContentTypes": []string{
				"application/did+ld+json",
				"application/did+json",
			},
			"supportedFeatures": []string{
				"did:resolve",
				"did:update",
				"did:deactivate",
			},
			"ledgerTypes": []string{
				"indy",
				"ethereum",
			},
			"storageTypes": []string{
				"ipfs",
			},
		}
		c.JSON(http.StatusOK, methodInfo)
	})

	// Start server
	fmt.Println("🚀 Starting SDIS Universal Resolver Driver")
	fmt.Println("📡 Listening on :8084")
	fmt.Println("🔗 Resolver endpoint: http://localhost:8084/1.0/identifiers/")
	fmt.Println("📋 Method info: http://localhost:8084/1.0/methods/sdis")
	fmt.Println("❤️  Health check: http://localhost:8084/health")
	
	r.Run(":8084")
}
