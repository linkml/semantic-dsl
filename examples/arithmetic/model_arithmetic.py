from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from linkml_runtime.linkml_model import Decimal
from pydantic import BaseModel as BaseModel
from pydantic import Field

metamodel_version = "None"
version = "None"


class WeakRefShimBaseModel(BaseModel):
    __slots__ = "__weakref__"


class ConfiguredBaseModel(
    WeakRefShimBaseModel,
    validate_assignment=True,
    validate_all=True,
    underscore_attrs_are_private=True,
    extra="forbid",
    arbitrary_types_allowed=True,
):
    pass


class OperatorSymbol(str, Enum):
    PLUS_SIGN = "+"
    _ = "-"


class Container(ConfiguredBaseModel):
    expressions: Optional[List[Union[Expression, CompoundExpression, Constant, Variable]]] = Field(
        default_factory=list
    )


class Expression(ConfiguredBaseModel):
    type: Literal["Expression"] = Field("Expression")


class CompoundExpression(Expression):
    operator: Optional[OperatorSymbol] = Field(None)
    left: Optional[Union[Expression, CompoundExpression, Constant, Variable]] = Field(None)
    right: Optional[Union[Expression, CompoundExpression, Constant, Variable]] = Field(None)
    type: Literal["CompoundExpression"] = Field("CompoundExpression")


class Constant(Expression):
    value: Optional[Union[float, int]] = Field(None)
    type: Literal["Constant"] = Field("Constant")


class Variable(Expression):
    name: Optional[str] = Field(None)
    type: Literal["Variable"] = Field("Variable")


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
Container.update_forward_refs()
Expression.update_forward_refs()
CompoundExpression.update_forward_refs()
Constant.update_forward_refs()
Variable.update_forward_refs()
