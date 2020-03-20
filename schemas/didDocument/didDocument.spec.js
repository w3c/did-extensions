


const {ajv, schemas} = require('../index')

describe('/did-core.didDocument', ()=>{
    it('id is only required attribute of a did document', ()=>{
        let valid = ajv
        .validate(schemas['/did-core.didDocument'], {
            "id": "did:example:123",
        });
        expect(valid).toBe(true)
        valid = ajv
        .validate(schemas['/did-core.didDocument'], {});
        expect(valid).toBe(false)
    })
    it('did document with none string id is NOT valid', ()=>{
        let valid = ajv
        .validate(schemas['/did-core.didDocument'], {
           "id": 0
        });
        expect(valid).toBe(false)
    })
    it('did document with additionalProperties is NOT valid', ()=>{
        let valid = ajv
        .validate(schemas['/did-core.didDocument'], {
            "id": "did:example:123",
            "authorization": {}
        });
        expect(valid).toBe(false)
    })
    it('did document with invalid pattern is NOT valid', ()=>{
        let valid = ajv
        .validate(schemas['/did-core.didDocument'], {
            "id": "did:123",
        });
        expect(valid).toBe(false)
    })
    it('did document must be an object', ()=>{
        let valid = ajv
        .validate(schemas['/did-core.didDocument'], 'foo');
        expect(valid).toBe(false)
    })
})