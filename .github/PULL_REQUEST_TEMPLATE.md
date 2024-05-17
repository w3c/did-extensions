## Instructions for Pull Requests

Please read these instructions thoroughly in order to ensure that your pull request is processed in a timely manner. This document contains detailed instructions for registering a DID Method. If your pull request concerns some other change to the repository, you may delete all of the text in this text box and write up a more relevant description.

There is a DID Method Registration form below that MUST be included in a DID Method Registration Request. The form includes check boxes that you are expected to fill out when you submit your request.

Once you submit your request, your pull request will be reviewed by the registry editors. Changes regarding the required criteria may be requested. If there are no objections or changes requested, your DID method will be registered after a minimum of 7 days.

## DID Method Registration Process

In order to register a new DID method, you must add a JSON file to the [./methods](./methods) directory.

Here is an example registration entry:

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

Your Pull Request will be automatically validated, please ensure that all of the automated tests pass (no errors reported) or your submission will not be reviewed. Common reasons for failed validation includes invalidly formatted JSON files and missing mandatory fields.

----- DID METHOD REGISTRATION FORM: DELETE EVERYTHING ABOVE THIS LINE ------

### DID Method Registration

As a DID method registrant, I have ensured that my DID method registration complies with the following statements:

- [ ] The DID Method specification [defines the DID Method Syntax](https://w3c.github.io/did-core/#method-syntax).
- [ ] The DID Method specification [defines the Create, Read, Update, and Deactivate DID Method Operations](https://w3c.github.io/did-core/#method-operations).
- [ ] The DID Method specification [contains a Security Considerations section](https://w3c.github.io/did-core/#security-requirements).
- [ ] The DID Method specification [contains a Privacy Considerations section](https://w3c.github.io/did-core/#privacy-requirements).
- [ ] The JSON file I am submitting has [passed all automated validation tests below](#partial-pull-merging).
- [ ] The JSON file contains a `contactEmail` address [OPTIONAL].
- [ ] The JSON file contains a `verifiableDataRegistry` entry [OPTIONAL].
