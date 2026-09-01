# DID Method Naming Convention

## Principle

A DID method name should describe **what the method fundamentally does or where
it anchors identity** — not reference brands, products, or opaque acronyms.

This follows the same principle as clean code: a repository method called
`repo.hashPassword()` tells you what it does; `repo.hp7()` does not. DID method
names are the public API of the identity ecosystem — they should be
self-documenting.

## Why Descriptive Names Matter

1. **Developer clarity** — a developer scanning the [catalogue](https://w3c.github.io/did-extensions/)
   should understand what each method does from the name alone, without clicking
   through to each specification
2. **Reduced IP/trademark conflicts** — descriptive functional terms are
   inherently non-brandable, avoiding the governance burden of adjudicating
   trademark disputes (see [did-extensions#597](https://github.com/w3c/did-extensions/issues/597),
   [did-methods#10](https://github.com/decentralized-identity/did-methods/issues/10#issuecomment-2501758865))
3. **Ecosystem coherence** — consistent naming creates a self-documenting
   catalogue where method categories emerge naturally
4. **Composability** — verb-based names make `extends` and `calls` relationships
   immediately readable (see [Composability](#composability) below)

## Current Landscape

The existing registered methods use inconsistent naming approaches:

| Naming Pattern | Examples | Clarity Level |
|---|---|---|
| Describes anchor/mechanism | `did:web`, `did:key`, `did:peer`, `did:pkh` | High — immediately clear |
| Abbreviates platform/chain | `did:ethr`, `did:sol`, `did:tz` | Medium — clear within ecosystem |
| Acronym of project name | `did:ion` (Identity Overlay Network), `did:dht` (Distributed Hash Table) | Low-Medium — requires lookup |
| Branded/opaque | `did:v1`, `did:cel`, `did:tdw` | Low — requires prior knowledge |

## The Verb/Action Model

Method names should follow **the same convention as code**: verbs and nouns that
describe behavior. Think of the DID scheme as a namespace and the method name as
a function:

```
did:<what-it-does>:<specific-identifier>
```

This is analogous to:

```
repository.method(args)
identity.web(domain)
identity.key(publicKey)
identity.peer(endpoint)
```

### Naming as Actions

| Action/Anchor | Method | Reads as |
|---|---|---|
| Resolve via web domain | `did:web` | "identity anchored to the **web**" |
| Derive from public key | `did:key` | "identity derived from a **key**" |
| Exchange between peers | `did:peer` | "identity for **peer**-to-peer" |
| Anchor to Ethereum | `did:ethr` | "identity on **Ethereum**" |
| Hash of public key | `did:pkh` | "identity from a **public key hash**" |
| Resolve via DNS | `did:dns` | "identity anchored to **DNS**" |
| Verifiable web history | `did:webvh` | "identity on **web** with **verifiable history**" |

The name should answer one of:

- **Where** does identity anchor? → `did:web`, `did:dns`, `did:ethr`
- **What** cryptographic primitive? → `did:key`, `did:pkh`, `did:jwk`
- **How** does resolution work? → `did:peer`, `did:self`, `did:dht`

### Compound Names for Extended Behavior

When a method extends or specializes another, use **compound names** that read
like method chaining in code:

```
base.method()              → did:web
base.method().extend()     → did:webvh    (web + verifiable history)
base.method().onChain()    → did:webtx    (web + transaction anchored)
```

| Base | Extension | Compound Name | Meaning |
|---|---|---|---|
| `web` | verifiable history | `did:webvh` | Web-anchored with cryptographic log |
| `key` | multicodec | `did:keym` | Key-derived with multicodec prefix |
| `peer` | numbered algorithms | `did:peer` | Peer with numalgo variants |
| `sns` | Solana name service | `did:sns` | Identity via Solana naming service |

The compound pattern keeps the ecosystem scannable: if you know `did:web`, you
can infer that `did:webvh` is a web-based variant with additional properties.

## Composability

DID methods don't exist in isolation — they **compose**. The naming convention
should make composition relationships visible:

### `extends` — Method B builds on Method A's resolution

```
did:webvh  extends  did:web     ← adds verifiable history to web resolution
did:plc    extends  did:web     ← adds portable location to web anchoring
```

When method B extends method A, method B's name should **contain or reference**
method A's name, so the relationship is immediately clear.

### `calls` — Method B delegates resolution to Method A

```
did:sns  calls  did:sol    ← SNS names resolve through Solana
did:ens  calls  did:ethr   ← ENS names resolve through Ethereum
```

When method B calls method A for resolution, method B's name should describe
its own function (the naming service), not the underlying chain.

### Reading Composition Like Code

```python
# Extends — like class inheritance
class WebVH(Web):           # did:webvh extends did:web
    def resolve(self):
        doc = super().resolve()
        return self.verify_history(doc)

# Calls — like dependency injection
class SNS:                  # did:sns calls did:sol
    def __init__(self, sol: Solana):
        self.resolver = sol
    def resolve(self, name):
        address = self.lookup_name(name)
        return self.resolver.resolve(address)
```

This is why descriptive names matter: `did:webvh extends did:web` reads
naturally. `did:xyz extends did:abc` tells you nothing.

## Guidelines

### DO: Name after the anchoring mechanism or fundamental property

```
✓ did:web    — anchors to web domains
✓ did:key    — derives from cryptographic keys
✓ did:peer   — operates peer-to-peer
✓ did:dns    — anchors to DNS records
✓ did:ethr   — anchors to Ethereum
```

### DO: Use recognizable abbreviations for well-known platforms

When the method is specific to a blockchain or network, abbreviating the
platform name is acceptable if widely recognized:

- `did:ethr` — Ethereum (widely known abbreviation)
- `did:sol` — Solana (widely known abbreviation)
- `did:btcr` — Bitcoin (widely known abbreviation + resolver)

### DO: Use compound names that reveal composition

```
✓ did:webvh  — clearly extends did:web
✓ did:keym   — clearly extends did:key
```

### DON'T: Use internal project names, version numbers, or marketing terms

```
✗ did:v1     — version number, not a description
✗ did:cel    — brand name, opaque to outsiders
✗ did:tdw    — acronym requiring explanation
```

### DON'T: Use acronyms that require explanation

If the acronym doesn't immediately convey the method's purpose to a developer
unfamiliar with your project, expand it or choose a more descriptive term.

### DON'T: Hide the `extends` or `calls` relationship

If your method is fundamentally "web + something", don't name it `did:nova` —
name it `did:web<suffix>` so the relationship is visible.

## Suggested Categories

Method names fall into natural categories based on their anchoring mechanism,
analogous to package namespaces in code:

| Category | Analogy | Description | Name Examples |
|---|---|---|---|
| **Key-derived** | `crypto.*` | Identity derived directly from cryptographic keys | `did:key`, `did:pkh`, `did:jwk` |
| **Web-anchored** | `http.*` | Identity anchored to web domains or URLs | `did:web`, `did:webvh` |
| **Ledger-anchored** | `chain.*` | Identity anchored to a specific blockchain/ledger | `did:ethr`, `did:sol`, `did:btcr` |
| **Service-anchored** | `service.*` | Identity anchored to a naming service or registry | `did:ens`, `did:dns`, `did:sns` |
| **Peer/local** | `local.*` | Identity for direct peer-to-peer or offline use | `did:peer`, `did:self` |
| **DHT-anchored** | `dht.*` | Identity anchored to distributed hash tables | `did:dht` |

## Self-Check for Method Authors

Before choosing a name, ask yourself:

1. **Can a developer guess what this method does from the name alone?**
   If not, choose a more descriptive name.

2. **Does this method extend another?** If yes, does the name make the
   `extends` relationship visible? (e.g., `did:webvh` clearly relates to `did:web`)

3. **Does this method delegate to another?** If yes, does the name describe
   your method's unique function? (e.g., `did:sns` describes the naming service,
   not the underlying Solana chain)

4. **Would two developers independently arrive at the same name?**
   Descriptive names have this property; branded names do not.

5. **Is the name future-proof?** Will it still make sense if the implementation
   migrates to a different chain or technology?

## Applying This Convention

This convention is a **recommendation**, not a requirement for registration.
The registration process remains mechanical (valid JSON, spec URL, no
conflicts). However, authors are encouraged to follow these guidelines because:

- The [interactive explorer](https://chongkan.github.io/did-extensions/explorer.html)
  uses naming patterns to surface method relationships
- The overlap detection in the Self-Assessment form flags methods with similar
  names that may indicate unintentional duplication
- Compound names make the ecosystem's composition graph readable at a glance
