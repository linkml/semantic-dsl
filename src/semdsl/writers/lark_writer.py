from dataclasses import dataclass
from typing import Union

from linkml_runtime.utils.compile_python import compile_python

from semdsl.datamodel.semdsl_model import (
    AtomicSequence,
    Disjunction,
    NonTerminal,
    SchemaGrammar,
    Sequence,
    Terminal,
)
from semdsl.view.view import rule_lhs_symbol
from semdsl.writers.writer import Writer


@dataclass
class LarkWriter(Writer):
    """
    A Writer that generates Lark grammars
    """

    def write(self, sg: SchemaGrammar, **kwargs):
        self.emit("from lark import Lark\n\n")
        self.emit('s = r"""\n')
        for rule in sg.rules:
            lhs = rule_lhs_symbol(rule)
            self.emit(f"{lhs} : ")
            if rule.rhs_serialized:
                self.emit(rule.rhs_serialized)
            else:
                self.emit(self._serialize_sequence(rule.rhs))
            if rule.alias:
                # TODO: only make aliases on ASs
                self.emit(f" -> {rule.alias}")
            self.emit("\n")
        self.emit("URIORCURIE : CURIE\n")
        self.emit("CURIE : /\\S+/\n")
        self.emit("%import common.ESCAPED_STRING\n")
        self.emit("%import common.LETTER\n")
        self.emit("%import common.NUMBER\n")
        self.emit("%import common.FLOAT\n")
        self.emit("%import common.WORD\n")
        self.emit("%import common.WS\n")
        for pragma in sg.pragmas:
            if not pragma.startswith("%"):
                pragma = f"%{pragma}"
            self.emit(f"{pragma}\n")
        self.emit('"""\n')
        starts = ", ".join([repr(x) for x in sg.start_symbols])
        parser = "earley" if not sg.parser else str(sg.parser.value)
        self.emit(f"grammar = Lark(s, start=[{starts}], parser='{parser}')\n")

    def _serialize_sequence(self, rhs: Union[Sequence, Terminal]) -> str:
        if isinstance(rhs, Disjunction):
            return " | ".join(self._serialize_sequence(operand) for operand in rhs.operands)
        if isinstance(rhs, AtomicSequence):
            if rhs.serialized:
                return rhs.serialized
            s = " ".join(self._serialize_sequence(element) for element in rhs.elements)
            if rhs.alias:
                s += f" -> {rhs.alias}"
            return s
        if isinstance(rhs, NonTerminal):
            return rhs.name + (rhs.repetitions or "")
        if isinstance(rhs, Terminal):
            # return repr(rhs.value)
            return f'"{rhs.value}"' + (rhs.repetitions or "")
        raise AssertionError(f"Unexpected sequence type {type(rhs)}")
