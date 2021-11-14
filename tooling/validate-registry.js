
const Ajv = require("ajv")
const yaml = require('js-yaml');
const fs   = require('fs');
const path   = require('path');
const ajv = new Ajv({ strict: false });

const didMethodRegistryDirectory = path.join(__dirname, '../methods');

const schema = yaml.load(fs.readFileSync('./did-method-registry-entry.yml', 'utf8'));
const validate = ajv.compile(schema)

const getAllRegistryEntries = () =>{
    const files = fs.readdirSync(didMethodRegistryDirectory);
    const entries = files.filter((file)=>{
        // ignore the index file.
        return file !== 'index.json';
    }).map((file) => {
        const fileContent = fs.readFileSync(path.join(didMethodRegistryDirectory, file)).toString();
        let didMethod = {
          error: 'methods/' + file
        };
        try {
          didMethod = JSON.parse(fileContent);
        } catch(e) {
          console.error('❌ Failed to parse DID Method registry entry: ' +
            'methods/' + file);
        }
        return didMethod;
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
