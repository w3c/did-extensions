const documentLoader = require("./documentLoader");

const canSignAndVerify = async document => {
  const jsigs = require("jsonld-signatures");
  const { Ed25519KeyPair } = require("crypto-ld");
  const { Ed25519Signature2018 } = jsigs.suites;
  const { AssertionProofPurpose } = jsigs.purposes;

  const key = new Ed25519KeyPair({
    "id": "did:web:did.actor:carol#z6MkpzW2izkFjNwMBwwvKqmELaQcH8t54QL5xmBdJg9Xh1y4",
    "type": "Ed25519VerificationKey2018",
    "privateKeyBase58": "2m6scGwwRf4n79LmhhNKHhqcdTM2SMzosYhFXH7NStnKrwTVmNYztwNbfK3adDPNgmoZE8tt2FC9WqkBD77rRtXC",
    "publicKeyBase58": "BYEz8kVpPqSt5T7DeGoPVUrcTZcDeX5jGkGhUQBWmoBg"
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
    suite: new Ed25519Signature2018({}),
    purpose: new AssertionProofPurpose({})
  });
  if (!result.verified) {
    console.error(result);
  }
  expect(result.verified).toBe(true);
};

module.exports = canSignAndVerify;
