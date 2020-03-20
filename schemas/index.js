var Ajv = require('ajv');
var ajv = new Ajv();

const path = require('path');
const fs = require('fs');

const prependPathSegment = pathSegment => location => path.join(pathSegment, location);
const readdirPreserveRelativePath = location => fs.readdirSync(location).map(prependPathSegment(location));
const readdirRecursive = location => readdirPreserveRelativePath(location)
    .reduce((result, currentValue) => fs.statSync(currentValue).isDirectory()
        ? result.concat(readdirRecursive(currentValue))
        : result.concat(currentValue), []);

// load all json files from schemas directory and add them to ajv and schemas map.
const files = readdirRecursive(__dirname).filter((f)=>{
    return !(/^(.(?!.*\.json$))*$/.test(f))
});

const schemas = {};
files.forEach((f)=>{
    const file = fs.readFileSync(f).toString();
    const schema = JSON.parse(file);
    ajv.addSchema(schema, schema.$id)
    schemas[schema.$id] = schema;
})

module.exports = {ajv, schemas};