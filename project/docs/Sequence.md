
# Class: Sequence




URI: [prodrules:Sequence](https://w3id.org/linkml/schemagrammar/prodrules/Sequence)


[![img](https://yuml.me/diagram/nofunky;dir:TB/class/[ProductionRule]++-%20lhs%200..1>[Sequence&#124;type:string%20%3F],[Disjunction]++-%20operands%200..*>[Sequence],[ProductionRule]++-%20rhs%200..1>[Sequence],[Sequence]^-[Disjunction],[Sequence]^-[AtomicSequence],[ProductionRule],[Disjunction],[AtomicSequence])](https://yuml.me/diagram/nofunky;dir:TB/class/[ProductionRule]++-%20lhs%200..1>[Sequence&#124;type:string%20%3F],[Disjunction]++-%20operands%200..*>[Sequence],[ProductionRule]++-%20rhs%200..1>[Sequence],[Sequence]^-[Disjunction],[Sequence]^-[AtomicSequence],[ProductionRule],[Disjunction],[AtomicSequence])

## Children

 * [AtomicSequence](AtomicSequence.md)
 * [Disjunction](Disjunction.md)

## Referenced by Class

 *  **None** *[lhs](lhs.md)*  <sub>0..1</sub>  **[Sequence](Sequence.md)**
 *  **None** *[operands](operands.md)*  <sub>0..\*</sub>  **[Sequence](Sequence.md)**
 *  **None** *[rhs](rhs.md)*  <sub>0..1</sub>  **[Sequence](Sequence.md)**

## Attributes


### Own

 * [type](type.md)  <sub>0..1</sub>
     * Range: [String](types/String.md)
