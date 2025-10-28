![W3C Logo](https://www.w3.org/Icons/w3c_home)

[![Echidna Auto-publish](https://github.com/w3c/did-extensions/actions/workflows/auto-publish.yml/badge.svg)](https://github.com/w3c/did-extensions/actions/workflows/auto-publish.yml)

# Decentralized Identifier Extensions

This repository contains a list of known DID Extensions that are tracked
by the
[W3C Decentralized Identifier Working Group](https://www.w3.org/2019/did-wg/)
(DID WG) for the purpose of enhancing DID ecosystem interoperability. There
might be extensions to DIDs other than the ones listed here; this is not
meant to be an exhaustive or centralized list of extensions.

An Editor's Draft of this repository is available at
https://w3c.github.io/did-extensions/.

## Adding a DID Method

In order to register a new DID method, you must add a JSON file
to the [./methods](./methods) directory and
[open a pull request](https://github.com/w3c/did-extensions/pulls)
to add the file to this repository.

Here is an [example registration entry](https://w3c.github.io/did-extensions/methods/example.json):

```jsonc
{
  // These fields are required
  "name": "example",
  "status": "registered",
  "specification": "https://w3c-ccg.github.io/did-spec/",
  // These fields are optional
  "contactName": "W3C Credentials Community Group",
  "contactEmail": "",
  "contactWebsite": "",
  "verifiableDataRegistry": "DID Specification"
}
```

Your Pull Request will be automatically validated, please ensure
that all of the automated tests pass (no errors reported) or
your submission will not be reviewed. Common reasons for failed
validation includes invalidly formatted JSON files and missing
mandatory fields. There will be a checklist that you are expected
to complete and attest to its accuracy. Once you submit your request,
your pull request will be reviewed by the registry editors. Changes
regarding the required criteria may be requested. If there are at
least two reviews by registry maintainers listed in the CODEOWNERS file, and no objections or
changes requested, your DID method will be registered after a
minimum of 7 days and a maximum of 30 days.

## Adding Anything Else

Use the standard fork, branch, and pull request workflow to propose changes to
the registry. Please make branch names informative—by including the issue or
bug number for example.

Editorial changes that improve the readability of the registry or correct
spelling or grammatical mistakes are welcome.

Non-editorial changes MUST go through a review and approval process that is
[detailed in the registry](https://w3c.github.io/did-extensions/#the-registration-process).

Please read [CONTRIBUTING.md](CONTRIBUTING.md), about licensing contributions.

## Code of Conduct

W3C functions under a [code of conduct](https://www.w3.org/Consortium/cepc/).

## DID Working Group Repositories

- [W3C DID Core Specification v1.0](https://github.com/w3c/did-core)
- [W3C DID Working Group](https://github.com/w3c/did-wg)
- [W3C DID Rubric v1.0](https://github.com/w3c/did-rubric)
- [W3C DID Use Cases v1.0](https://github.com/w3c/did-use-cases)
- [W3C DID Test Suite and Implementation Report](https://github.com/w3c/did-test-suite)
