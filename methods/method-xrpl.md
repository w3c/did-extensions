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
      "serviceEndpoint": "ipfs://bafybeih3oxzz564lprw3y4r7uvr33yzeczxma6qgsb5intca52cigddrwa"
    }
  ]
}
```

## 5. Security Considerations
- Signature validation MUST conform to XRPL cryptographic standards.
- IPFS or off-ledger content MUST be CID-verified.
- Ledger state consistency MUST be validated.

## 6. Implementation Status
- **Status**: Experimental
- **Digest (SHA-256)**: `6BF19A35ABA36C9683D764C4316E8CC5D3E277C54A22F428D16F35CD6FCD7B07`
- **Vault CID**: `bafybeih3oxzz564lprw3y4r7uvr33yzeczxma6qgsb5intca52cigddrwa`
- **NFT Linkage**: Enabled
- **Redeem UI**:  
  [https://a4gq6-oaaaa-aaaab-qaa4q-cai.raw.icp0.io/?id=3ndsk-pqaaa-aaaaa-qalfa-cai](https://a4gq6-oaaaa-aaaab-qaa4q-cai.raw.icp0.io/?id=3ndsk-pqaaa-aaaaa-qalfa-cai)

> ⚠️ Only the NFT holder with matching digest can trigger redeem.  
> This UI is for public record and structural audit.

## 7. Maintainer Information
- **Creator**: Inme  
- **DID**: `did:xrpl:mainnet:rPWSjhFZCQgEKhRnKnn6geavviiaU58M6d`  
- **Email**: popoashley@hotmail.com

## 8. Appendix

| Term | Description |
|------|-------------|
| `VaultService` | A decentralized data store linked to the DID Document, typically stored on IPFS. |
| `publicKeyBase58` | The public key associated with the DID used for verification. |
| `Redeem UI` | Web-based endpoint for interacting with this DID method's NFT. Access restricted to authorized digest holders. |
