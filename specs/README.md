# DID Method Specifications

This directory contains Markdown-based method specifications co-located with
the registry. Hosting specs alongside registration entries ensures:

- **No broken links** — spec and registration live in the same repo
- **Always latest version** — no drift between registry URL and actual spec
- **GitHub-native editing** — anyone can fix a typo via PR without touching HTML
- **Standardized structure** — every spec follows the same template and sections
- **Better review** — reviewers see spec quality during registration, not just a URL

## Template

Use [TEMPLATE.md](./TEMPLATE.md) as the starting point for your specification.

The template defines 14 sections — 8 required, 3 recommended, 3 optional:

| Section | Status | What it covers |
|---|---|---|
| Abstract | REQUIRED | One-paragraph summary |
| Use Case & Requirements | REQUIRED | Target scenario + 22-requirement self-assessment |
| DID Syntax | REQUIRED | ABNF grammar, identifier format |
| DID Document | REQUIRED | Example documents per identity tier |
| CRUD Operations | REQUIRED | Create, Resolve, Update, Deactivate |
| Security Considerations | REQUIRED | Threat model, crypto guarantees |
| Privacy Considerations | REQUIRED | PII, correlation, data minimization |
| Trust Model | RECOMMENDED | Hierarchy, anchor points |
| Interoperability | RECOMMENDED | Universal Resolver, SDKs, protocols |
| Architectural Rationale | RECOMMENDED | Design trade-offs |
| W3C Requirements Coverage | RECOMMENDED | Full 22-requirement matrix |
| Metadata Schema | OPTIONAL | On-chain/storage layout |
| Implementation Notes | OPTIONAL | SDK usage, deployment |
| References | REQUIRED | Normative + informative |

## Structure

Each method specification lives in its own directory:

```
specs/
├── TEMPLATE.md              ← start here
├── README.md                ← this file
├── sns/                     ← example: well-documented method
│   ├── README.md            ← spec overview + section index
│   ├── 01-abstract.md
│   ├── 02-use-case.md
│   ├── 03-did-syntax.md
│   ├── ...
│   └── 14-references.md
├── web/                     ← example: minimal but complete
│   └── spec.md              ← single-file spec (simpler methods)
└── <your-method>/
    └── ...
```

For simpler methods, a single `spec.md` file is acceptable. For complex methods
with multiple tiers, trust models, or integration points, split into numbered
section files (like did:sns).

## Best-Documented Methods (Reference Examples)

These methods demonstrate high-quality specification practices:

| Method | Sections | Highlights | Spec |
|---|---|---|---|
| **did:sns** | 14 sections | Identity tiers, trust model grading, 7 privacy layers, W3C 21/22 coverage, credential schemas, regulatory mapping | [Attestto-com/did-sns-spec](https://github.com/Attestto-com/did-sns-spec/tree/main/did-sns/spec) |
| **did:web** | 6 sections | Simple and clear, well-defined CRUD, thorough DNS security analysis | [w3c-ccg/did-method-web](https://github.com/w3c-ccg/did-method-web) |
| **did:webvh** | 10+ sections | Verifiable history, cryptographic log, migration from did:web | [decentralized-identity/didwebvh](https://github.com/decentralized-identity/didwebvh) |
| **did:key** | 5 sections | Minimal spec for ephemeral method, clean ABNF grammar | [w3c-ccg/did-key-spec](https://github.com/w3c-ccg/did-key-spec) |
| **did:peer** | 8 sections | Multiple numalgo algorithms, layered construction | [decentralized-identity/peer-did-method-spec](https://github.com/decentralized-identity/peer-did-method-spec) |
| **did:dht** | 8 sections | DHT gateway architecture, DNS resource record mapping | [decentralized-identity/did-dht](https://github.com/decentralized-identity/did-dht) |
| **did:ethr** | 6 sections | Smart contract registry, event-based DID Document construction | [decentralized-identity/ethr-did-resolver](https://github.com/decentralized-identity/ethr-did-resolver) |
| **did:ion** | 7 sections | Sidetree protocol, Bitcoin anchoring, long-form DIDs | [decentralized-identity/ion](https://github.com/decentralized-identity/ion) |
| **did:pkh** | 5 sections | Blockchain address derivation, multi-chain CAIP-10 | [w3c-ccg/did-pkh](https://github.com/w3c-ccg/did-pkh) |
| **did:jwk** | 4 sections | Minimal — JWK → DID Document, deterministic | [w3c-ccg/did-jwk](https://github.com/w3c-ccg/did-jwk) |

## Why Markdown?

| HTML/ReSpec Specs | Markdown Specs |
|---|---|
| Edit requires reading raw HTML | Edit directly on GitHub with preview |
| Separate repo = broken links over time | Same repo = always in sync |
| Rendering depends on ReSpec JS | Renders natively on GitHub |
| Review requires local build | Review in PR diff view |
| Style varies per method | Template enforces standard sections |
| Contributors need HTML knowledge | Contributors need only Markdown |
