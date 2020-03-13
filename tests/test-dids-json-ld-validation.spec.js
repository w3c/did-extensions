const documentLoader = require("./documentLoader");
const getMethodsForTest = require("./getMethodsForTest");
const focusedMethods = require("./focusedMethods");
const methodsForTest = getMethodsForTest(focusedMethods);
const canSignAndVerify = require("./canSignAndVerify");

const makeTestDIDsJsonLd = methodsForTest => {
  describe("Test DIDs JSON-LD Validation", () => {
    Object.keys(methodsForTest).map(method => {
      describe(method, () => {
        methodsForTest[method].forEach(did => {
          it(did, async () => {
            const { document } = await documentLoader(did);
            await canSignAndVerify(document);
          });
        });
      });
    });
  });
};

makeTestDIDsJsonLd(methodsForTest);
