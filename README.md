![W3C Logo](https://www.w3.org/Icons/w3c_home)

# Decentralized Identifier Core Registries v1.0

This repository contains a registry created by the
[W3C Decentralized Identifier Working Group](https://www.w3.org/2019/did-wg/)
(DID WG) for the purpose of enhancing DID ecosystem interoperability.

An Editor's Draft of this repository is available at
https://w3c.github.io/did-core-registries/.

## CI Tests

This repo uses Github Actions to protect registry definitions and highlight interoperability and compliance issues regarding specific DID Methods.

In order to get your DID Method added to this repo you must.

1. Edit the [focusedMethods](./tests/focusedMethods.js) to include your did method as it is registerd, eg for `did:web:example.com`, `'web'`.

2. Edit the [universal-resolver-config.json](./tests/universal-resolver-config.json), to ensure that your did method is defined and that there is a testIdentifier, for example: `"testIdentifiers": ["did:web:example.com"]`.

3. Build a resolver cache entry for your did method: `npm run build-resolver-cache`.

4. Commit the changes to a branch and open a PR against master.

These test documents must be updated from time to time to accurately reflect their current represenations provided by the universal resolver.

In order to get the latest representation from the Universal Resolver, you will need to delete the existing did document from [test-dids](./test-dids), and re-run:

`npm run build-resolver-cache`

Then commit the changes to a branch and open a PR against master.

In the future, we may decide to add this download step to CI.

## Contributing to the Repository

Use the standard fork, branch, and pull request workflow to propose changes to
the registry. Please make branch names informative—by including the issue or
bug number for example.

Editorial changes that improve the readability of the registry or correct
spelling or grammatical mistakes are welcome.

Non-editorial changes MUST go through a review and approval process that is
detailed in the registry.

Please read [CONTRIBUTING.md](CONTRIBUTING.md), about licensing contributions.

## Code of Conduct

W3C functions under a [code of conduct](https://www.w3.org/Consortium/cepc/).

## DID Working Group Repositories

- [W3C DID Core Specification v1.0](https://github.com/w3c/did-core)
- [W3C DID Working Group](https://github.com/w3c/did-wg)
- [W3C DID Rubric v1.0](https://github.com/w3c/did-rubric)
- [W3C DID Use Cases v1.0](https://github.com/w3c/did-use-cases)
- [W3C DID Test Suite and Implementation Report](https://github.com/w3c/did-test-suite)
