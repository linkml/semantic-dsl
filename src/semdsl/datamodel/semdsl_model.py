from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any, Union, Literal
from pydantic import BaseModel as BaseModel, Field
from linkml_runtime.linkml_model import Decimal

metamodel_version = "None"
version = "None"

class WeakRefShimBaseModel(BaseModel):
   __slots__ = '__weakref__'
    
class ConfiguredBaseModel(WeakRefShimBaseModel,
                validate_assignment = True, 
                validate_all = True, 
                underscore_attrs_are_private = True, 
                extra = 'forbid', 
                arbitrary_types_allowed = True):
    pass                    


class ParserType(str, Enum):
    
    earley = "earley"
    lalr = "lalr"
    
    

class GrammarType(str, Enum):
    
    ContextFree = "ContextFree"
    Regular = "Regular"
    ContextSensitive = "ContextSensitive"
    
    

class GrammarSyntaxType(str, Enum):
    
    lark = "lark"
    antlr = "antlr"
    ebnf = "ebnf"
    
    

class SchemaGrammar(ConfiguredBaseModel):
    """
    A SchemaGrammar (or DSL) is a set of production rules that are mapped to a schema
    """
    description: Optional[str] = Field(None, description="""A description of the DSL""")
    rules: Optional[List[ProductionRule]] = Field(default_factory=list, description="""A set of production rules""")
    expressivity: Optional[GrammarType] = Field(None, description="""The expressivity of the grammar, e.g. regular, context-free, etc.""")
    start_symbols: Optional[List[str]] = Field(default_factory=list, description="""All possible start symbols of the grammar""")
    parser: Optional[ParserType] = Field(None, description="""The parser used to parse the DSL, e.g. lalr, earley, etc.""")
    pragmas: Optional[List[str]] = Field(default_factory=list, description="""Pragmas that are used to control the parser""")
    syntax: Optional[GrammarSyntaxType] = Field(None, description="""The syntax of the DSL, e.g. Lark, ANTLR, etc.""")
    normalize_collections: Optional[bool] = Field(None, description="""If true, then collections are normalized to a single element""")
    


class ProductionRule(ConfiguredBaseModel):
    """
    A production rule is a mapping from a left-hand side (LHS) to a right-hand side (RHS). The LHS is a non-terminal symbol, and the RHS is a sequence of symbols, which may be terminals or non-terminals.
    """
    description: Optional[str] = Field(None, description="""A description of the element""")
    lhs_symbol: Optional[str] = Field(None, description="""The left-hand side of the production rule (applies only to CFGs or RGs)""")
    lhs: Optional[Union[Sequence,Disjunction,AtomicSequence]] = Field(None, description="""The left-hand side of the production rule. Note for CFGs or RGs, it may be more convenient to use lhs_symbol""")
    rhs: Optional[Union[Sequence,Disjunction,AtomicSequence]] = Field(None, description="""The right-hand side of the production rule""")
    rhs_serialized: Optional[str] = Field(None, description="""The right-hand side of the production rule, serialized as a string""")
    is_terminal: Optional[bool] = Field(None)
    alias: Optional[str] = Field(None)
    source_class: Optional[str] = Field(None, description="""The LinkML class definition the rule is mapped to""")
    source_slot: Optional[str] = Field(None, description="""The LinkML slot definition the rule is mapped to""")
    yields: Optional[Any] = Field(None)
    


class Sequence(ConfiguredBaseModel):
    """
    A sequence is a sequence of symbols, which may be terminals or non-terminals.
    """
    type: Literal["Sequence"] = Field("Sequence")
    serialized: Optional[str] = Field(None)
    


class Disjunction(Sequence):
    """
    A disjunction is a set of sequences that represent alternative ways to parse tokens
    """
    operands: Optional[List[Union[Sequence,Disjunction,AtomicSequence]]] = Field(default_factory=list, description="""The operands of the disjunction""")
    type: Literal["Disjunction"] = Field("Disjunction")
    serialized: Optional[str] = Field(None)
    


class AtomicSequence(Sequence):
    """
    An atomic sequence is a sequence of symbols, which may be terminals or non-terminals.
    """
    elements: Optional[List[Union[Union[Sequence,Disjunction,AtomicSequence], Union[Symbol,Terminal,NonTerminal]]]] = Field(default_factory=list, description="""The elements of the sequence""")
    alias: Optional[str] = Field(None)
    source_class: Optional[str] = Field(None, description="""The LinkML class definition the rule is mapped to""")
    type: Literal["AtomicSequence"] = Field("AtomicSequence")
    serialized: Optional[str] = Field(None)
    


class Symbol(ConfiguredBaseModel):
    """
    A symbol is a terminal or non-terminal symbol
    """
    type: Literal["Symbol"] = Field("Symbol")
    repetitions: Optional[str] = Field(None)
    


class Terminal(Symbol):
    """
    A terminal symbol is a symbol that represents a literal token
    """
    value: Optional[str] = Field(None)
    type: Literal["Terminal"] = Field("Terminal")
    repetitions: Optional[str] = Field(None)
    


class NonTerminal(Symbol):
    """
    A non-terminal symbol is a symbol that represents a non-terminal
    """
    name: Optional[str] = Field(None, description="""The name of the symbol""")
    source_class: Optional[str] = Field(None, description="""The LinkML class definition the rule is mapped to""")
    source_slot: Optional[str] = Field(None, description="""The LinkML slot definition the rule is mapped to""")
    type: Literal["NonTerminal"] = Field("NonTerminal")
    repetitions: Optional[str] = Field(None)
    



# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
SchemaGrammar.update_forward_refs()
ProductionRule.update_forward_refs()
Sequence.update_forward_refs()
Disjunction.update_forward_refs()
AtomicSequence.update_forward_refs()
Symbol.update_forward_refs()
Terminal.update_forward_refs()
NonTerminal.update_forward_refs()

