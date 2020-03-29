const { ajv, schemas } = require("../index");

describe("/did-core.publicKey.JwsVerificationKey2020", () => {
  it("type must be JwsVerificationKey2020", () => {
    const validExample = {
      id: "did:example:123#WjKgJV7VRw3hmgU6--4v15c0Aewbcvat1BsRFTIqa5Q",
      type: "JwsVerificationKey2020",
      controller: "did:example:123",
      publicKeyJwk: {
        crv: "secp256k1",
        x: "NtngWpJUr-rlNNbs0u-Aa8e16OwSJu6UiFf0Rdo1oJ4",
        y: "qN1jKupJlFsPFc1UkWinqljv4YE0mq_Ickwnjgasvmo",
        kty: "EC",
        kid: "WjKgJV7VRw3hmgU6--4v15c0Aewbcvat1BsRFTIqa5Q"
      }
    };
    let valid = ajv.validate(
      schemas["/did-core.publicKey.JwsVerificationKey2020"],
      validExample
    );
    expect(valid).toBe(true);
    valid = ajv.validate(
      schemas["/did-core.publicKey.JwsVerificationKey2020"],
      {
        ...validExample,
        type: "Secp256k1VerificationKey2018"
      }
    );
    expect(valid).toBe(false);
  });

  it("publicKeyJwk is valid", () => {
    let valid = ajv.validate(
      schemas["/did-core.publicKey.JwsVerificationKey2020"],
      {
        id: "did:example:123#WjKgJV7VRw3hmgU6--4v15c0Aewbcvat1BsRFTIqa5Q",
        type: "JwsVerificationKey2020",
        controller: "did:example:123",
        publicKeyJwk: {
          crv: "secp256k1",
          x: "NtngWpJUr-rlNNbs0u-Aa8e16OwSJu6UiFf0Rdo1oJ4",
          y: "qN1jKupJlFsPFc1UkWinqljv4YE0mq_Ickwnjgasvmo",
          kty: "EC",
          kid: "WjKgJV7VRw3hmgU6--4v15c0Aewbcvat1BsRFTIqa5Q"
        }
      }
    );
    expect(valid).toBe(true);
  });
});
