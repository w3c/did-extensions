## Registry Tooling

This directory contains command line tooling and support scripts for the did spec registries.

### Setup Tooling

```
npm i
```

### Validate DID Methods

```
npm run registry:validate
```

### Generate DID Methods Registry Index

This command is run in CI, the index file produced is git ignored.

This file is used by the Respec build plugin to build the registry 

in client side javascript at page load time.

```
npm run registry:generate:index
```