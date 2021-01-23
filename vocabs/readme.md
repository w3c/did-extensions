# Machine-readable specification for the DID Core vocabulary

The folder contains:

* [RDFS vocabulary definition](https://www.w3.org/TR/rdf11-primer/#section-vocabulary) in [Turtle](./DID-core-v1.ttl), [JSON-LD](./DID-core-v1.jsonld), and [RDF/XML](./DID-core-v1.rdf) formats.
* RDF Graph constraints defined using
  * the [Shapes Constraint Language (SHACL)](https://www.w3.org/TR/shacl/) in [Turtle](./DID-core-shape-v1.ttl) and [JSON-LD](./DID-core-shape-v1.jsonld) formats;
  * the [Shape Expressions (ShEx)](http://shex.io/shex-primer/) in [ShExC](./DID-core-shape-v1.shex) format.

## Notes

* SHACL and ShEx are [_alternative_ formats](https://book.validatingrdf.com/bookHtml013.html) to express constraints on an RDF Graph and provide validity checking. 
