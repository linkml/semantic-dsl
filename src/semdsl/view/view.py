from typing import Optional

from semdsl.datamodel.semdsl_model import (
    AtomicSequence,
    Disjunction,
    NonTerminal,
    ProductionRule,
    SchemaGrammar,
    Sequence,
)


def rule_by_non_terminal(sg: SchemaGrammar, nt: str) -> Optional[ProductionRule]:
    for rule in sg.rules:
        if rule_lhs_symbol(rule) == nt:
            return rule
    return None


def rule_lhs_symbol(rule: ProductionRule) -> Optional[str]:
    if rule.lhs_symbol:
        return rule.lhs_symbol
    if rule.lhs:
        return _sequence_lhs_symbol(rule.lhs)


def _sequence_lhs_symbol(sequence: Sequence) -> Optional[str]:
    if isinstance(sequence, Disjunction):
        if len(sequence.operands) != 1:
            raise ValueError(f"Disjunction {sequence} must have exactly one operand; in {rule}")
        return lhs_symbol(sequence.operands[0])
    if isinstance(sequence, AtomicSequence):
        if len(sequence.elements) != 1:
            raise ValueError(f"AtomicSequence {sequence} must have exactly one element; in {rule}")
        el = sequence.elements[0]
        if not isinstance(el, NonTerminal):
            raise ValueError(
                f"AtomicSequence {sequence} must have exactly one NonTerminal element; in {rule}"
            )
        return el.name
    raise AssertionError(f"Unexpected sequence type {type(sequence)}")
