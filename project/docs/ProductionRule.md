
# Class: ProductionRule




URI: [prodrules:ProductionRule](https://w3id.org/linkml/schemagrammar/prodrules/ProductionRule)


[![img](https://yuml.me/diagram/nofunky;dir:TB/class/[Sequence],[Sequence]<rhs%200..1-++[ProductionRule&#124;description:string%20%3F;is_terminal:boolean%20%3F;alias:string%20%3F],[Sequence]<lhs%200..1-++[ProductionRule],[NonTerminal]<lhs_symbol%200..1-%20[ProductionRule],[Grammar]++-%20rules%200..*>[ProductionRule],[NonTerminal],[Grammar])](https://yuml.me/diagram/nofunky;dir:TB/class/[Sequence],[Sequence]<rhs%200..1-++[ProductionRule&#124;description:string%20%3F;is_terminal:boolean%20%3F;alias:string%20%3F],[Sequence]<lhs%200..1-++[ProductionRule],[NonTerminal]<lhs_symbol%200..1-%20[ProductionRule],[Grammar]++-%20rules%200..*>[ProductionRule],[NonTerminal],[Grammar])

## Referenced by Class

 *  **None** *[➞rules](grammar__rules.md)*  <sub>0..\*</sub>  **[ProductionRule](ProductionRule.md)**

## Attributes


### Own

 * [description](description.md)  <sub>0..1</sub>
     * Range: [String](types/String.md)
 * [lhs_symbol](lhs_symbol.md)  <sub>0..1</sub>
     * Range: [NonTerminal](NonTerminal.md)
 * [lhs](lhs.md)  <sub>0..1</sub>
     * Range: [Sequence](Sequence.md)
 * [rhs](rhs.md)  <sub>0..1</sub>
     * Range: [Sequence](Sequence.md)
 * [is_terminal](is_terminal.md)  <sub>0..1</sub>
     * Range: [Boolean](types/Boolean.md)
 * [alias](alias.md)  <sub>0..1</sub>
     * Range: [String](types/String.md)
