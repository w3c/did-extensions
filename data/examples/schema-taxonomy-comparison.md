# Schema.org-Based DID Method Taxonomy vs. Clusters Model

## The Problem Both Approaches Try to Solve

225 registered DID methods with no standard way to classify, compare, or
discover them. A developer looking for "a method that works offline for
peer-to-peer" has to read 225 specs.

## Hernan's Clusters Model (Noun-Based)

Classifies methods by **what they identify** (the DID Subject):

```
                People  Orgs  Things  Documents  Devices
               ┌──────┬──────┬──────┬──────────┬────────┐
did:web        │  ✓   │  ✓   │      │    ✓     │        │
did:ethr       │  ✓   │  ✓   │      │          │        │
did:key        │  ✓   │      │      │          │   ✓    │
did:peer       │  ✓   │      │      │          │        │
               └──────┴──────┴──────┴──────────┴────────┘
```

**Problems:**

1. **Every method can identify everything.** DID Core says "a DID refers to
   any subject as determined by the controller." A `did:web` can identify a
   person, an org, a device, a document — the method doesn't restrict this.
   The matrix fills up with checkmarks everywhere.

2. **Doesn't capture HOW methods differ.** `did:web` and `did:key` both
   identify people, but they're fundamentally different — one needs a web
   server, the other is self-certifying from a keypair. The matrix can't
   express this.

3. **Not machine-readable.** No standard vocabulary, no JSON-LD context, no
   way for tools to consume the classification programmatically.

4. **Rigid matrix.** Adding a new subject category (e.g., "AI Agents") requires
   restructuring the entire taxonomy. No inheritance, no extension mechanism.

5. **No composition.** Can't express that `did:webvh` extends `did:web` or
   that `did:sns` delegates resolution to `did:sol`.

## Schema.org Model (Verb + Noun + Instrument)

Classifies methods by **what they DO** (Actions) with **what tools** (Instruments)
to produce **what result** (DID Documents):

```json
{
  "@type": ["DIDMethod", "schema:SoftwareApplication"],
  "name": "did:web",

  "anchor": {
    "instrument": { "@type": "schema:WebAPI", "name": "HTTPS" }
  },

  "crud": {
    "create":     { "@type": "schema:CreateAction", "instrument": "Web server + TLS" },
    "resolve":    { "@type": "schema:FindAction",   "instrument": "HTTPS client" },
    "update":     { "@type": "schema:UpdateAction",  "instrument": "File system" },
    "deactivate": { "@type": "schema:DeleteAction",  "instrument": "Remove file / 410" }
  },

  "extends": null,
  "calls": null,
  "additionalType": ["didm:WebAnchored"]
}
```

### Why It's Better

| Dimension | Clusters (Hernan) | Schema.org (Proposed) |
|---|---|---|
| **Classifies by** | DID Subject (noun) | Method behavior (verb + instrument) |
| **Captures behavior** | No | Yes — CRUD as schema:Action subtypes |
| **Machine-readable** | No | Yes — JSON-LD, standard context |
| **Composition** | No | Yes — `extends` and `calls` relationships |
| **Extensible** | Add column/row to matrix | `additionalType` — no schema change |
| **Standard vocabulary** | Custom | schema.org (used by Google, Bing, etc.) |
| **Multi-classification** | 1 cell per method | Multiple `additionalType` values |
| **Anchoring mechanism** | Not captured | `anchor.instrument` |
| **Tool requirements** | Not captured | `softwareRequirements` |
| **Search/discovery** | Manual | SPARQL, JSON-LD framing, tooling |

### The Key Insight

Schema.org already has the vocabulary:

| DID Concept | Schema.org Type | Maps To |
|---|---|---|
| Create DID | `schema:CreateAction` | CRUD Create |
| Resolve DID | `schema:FindAction` | CRUD Resolve |
| Update DID | `schema:UpdateAction` | CRUD Update |
| Deactivate DID | `schema:DeleteAction` | CRUD Deactivate |
| Blockchain | `schema:SoftwareSourceCode` | Anchor instrument |
| Web server | `schema:WebAPI` | Anchor instrument |
| DID Document | `schema:DigitalDocument` | Action result |
| Method spec | `schema:TechArticle` | Documentation |
| Controller | `schema:Person/Organization` | Action agent |

### Composition Is Visible

```
did:webvh
  extends: did:web                    ← class inheritance
  anchor.instrument: [HTTPS, CryptoLog]  ← adds instrument

did:sns
  calls: did:sol                      ← dependency injection
  anchor.instrument: [SNS Program, Solana]

did:peer
  extends: null                       ← standalone
  calls: null
  anchor: null (peer-exchanged)       ← no external dependency
```

### Query Examples

With schema.org typing, you can query:

```sparql
# Find all methods that use a blockchain as anchor
SELECT ?method WHERE {
  ?method a didm:DIDMethod ;
         didm:anchor/schema:instrument/a schema:BlockChain .
}

# Find all methods that extend did:web
SELECT ?method WHERE {
  ?method didm:extends <did:method:web> .
}

# Find methods that don't need a server (self-certifying)
SELECT ?method WHERE {
  ?method a didm:SelfCertifying .
}
```

## Migration Path

The schema.org model is **additive** — it doesn't replace the current JSON
registration. It extends it:

```jsonc
// Current registration (stays as-is)
{
  "name": "web",
  "status": "registered",
  "specification": "./specs/web/spec.md",

  // NEW: schema.org-typed metadata
  "@context": "https://w3c.github.io/did-extensions/vocab",
  "@type": "DIDMethod",
  "anchor": { "instrument": { "@type": "WebAPI" } },
  "extends": null,
  "calls": null,
  "additionalType": ["WebAnchored"]
}
```

Existing tools ignore the `@context`/`@type` fields. New tools can consume
them for discovery, comparison, and visualization.
