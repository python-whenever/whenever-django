from __future__ import annotations

import datetime as _stdlib
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from django.core.exceptions import ValidationError
from django.db import models

if TYPE_CHECKING:
    from django.db.models import Model

from ..descriptors import CompositeFieldDescriptor
from ._base import WheneverField

_UTC = _stdlib.timezone.utc


class _CompositeWheneverField(WheneverField):
    """Base for fields that store a UTC timestamp plus paired metadata column.

    Subclasses set ``paired_suffix`` and ``paired_max_length`` to control
    the paired CharField, and provide module-level ``compose_fn`` /
    ``decompose_fn`` callables that bridge between the whenever type and
    the two-column representation.
    """

    stdlib_type = None
    paired_suffix: str
    paired_max_length: int
    compose_fn: Callable[..., Any]
    decompose_fn: Callable[..., tuple[_stdlib.datetime, str]]

    def get_internal_type(self) -> str:
        return "DateTimeField"

    def contribute_to_class(
        self, cls: type[Model], name: str, private_only: bool = False
    ) -> None:
        super().contribute_to_class(cls, name, private_only=private_only)

        paired_field: models.CharField[str, str] = models.CharField(
            max_length=self.paired_max_length,
            null=self.null,
            blank=self.blank,
            editable=False,
        )
        paired_field.creation_counter = self.creation_counter - 1
        self._paired_attname = f"{self.attname}{self.paired_suffix}"
        cls.add_to_class(self._paired_attname, paired_field)

        descriptor = CompositeFieldDescriptor(
            field=self,
            paired_attname=self._paired_attname,
            compose=self.compose_fn,
            decompose=self.decompose_fn,
        )
        setattr(cls, self.name, descriptor)

    def _from_db(self, value: Any, connection: Any) -> _stdlib.datetime:
        dt: _stdlib.datetime
        if isinstance(value, _stdlib.datetime):
            dt = value
        else:
            dt = _stdlib.datetime.fromisoformat(str(value))
        # The column stores UTC. SQLite and some backends return naive
        # datetimes — restoring UTC is safe because only UTC is ever stored.
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_UTC)
        return dt

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, self.whenever_type):
            return self._to_db(value)
        if isinstance(value, _stdlib.datetime):
            return value
        raise TypeError(
            f"{self.__class__.__name__} expects "
            f"{self.whenever_type.__name__}, "
            f"got {type(value).__name__}."
        )

    def pre_save(self, model_instance: Any, add: bool) -> Any:
        value = model_instance.__dict__.get(self.attname)
        if value is None:
            return None
        if isinstance(value, self.whenever_type):
            _, meta_value = self.decompose_fn(value)
            model_instance.__dict__[self._paired_attname] = meta_value
            return self._to_db(value)
        if isinstance(value, _stdlib.datetime):
            return value
        raise TypeError(
            f"{self.__class__.__name__} expects "
            f"{self.whenever_type.__name__}, "
            f"got {type(value).__name__}."
        )

    def to_python(self, value: Any) -> Any:
        if value is None or isinstance(value, self.whenever_type):
            return value
        if isinstance(value, str):
            try:
                return self._parse(value)
            except (ValueError, TypeError) as e:
                raise ValidationError(
                    f"Invalid value for {self.__class__.__name__}: {e}"
                ) from e
        raise ValidationError(
            f"Cannot convert {type(value).__name__} to {self.whenever_type.__name__}."
        )

    def value_to_string(self, obj: Any) -> str:
        value = getattr(obj, self.name, None)
        if value is None:
            return ""
        return str(value)
