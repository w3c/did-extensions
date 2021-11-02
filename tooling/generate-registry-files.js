const fs = require('fs');
const mkdirp = require('mkdirp');
const path = require('path');
const didMethodRegex = /<tr>\n.*<td>\n\s+did:(.*):\n.*<\/td>\n.*<td>\s+(.*)\n.*<\/td>\n.*<td>\s+(.*)\n.*<\/td>\n.*<td>\n\s+(.*)\n.*<\/td>\n.*<td>\n\s+(.*)\n.*/g;
const didSpecRegex = /<a href="(.*)">.*<\/a>/;
const websiteRegex = /<a href="(.*)">.*<\/a>/;
const emailRegex = /<a href="mailto:(.*)">.*<\/a>/;
// set directories and paths
const registryFile = path.join(__dirname, '../index.html');
const methodsDir = path.join(__dirname, '../methods');

// create directories
mkdirp.sync(methodsDir);

const validateRegistryEntry = require('./validation');

// we migth consider not allowing html here
const getUnsafeContact = (contact)=>{
  // const obj = {}
  // if (contact.includes('href="http')){
  //   let website = contact.match(websiteRegex)[1];
  //   obj.website = website;
  // }
  // if (contact.includes('href=\"mailto')){
  //   let email = contact.match(emailRegex)[1];
  //   obj.email = email;
  // } 
  // // no useful structure
  // if (!Object.keys(obj).length){
  //   obj.name = contact
  // }
  // // flatten object to single string value.
  // if (obj.website){
  //   return obj.website
  // }
  // if (obj.email){
  //   return obj.email
  // }
  // return obj.name 
  return contact;
}

// we migth consider not allowing html here
const getUnsafeRegistry = (registry)=>{
  // const obj = {}
  // if (registry.includes('href=')){
  //   let website = registry.match(websiteRegex)[1];
  //   obj.website = website;
  // } else {
  //   obj.name = registry
  // }
  // // flatten object to single string value.
  // return obj.website ? obj.website : obj.name
  return registry;
}

// analyze DID Methods in index.html and write out individual files
(async () => {
  // search every DID Method
  const registryHtml = fs.readFileSync(registryFile, 'utf-8');
  const allDidMethods =
    [...registryHtml.matchAll(didMethodRegex)];
  for(const method of allDidMethods) {
    const name = method[1];
    let status = method[2].toLowerCase();
    const registry = getUnsafeRegistry(method[3]);
    const contact = getUnsafeContact(method[4]);
 
    let specification = method[5].match(didSpecRegex);
    if(specification === null) {
      specification = '';
    } else {
      specification = specification[1];
    }
    if(status === 'provisional') {
      status = 'registered';
    }

    const entry = {
      status, name, specification, contact, registry
    };  

    const valid = validateRegistryEntry(entry)
    
    if (!valid){
      throw new Error('Invalid registry entry: ' + JSON.stringify(entry, null, 2));
    }
    const methodFile = path.join(methodsDir, name + '.json');
    fs.writeFileSync(methodFile, JSON.stringify(entry, null, 2));
  }
})();