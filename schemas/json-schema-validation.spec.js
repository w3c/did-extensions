


const {ajv, schemas} = require('./index')

describe('JSON Schema Validation', ()=>{
    it('ajv is initialized and schemas are defined ', ()=>{
        expect(ajv).toBeDefined();
        expect(schemas).toBeDefined();
    })
})