const {decode} = require('html-entities');
const fs = require('fs');
const mkdirp = require('mkdirp');
const path = require('path');
const util = require('util');
const exec = util.promisify(require('child_process').exec);

// set directories and paths
const registryFile = path.join(__dirname, '../index.html');
const methodsDir = path.join(__dirname, 'methods');

// create directories
mkdirp.sync(methodsDir);

// analyze DID Methods in index.html and write out individual files
(async () => {
  // search every DID Method
  const registryHtml = fs.readFileSync(registryFile, 'utf-8');
  const didMethodRegex = /<tr>\n.*<td>\n\s+did:(.*):\n.*<\/td>\n.*<td>\s+(.*)\n.*<\/td>\n.*<td>\s+(.*)\n.*<\/td>\n.*<td>\n\s+(.*)\n.*<\/td>\n.*<td>\n\s+(.*)\n.*/g;
  const didSpecRegex = /<a href="(.*)">.*<\/a>/;
  const allDidMethods =
    [...registryHtml.matchAll(didMethodRegex)];
  for(const method of allDidMethods) {
    const name = method[1];
    let status = method[2];
    const registry = method[3];
    const contact = method[4];
    const {rubricEvaluation, website, implementation, testSuite} = '';
    let specification = method[5].match(didSpecRegex);
    if(specification === null) {
      specification = '';
    } else {
      specification = specification[1];
    }
    if(status === 'PROVISIONAL') {
      status = '';
    }
    const entry = {
      name, description: '', status, registry, contact, specification,
      rubricEvaluation: '', website: '', implementation: '', testSuite: ''
    };

    // write entry to disk
    const methodFile = path.join(methodsDir, name + '.json');
    fs.writeFileSync(methodFile, JSON.stringify(entry, null, 2));


  }
})();