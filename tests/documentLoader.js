const fs = require("fs");
const path = require("path");

// const jsonld = require("jsonld");

const resolver = require("./resolver");

const loadContext = relativePath => {
  return JSON.parse(
    fs.readFileSync(path.resolve(__dirname, relativePath)).toString()
  );
};

const contexts = {
  // "https://schema.org/": loadContext(
  //   "../contexts/schema.org/jsonldcontext.jsonld"
  // ),

  "https://www.w3.org/ns/did/v1": loadContext(
    "../contexts/w3.org/did-v1.jsonld"
  ),

  "https://w3id.org/did/v1": loadContext("../contexts/w3id.org/did-v1.jsonld"),

  "https://w3id.org/did/v0.11": loadContext(
    "../contexts/w3id.org/did-v0.11.jsonld"
  ),

};

const documentLoader = async (url, options) => {
  console.log(url);
  if (url.indexOf("did:") === 0) {
    const didDoc = await resolver.resolve(url, options);
    // console.log(didDoc);
    return {
      contextUrl: null, // this is for a context via a link header
      document: didDoc, // this is the actual document that was loaded
      documentUrl: url // this is the actual context URL after redirects
    };
  }

  const context = contexts[url];

  if (context) {
    return {
      contextUrl: null, // this is for a context via a link header
      document: context, // this is the actual document that was loaded
      documentUrl: url // this is the actual context URL after redirects
    };
  }


  console.warn("Remote context detected!" + url);
  
  // Comment out to disable remote loading of contexts.
  try {
    return jsonld.documentLoader(url);
  } catch (e) {
    console.error("No remote context support for " + url);
  }

  console.error("No custom context support for " + url);
  throw new Error("No custom context support for " + url);
};

module.exports = documentLoader;