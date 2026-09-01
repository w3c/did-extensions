# Machine-readable specification for the DID Core vocabulary

The folder contains:

* [RDFS vocabulary definition](https://www.w3.org/TR/rdf11-primer/#section-vocabulary) in [Turtle](./vocab.ttl), [JSON-LD](./vocab.jsonld), and [RDF/XML](./vocab.rdf) formats, as well as a human readable [HTML](./vocab.html) document.
* JSON-Context file
  * the core [JSON-LD Context](./context.jsonld);
  * a human readable [HTML](./context.html) version of the context file.
* RDF Graph constraints defined using
  * the [Shapes Constraint Language (SHACL)](https://www.w3.org/TR/shacl/) in [Turtle](./shacl.ttl) and [JSON-LD](./shacl.jsonld) formats;
  * the [Shape Expressions (ShEx)](http://shex.io/shex-primer/) in [ShExC](./shex.shex) format.
  
  These file patterns are used to set up the redirects and content negotiations from `https://www.w3.org/ns` to the vocabulary, context, and constraint files.

## Notes

* SHACL and ShEx are [_alternative_ formats](https://book.validatingrdf.com/bookHtml013.html) to express constraints on an RDF Graph and provide validity checking.
* The [HTML version of the context file](./context.html) is currently not served from `https://www.w3.org/ns` 
