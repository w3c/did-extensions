


const {ajv, schemas} = require('./index')

describe('JSON Schema Validation', ()=>{
    it('ajv is initialized and schemas are defined ', ()=>{
        expect(ajv).toBeDefined();
        expect(schemas).toBeDefined();
        expect(Object.keys(schemas).length).toBe(4);
    })
})