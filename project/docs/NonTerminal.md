
# Class: NonTerminal




URI: [prodrules:NonTerminal](https://w3id.org/linkml/schemagrammar/prodrules/NonTerminal)


[![img](https://yuml.me/diagram/nofunky;dir:TB/class/[Symbol],[Grammar]-%20start_symbols%200..*>[NonTerminal&#124;name:string;source_class:string%20%3F;source_slot:string%20%3F;type(i):string%20%3F],[ProductionRule]-%20lhs_symbol%200..1>[NonTerminal],[Symbol]^-[NonTerminal],[ProductionRule],[Grammar])](https://yuml.me/diagram/nofunky;dir:TB/class/[Symbol],[Grammar]-%20start_symbols%200..*>[NonTerminal&#124;name:string;source_class:string%20%3F;source_slot:string%20%3F;type(i):string%20%3F],[ProductionRule]-%20lhs_symbol%200..1>[NonTerminal],[Symbol]^-[NonTerminal],[ProductionRule],[Grammar])

## Parents

 *  is_a: [Symbol](Symbol.md)

## Referenced by Class

 *  **None** *[➞start_symbols](grammar__start_symbols.md)*  <sub>0..\*</sub>  **[NonTerminal](NonTerminal.md)**
 *  **None** *[lhs_symbol](lhs_symbol.md)*  <sub>0..1</sub>  **[NonTerminal](NonTerminal.md)**

## Attributes


### Own

 * [name](name.md)  <sub>1..1</sub>
     * Range: [String](types/String.md)
 * [source_class](source_class.md)  <sub>0..1</sub>
     * Range: [String](types/String.md)
 * [source_slot](source_slot.md)  <sub>0..1</sub>
     * Range: [String](types/String.md)

### Inherited from Symbol:

 * [type](type.md)  <sub>0..1</sub>
     * Range: [String](types/String.md)
