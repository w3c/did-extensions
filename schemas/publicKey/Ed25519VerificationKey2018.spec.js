


const {ajv, schemas} = require('../index')

const schema = schemas['/did-core.publicKey.Ed25519VerificationKey2018']

describe('/did-core.publicKey.Ed25519VerificationKey2018', ()=>{
    it('type must be Ed25519VerificationKey2018', ()=>{
        const validExample = {
          "id": "did:example:123#ZC2jXTO6t4R501bfCXv3RxarZyUbdP2w_psLwMuY6ec",
          "type": "Ed25519VerificationKey2018",
          "controller": "did:example:123",
          "publicKeyBase58": "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
        }
        let valid = ajv
        .validate(schema, validExample);
        expect(valid).toBe(true)
        valid = ajv
        .validate(schema, {
            ...validExample,
            type: 'Ed25519VerificationKey2019'
        });
        expect(valid).toBe(false)
    })

    it('publicKeyBase58 is valid', ()=>{
        let valid = ajv
        .validate(schema, {
            "id": "did:example:123#WjKgJV7VRw3hmgU6--4v15c0Aewbcvat1BsRFTIqa5Q",
            "type": "Ed25519VerificationKey2018",
            "controller": "did:example:123",
            "publicKeyBase58": "H3C2AVvLMv6gmMNam3uVAjZpfkcJCwDwnZn6z3wXmqPV"
        });
        expect(valid).toBe(true)
    })

    it('publicKeyJwk is valid', ()=>{
      let valid = ajv
      .validate(schema, {
          "id": "did:example:123#_Qq0UL2Fq651Q0Fjd6TvnYE-faHiOpRlPVQcY_-tA4A",
          "type": "Ed25519VerificationKey2018",
          "controller": "did:example:123",
          "publicKeyJwk": {
            "crv": "Ed25519",
            "x": "VCpo2LMLhn6iWku8MKvSLg2ZAoC-nlOyPVQaO3FxVeQ",
            "kty": "OKP",
            "kid": "_Qq0UL2Fq651Q0Fjd6TvnYE-faHiOpRlPVQcY_-tA4A"
          }
      });
      expect(valid).toBe(true)
  })
})