
# prodrules


**metamodel version:** 1.7.0

**version:** None


This is the project description.


### Classes

 * [Grammar](Grammar.md)
 * [ProductionRule](ProductionRule.md)
 * [Sequence](Sequence.md)
     * [AtomicSequence](AtomicSequence.md)
     * [Disjunction](Disjunction.md)
 * [Symbol](Symbol.md)
     * [NonTerminal](NonTerminal.md)
     * [Terminal](Terminal.md)

### Mixins


### Slots

 * [alias](alias.md)
 * [description](description.md)
 * [elements](elements.md)
 * [➞description](grammar__description.md)
 * [➞expressivity](grammar__expressivity.md)
 * [➞parser](grammar__parser.md)
 * [➞pragmas](grammar__pragmas.md)
 * [➞rules](grammar__rules.md)
 * [➞start_symbols](grammar__start_symbols.md)
 * [➞syntax](grammar__syntax.md)
 * [is_terminal](is_terminal.md)
 * [lhs](lhs.md)
 * [lhs_symbol](lhs_symbol.md)
 * [name](name.md)
 * [operands](operands.md)
 * [rhs](rhs.md)
 * [source_class](source_class.md)
 * [source_slot](source_slot.md)
 * [type](type.md)
 * [value](value.md)

### Enums

 * [GrammarSyntaxType](GrammarSyntaxType.md)
 * [GrammarType](GrammarType.md)
 * [ParserType](ParserType.md)

### Subsets


### Types


#### Built in

 * **Bool**
 * **Curie**
 * **Decimal**
 * **ElementIdentifier**
 * **NCName**
 * **NodeIdentifier**
 * **URI**
 * **URIorCURIE**
 * **XSDDate**
 * **XSDDateTime**
 * **XSDTime**
 * **float**
 * **int**
 * **str**

#### Defined

 * [Boolean](types/Boolean.md)  (**Bool**)  - A binary (true or false) value
 * [Curie](types/Curie.md)  (**Curie**)  - a compact URI
 * [Date](types/Date.md)  (**XSDDate**)  - a date (year, month and day) in an idealized calendar
 * [DateOrDatetime](types/DateOrDatetime.md)  (**str**)  - Either a date or a datetime
 * [Datetime](types/Datetime.md)  (**XSDDateTime**)  - The combination of a date and time
 * [Decimal](types/Decimal.md)  (**Decimal**)  - A real number with arbitrary precision that conforms to the xsd:decimal specification
 * [Double](types/Double.md)  (**float**)  - A real number that conforms to the xsd:double specification
 * [Float](types/Float.md)  (**float**)  - A real number that conforms to the xsd:float specification
 * [Integer](types/Integer.md)  (**int**)  - An integer
 * [Ncname](types/Ncname.md)  (**NCName**)  - Prefix part of CURIE
 * [Nodeidentifier](types/Nodeidentifier.md)  (**NodeIdentifier**)  - A URI, CURIE or BNODE that represents a node in a model.
 * [Objectidentifier](types/Objectidentifier.md)  (**ElementIdentifier**)  - A URI or CURIE that represents an object in the model.
 * [String](types/String.md)  (**str**)  - A character string
 * [Time](types/Time.md)  (**XSDTime**)  - A time object represents a (local) time of day, independent of any particular day
 * [Uri](types/Uri.md)  (**URI**)  - a complete URI
 * [Uriorcurie](types/Uriorcurie.md)  (**URIorCURIE**)  - a URI or a CURIE
