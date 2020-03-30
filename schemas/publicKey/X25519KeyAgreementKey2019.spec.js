


const {ajv, schemas} = require('../index')

describe('/did-core.publicKey.X25519KeyAgreementKey2019', ()=>{
    it('type must be X25519KeyAgreementKey2019', ()=>{
        const validExample = {
            "id": "did:web:did.actor:alice#zC8GybikEfyNaausDA4mkT4egP7SNLx2T1d1kujLQbcP6h",
            "type": "X25519KeyAgreementKey2019",
            "controller": "did:web:did.actor:alice",
            "publicKeyBase58": "CaSHXEvLKS6SfN9aBfkVGBpp15jSnaHazqHgLHp8KZ3Y"
          }
        let valid = ajv
        .validate(schemas['/did-core.publicKey.X25519KeyAgreementKey2019'], validExample);
        expect(valid).toBe(true)
        valid = ajv
        .validate(schemas['/did-core.publicKey.X25519KeyAgreementKey2019'], {
            ...validExample,
            type: 'Secp256k1VerificationKey2018'
        });
        expect(valid).toBe(false)
    })

    it('publicKeyJwk is valid', ()=>{
        let valid = ajv
        .validate(schemas['/did-core.publicKey.X25519KeyAgreementKey2019'], {
            "id": "did:example:123#Bob",
            "type": "X25519KeyAgreementKey2019",
            "controller": "did:example:123",
            "publicKeyJwk": {
                "kty":"OKP",
                "crv":"X25519",
                "kid":"Bob",
                "x":"3p7bfXt9wbTTW2HC7OQ1Nz-DQ8hbeGdNrfx-FG-IK08"
            }  
        });
        expect(valid).toBe(true)
    })
})