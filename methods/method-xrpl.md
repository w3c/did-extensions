# DID Method: xrpl

## 1. DID Method Name
The name `xrpl` shall be used to refer to this method.

## 2. Method Specific Identifier
A DID that uses this method MUST begin with the following prefix: `did:xrpl`.  
The remainder of the DID MUST be a valid XRP Ledger address.

Example:
```
did:xrpl:mainnet:rPWSjhFZCQgEKhRnKnn6geavviiaU58M6d
```

## 3. CRUD Operations
- **Create**: A DID is considered created when the XRPL account is initialized with a proper public key and optional metadata.
- **Read**: The DID Resolver queries the XRPL for the account’s state and constructs a DID Document.
- **Update**: Updates are done by modifying the XRPL account settings or linked metadata (e.g., IPFS service endpoints).
- **Deactivate**: Account deactivation may be represented by setting specific flags or burning keys.

## 4. DID Document Example

```json
{
  "@context": ["https://www.w3.org/ns/did/v1"],
  "id": "did:xrpl:mainnet:rPWSjhFZCQgEKhRnKnn6geavviiaU58M6d",
  "controller": "did:xrpl:mainnet:rPWSjhFZCQgEKhRnKnn6geavviiaU58M6d",
  "verificationMethod": [
    {
      "id": "#key-1",
      "type": "Ed25519VerificationKey2018",
      "controller": "did:xrpl:mainnet:rPWSjhFZCQgEKhRnKnn6geavviiaU58M6d",
      "publicKeyBase58": "..."
    }
  ],
  "authentication": ["#key-1"],
  "service": [
    {
      "id": "#vault",
      "type": "VaultService",
      "serviceEndpoint": "ipfs://bafybei..."
    }
  ]
}
```

## 5. Security Considerations
- Signature validation MUST conform to XRPL cryptographic standards.
- IPFS or off-ledger content MUST be CID-verified.
- Ledger state consistency MUST be validated.

## 6. Implementation
- Status: Experimental
- Resolver Repo: [To Be Added]
- Maintainer: Inme (did:xrpl:mainnet:rPWSjhFZCQgEKhRnKnn6geavviiaU58M6d)

## 7. Contact
For questions or feedback, please contact the maintainer at:
- Email: inme@xrplcreator.net
- DID: did:xrpl:mainnet:rPWSjhFZCQgEKhRnKnn6geavviiaU58M6d

## 8. Appendix
| Term | Description |
|------|-------------|
| `VaultService` | A decentralized data store linked to the DID Document, typically stored on IPFS. |
| `publicKeyBase58` | The public key associated with the DID used for verification. |
