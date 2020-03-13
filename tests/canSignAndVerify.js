const documentLoader = require("./documentLoader");

const canSignAndVerify = async document => {
  const jsigs = require("jsonld-signatures");
  const { Ed25519KeyPair } = require("crypto-ld");
  const { Ed25519Signature2018 } = jsigs.suites;
  const { AssertionProofPurpose } = jsigs.purposes;

  const key = new Ed25519KeyPair({
    passphrase: null,
    id:
      "did:key:z6MkfBth5EfE8HgwtA9YfGgBCqqerTaeSKPPjy5aFHumngqj#z6MkfBth5EfE8HgwtA9YfGgBCqqerTaeSKPPjy5aFHumngqj",
    controller: "did:key:z6MkfBth5EfE8HgwtA9YfGgBCqqerTaeSKPPjy5aFHumngqj",
    type: "Ed25519VerificationKey2018",
    privateKeyBase58:
      "2H6yx9zBBc1v7m9AQdEtPzjDPCKnExcch6xqTS441oCQB4pceS8EAR1X29yTtbhjzdR1cpQFgC9eQSeRxmZ3bQah",
    publicKeyBase58: "jdeUzQnnkCUmfJqyhiLMkHf2tJo2S933xAeR1wksU4M"
  });

  const signed = await jsigs.sign(
    { ...document },
    {
      documentLoader,
      suite: new Ed25519Signature2018({
        key,
        date: "2019-12-11T03:50:55Z"
      }),
      purpose: new AssertionProofPurpose(),
      compactProof: false
    }
  );

  expect(signed.id).toBe(document.id);
  expect(signed.proof.verificationMethod).toBe(key.id);

  const result = await jsigs.verify(signed, {
    documentLoader,
    suite: new Ed25519Signature2018({
      key
    }),
    purpose: new AssertionProofPurpose({
      controller: (await documentLoader(key.controller)).document
    })
  });
  if (!result.verified) {
    console.error(result);
  }
  expect(result.verified).toBe(true);
};

module.exports = canSignAndVerify;
