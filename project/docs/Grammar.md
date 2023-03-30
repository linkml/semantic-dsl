
# Class: Grammar




URI: [prodrules:Grammar](https://w3id.org/linkml/schemagrammar/prodrules/Grammar)


[![img](https://yuml.me/diagram/nofunky;dir:TB/class/[ProductionRule],[NonTerminal],[NonTerminal]<start_symbols%200..*-%20[Grammar&#124;description:string%20%3F;expressivity:GrammarType%20%3F;parser:ParserType%20%3F;pragmas:string%20*;syntax:GrammarSyntaxType%20%3F],[ProductionRule]<rules%200..*-++[Grammar])](https://yuml.me/diagram/nofunky;dir:TB/class/[ProductionRule],[NonTerminal],[NonTerminal]<start_symbols%200..*-%20[Grammar&#124;description:string%20%3F;expressivity:GrammarType%20%3F;parser:ParserType%20%3F;pragmas:string%20*;syntax:GrammarSyntaxType%20%3F],[ProductionRule]<rules%200..*-++[Grammar])

## Attributes


### Own

 * [➞description](grammar__description.md)  <sub>0..1</sub>
     * Range: [String](types/String.md)
 * [➞rules](grammar__rules.md)  <sub>0..\*</sub>
     * Range: [ProductionRule](ProductionRule.md)
 * [➞expressivity](grammar__expressivity.md)  <sub>0..1</sub>
     * Range: [GrammarType](GrammarType.md)
 * [➞start_symbols](grammar__start_symbols.md)  <sub>0..\*</sub>
     * Range: [NonTerminal](NonTerminal.md)
 * [➞parser](grammar__parser.md)  <sub>0..1</sub>
     * Range: [ParserType](ParserType.md)
 * [➞pragmas](grammar__pragmas.md)  <sub>0..\*</sub>
     * Range: [String](types/String.md)
 * [➞syntax](grammar__syntax.md)  <sub>0..1</sub>
     * Range: [GrammarSyntaxType](GrammarSyntaxType.md)
