const fs = require("fs");
const path = require("path");

const resolver = require("./resolver");

const loadContext = relativePath => {
  return JSON.parse(
    fs.readFileSync(path.resolve(__dirname, relativePath)).toString()
  );
};

const contexts = {
  "https://www.w3.org/ns/did/v1": loadContext("../contexts/did-v1.jsonld")
};

const documentLoader = async (url, options) => {
  if (url.indexOf("did:") === 0) {
    const didDoc = await resolver.resolve(url.split('#')[0], options);
    return {
      contextUrl: null,
      document: didDoc,
      documentUrl: url
    };
  }

  const context = contexts[url];

  if (context) {
    return {
      contextUrl: null,
      document: context,
      documentUrl: url
    };
  }

  throw new Error("Remote context detected! " + url);
};

module.exports = documentLoader;
