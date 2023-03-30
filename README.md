# Semantic-DSL

For rapid development of semantically-backed Domain-Specific Languages (DSLs),

## Installation

```bash
pip install semdsl
```

## Usage

To illustrate the usage of semdsl, we will create a simple [LinkML](https://linkml.io) schema 
for part of the [Clue board game](https://en.wikipedia.org/wiki/Cluedo), in particular for
representing a hypothesis about who committed the misdeed, where, and with what.

We will *annotate* the schema with *grammar hints*, that can be used to generate the grammar for the DSL.


```yaml

```python
>>> schema = """
... id: https://example.org/clue
... name: clue
... imports:
...   - https://w3id.org/linkml/types
... classes:
...   ClueHypothesis:
...     attributes:
...       person:   # e.g. Colonel Mustard
...         annotations:
...           grammar.main: "WORD WORD"
...       location: # e.g. Kitchen
...         annotations:
...           grammar.main: "WORD"
...       weapon:   # e.g. Candlestick
...         annotations:
...           grammar.main: "WORD"
...     annotations:
...       grammar.main: >-
...         "<" person "in the" location "with the" weapon ">" 
... """

```

The idea is to be able to represent hypotheses using strings like `<Colonel Mustard in the Kitchen with the Candlestick>`.

We can then use the `DSLEngine` class to load the schema and generate a grammar:

```python
>>> from semdsl import DSLEngine
>>> engine = DSLEngine()
>>> engine.load_schema(schema)
>>> print(engine.lark_serialization)
from lark import Lark
...
class_clue_hypothesis : "<" person "in the" location "with the" weapon ">"
person : WORD WORD
location : WORD
weapon : WORD
...

```

The default is Lark syntax.

You can then use the generated grammar to parse serializations into pydantic objects that are schema conformant:

```python
>>> obj = engine.parse_as_object('<Colonel Mustard in the Kitchen with the Candlestick>')
>>> print(obj.location)
Kitchen
>>> print(obj.json())
   {"person": "Colonel Mustard", "location": "Kitchen", "weapon": "Candlestick"}

```

## Auto-assigning production rules

In the previous example we saw how we could *annotate* an existing schema with grammar rules

However, we can also *generate* grammar rules from the schema itself.

This is done by using the `grammar.main` annotation on a class, and then using the `grammar.auto` annotation on the attributes of that class. For example:

```python
>>> schema = """
... id: https://example.org/clue
... name: clue
... imports:
...   - https://w3id.org/linkml/types
... classes:
...   ClueHypothesis:
...     attributes:
...       person:   # e.g. Colonel Mustard
...       location: # e.g. Kitchen
...       weapon:   # e.g. Candlestick
... """

```

now we will create a new engine and load the schema, and generate a de-novo "functional-style" grammar:

```python
>>> engine = DSLEngine() ## create new DSLEngine
>>> engine.load_schema(schema)
>>> print(engine.lark_serialization)
from lark import Lark
...
class_clue_hypothesis : "ClueHypothesis(" slot_clue_hypothesis__person? slot_clue_hypothesis__location? slot_clue_hypothesis__weapon? ")"
slot_clue_hypothesis__person : "person=" TYPE_STRING
slot_clue_hypothesis__location : "location=" TYPE_STRING
slot_clue_hypothesis__weapon : "weapon=" TYPE_STRING
...

```

You can then use the generated grammar to parse strings into objects:

```python
>>> obj = engine.parse_as_object('ClueHypothesis(person="Colonel Mustard" location="Kitchen" weapon="Candlestick")')
>>> print(obj.location)
Kitchen

```

## Adding additional semantics

You can use the following metamodel element:

- [class_uri](https://w3id.prg/linkml/class_uri) 
- [slot_uri](https://w3id.prg/linkml/slot_uri) 

to assign URIs to classes and slots in your schema, which can be used in RDF serialization.

Here we extend our Clue schema, adding classes for the ranges of the slots in the main class:

```python
>>> schema = """
... id: https://example.org/clue
... name: clue
... prefixes:
...   linkml: https://w3id.org/linkml/
...   clue: https://example.org/clue/
...   schema: http://schema.org/
...   prov: http://www.w3.org/ns/prov#
...   dbpedia: http://dbpedia.org/ontology/
... imports:
...   - linkml:types
... classes:
...   NamedThing:
...     class_uri: schema:Thing
...     attributes:
...       id:
...         identifier: true
...       range: uriorcurie
...   Person:
...     class_uri: schema:Person
...     is_a: NamedThing
...   Location:
...     class_uri: schema:Location
...     is_a: NamedThing
...   Weapon:
...     class_uri: dbpedia:Weapon
...     is_a: NamedThing
...   ClueHypothesis:
...     class_uri: prov:Action
...     tree_root: true
...     attributes:
...       person:   # e.g. Colonel Mustard
...         slot_uri: prov:wasAssociatedWith
...         range: Person
...         annotations:
...           grammar.main: TYPE_URIORCURIE
...       location: # e.g. Kitchen
...         slot_uri: prov:atLocation
...         range: Location
...         annotations:
...           grammar.main: TYPE_URIORCURIE
...       weapon:   # e.g. Candlestick
...         slot_uri: prov:used
...         range: Weapon
...         annotations:
...           grammar.main: TYPE_URIORCURIE
...     annotations:
...       grammar.main: >-
...         "<" person "in the" location "with the" weapon ">"
... """

```

Now parse and export to a file. This time the input string uses CURIEs to represent the different things
in the Clue hypothesis.

```python
>>> engine = DSLEngine()
>>> engine.load_schema(schema)
>>> obj = engine.parse_as_object("< clue:ColonelMustard in the clue:Kitchen with the clue:Candlestick >")
>>> import yaml
>>> with open("tests/output/clue-output.yaml", "w", encoding="utf-8") as f:
...     yaml.dump(obj.dict(), f)

```

From here we can use LinkML to convert to an RDF serialization:

```bash
cd clue-output.yaml
linkml-convert clue-output -s clue_model.yaml -t ttl
````

Results:

```turtle
@prefix clue: <https://example.org/clue/> .
@prefix prov: <http://www.w3.org/ns/prov#> .

[] a prov:Action ;
    prov:atLocation clue:Kitchen ;
    prov:used clue:Candlestick ;
    prov:wasAssociatedWith clue:ColonelMustard .
```

## Command Line Interface

```
semdsl --help
```

## Limitations

### Restricted to Lark grammars

Currently, semdsl only supports Lark grammars. The framework is designed to allow extensibility, e.g. to ANTLR,
but this is currently unsupported.
