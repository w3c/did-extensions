
const Ajv = require("ajv")
const yaml = require('js-yaml');
const fs   = require('fs');
const path   = require('path');
const ajv = new Ajv({ strict: false });

const didMethodRegistryDirectory = path.join(__dirname, '../example-registry');
 
const schema = yaml.load(fs.readFileSync('./did-method-registry-entry.yml', 'utf8'));
const validate = ajv.compile(schema)
  
const getAllRegistryEntries = () =>{
    const files = fs.readdirSync(didMethodRegistryDirectory);
    const entries = files.map((file) => {
        const fileContent = fs.readFileSync(path.join(didMethodRegistryDirectory, file)).toString();
        return JSON.parse(fileContent);
    }).sort((a, b)=>{
        return a.name > b.name ? 1 : -1;
    })
    return entries
}

const validateRegistryEntry = (entry)=>{
    const valid = validate(entry)
    if (!valid) {
        console.error(entry)
        console.error(validate.errors)
    }
    return valid;
}

(async ()=>{
    console.log('🧙  validating did method registry');
    const entries = getAllRegistryEntries();
    entries.forEach((entry)=>{
        const valid = validateRegistryEntry(entry)
        if (!valid){
            console.error('❌ Invalid did method registry entry: ' + JSON.stringify(entry, null, 2));
            process.exit(1);
        }
    })
    console.log('✅  did method registry is valid');
})();