import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional, Tuple, Union

from lark import ParseTree, Token, Tree
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import SlotDefinition

from semdsl.datamodel.semdsl_model import AtomicSequence, Disjunction, SchemaGrammar
from semdsl.view.view import rule_lhs_symbol

logger = logging.getLogger(__name__)


@dataclass
class Mapper:
    """
    Base class for all mappers
    """

    schemagrammar: SchemaGrammar = None
    schemaview: SchemaView = None

    def transform(
        self,
        node: Union[ParseTree, Token, Tree],
        parent_slot: Optional[SlotDefinition] = None,
        target: str = None,
    ) -> Any:
        sv = self.schemaview
        class_defs = sv.all_classes()
        if target is None:
            if parent_slot and parent_slot.range:
                target = parent_slot.range
            else:
                candidates = [x.name for x in class_defs.values() if x.tree_root]
                if len(candidates) < 1:
                    candidates = [x.name for x in class_defs.values() if not x.abstract]
                [target] = candidates
        if parent_slot is None:
            parent_slot = SlotDefinition("TEMP", range=target)
        if isinstance(node, Tree):
            # print(node.pretty("--"))
            # print(node)
            token = node.data
            if not isinstance(token, Token):
                if isinstance(token, str):
                    token = Token("ALIAS", token)
                else:
                    raise AssertionError(f"Unexpected token type {type(token)}, token={token}")
            tgt_class, tgt_atomic_seq = self.lookup_token_value(token)
            if tgt_class:
                if tgt_class not in sv.all_classes():
                    raise ValueError(f"Unknown class {tgt_class}")
                target = tgt_class
            is_object = (
                tgt_class and not class_defs[tgt_class].abstract and not class_defs[tgt_class].mixin
            )
            # class_induced_slots = self.schemaview.class_induced_slots(tgt_class)
            if is_object:
                params = {}
                n = 0
                for child in node.children:
                    if isinstance(child, Tree) and isinstance(child.data, Token):
                        ks = child.data.value
                        k = self.lookup_token_source_slot(ks)
                        if k is None:
                            k = ks
                            sub_slot = SlotDefinition(k)
                        else:
                            sub_slot = self.schemaview.induced_slot(k, target)
                    else:
                        k = f"k{n}"
                        n += 1
                        sub_slot = SlotDefinition(k)
                    v = self.transform(child, sub_slot, sub_slot.range)
                    if v is not None:
                        if sub_slot.multivalued:
                            if isinstance(v, list):
                                params.setdefault(k, []).extend(v)
                            else:
                                # lists of length 1 are treated as singletons in AST
                                params.setdefault(k, []).append(v)
                        else:
                            params[k] = v
                type_designator = sv.get_type_designator_slot(target)
                if type_designator:
                    params[type_designator.name] = target
                return dict(**params)
            else:
                if len(node.children) > 1:
                    results = [
                        self.transform(child, parent_slot, target) for child in node.children
                    ]
                    if not parent_slot.multivalued:
                        if parent_slot.range in sv.all_classes():
                            raise AssertionError(
                                f"Unexpected number of children {len(node.children)}:: {tgt_class} // {node}"
                            )
                        results = " ".join(results)
                    return results
                if node.children:
                    return self.transform(node.children[0], parent_slot, target)
        if isinstance(node, Token):
            ranges = sv.slot_range_as_union(parent_slot)
            reprs = []
            for rng in ranges:
                if rng in sv.all_types():
                    typ = sv.induced_type(rng)
                    reprs.append(typ.uri)
            node_value = node.value
            python_value = None
            if "xsd:integer" in reprs:
                try:
                    python_value = int(node_value)
                except ValueError:
                    pass
            if python_value is None and ("xsd:float" in reprs or "xsd:double" in reprs):
                try:
                    python_value = float(node_value)
                except ValueError:
                    pass
            if python_value is None and "xsd:decimal" in reprs:
                try:
                    python_value = Decimal(node_value)
                except ValueError:
                    pass
            if "xsd:boolean" in reprs:
                if node_value is None:
                    # presence of a field indicates set to True
                    node_value = True
                try:
                    python_value = bool(node_value)
                except ValueError:
                    pass
            if python_value is None:
                python_value = node_value
                if node.type == "TYPE_STRING":
                    if python_value.startswith('"'):
                        python_value = python_value[1:]
                    if python_value.endswith('"'):
                        python_value = python_value[:-1]
            return python_value

    def lookup_token_value(self, token: Token) -> Optional[Tuple[str, AtomicSequence]]:
        for rule in self.schemagrammar.rules:
            if rule_lhs_symbol(rule) == token.value:
                if not isinstance(rule.rhs, AtomicSequence):
                    logger.warning(f"Object rules must be atomic {rule}")
                if rule.source_class:
                    return rule.source_class, rule.rhs
            if isinstance(rule.rhs, Disjunction):
                for op in rule.rhs.operands:
                    if isinstance(op, AtomicSequence):
                        if op.alias == token.value:
                            return op.source_class, op
        return None, None

    def lookup_token_source_slot(self, n: str) -> str:
        for rule in self.schemagrammar.rules:
            if rule_lhs_symbol(rule) == n:
                return rule.source_slot
