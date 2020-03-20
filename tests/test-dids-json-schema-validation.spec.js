const documentLoader = require("./documentLoader");
const getMethodsForTest = require("./getMethodsForTest");
const focusedMethods = require("./focusedMethods");
const methodsForTest = getMethodsForTest(focusedMethods);

const { ajv, schemas } = require("../schemas");

const makeTestDIDsJsonSchema = methodsForTest => {
  describe("Test DIDs JSON Schema Validation", () => {
    Object.keys(methodsForTest).map(method => {
      describe(method, () => {
        methodsForTest[method].forEach(did => {
          it(did, async () => {
            const { document } = await documentLoader(did);
            let valid = ajv.validate(
              schemas["/did-core.didDocument"],
              document
            );
            if (!valid) {
              console.error(ajv.errors);
            }
            expect(valid).toBe(true);
          });
        });
      });
    });
  });
};

makeTestDIDsJsonSchema(methodsForTest);
