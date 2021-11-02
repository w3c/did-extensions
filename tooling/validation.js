

const Ajv = require("ajv")
const yaml = require('js-yaml');
const fs   = require('fs');
const ajv = new Ajv({ strict: false });

const schema = yaml.load(fs.readFileSync('./did-method-registry-entry.yml', 'utf8'));
const validate = ajv.compile(schema)
  
const validateRegistryEntry = (entry)=>{
    const valid = validate(entry)
    if (!valid) {
        console.error(entry)
        console.error(validate.errors)
    }
    return valid;
}

module.exports = validateRegistryEntry;