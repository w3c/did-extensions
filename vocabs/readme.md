# Machine-readable specification for the DID Core vocabulary

The folder contains:

* [RDFS vocabulary definition](https://www.w3.org/TR/rdf11-primer/#section-vocabulary) in [Turtle](./DID-core.ttl) and [JSON-LD](./DID-core.jsonld) formats.
* RDF Graph constraints defined using
  * the [Shapes Constraint Language (SHACL)](https://www.w3.org/TR/shacl/) in [Turtle](./DID-core-shape.ttl) format;
  * the [Shape Expressions (ShEx)](http://shex.io/shex-primer/) in [ShExC](./DID-core-shape.shex) format.

## Notes

* The URI-s used for the terms and the vocabulary as a whole may still change.
* SHACL and ShEx are [_alternative_ formats](https://book.validatingrdf.com/bookHtml013.html) to express constraints on an RDF Graph and provide validity checking. 
