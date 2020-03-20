const fs = require("fs");
const path = require("path");

const resolver = {
  resolve: async (didUri, options) => {
    try {
      const file = fs.readFileSync(
        path.resolve(__dirname, `../test-dids/${didUri}.json`)
      );
      const document = JSON.parse(file.toString());
      const finalDoc = document;

      if (options) {
        if (options.overwrite_did_context) {
          finalDoc["@context"] = options.overwrite_did_context;
        }
      }

      return finalDoc;
    } catch (e) {
      // tslint:disable-next-line:no-console
      console.error(didUri + " is not in cache. Assuming not resolvable.");
      throw new Error(e);
    }
  }
};

module.exports = resolver;
