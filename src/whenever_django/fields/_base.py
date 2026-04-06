from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.db import models


class WheneverField(models.Field):
    """Base class for all whenever model fields.

    Subclasses must define:
      - whenever_type: the whenever class (e.g., whenever.Instant)
      - stdlib_type: the corresponding stdlib class (e.g., datetime.datetime)
      - _from_db(value, connection): convert DB value to whenever type
      - _to_db(value): convert whenever type to DB-storable value
      - _parse(value): parse a string/form value into the whenever type
    """

    whenever_type: type = None  # type: ignore[assignment]
    stdlib_type: type | None = None

    def __init__(
        self, *args: Any, from_stdlib: bool = False, **kwargs: Any
    ) -> None:
        if from_stdlib and self.stdlib_type is None:
            raise TypeError(
                f"{self.__class__.__name__} does not support from_stdlib=True "
                f"(no stdlib equivalent exists)."
            )
        self.from_stdlib = from_stdlib
        super().__init__(*args, **kwargs)

    def deconstruct(self) -> tuple[str, str, list[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        if self.from_stdlib:
            kwargs["from_stdlib"] = True
        return name, path, args, kwargs

    def from_db_value(
        self,
        value: Any,
        expression: Any,
        connection: Any,
    ) -> Any:
        if value is None:
            return None
        return self._from_db(value, connection)

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
        if self.stdlib_type and isinstance(value, self.stdlib_type):
            return self.whenever_type(value)
        raise ValidationError(
            f"Cannot convert {type(value).__name__} to "
            f"{self.whenever_type.__name__}."
        )

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, self.whenever_type):
            return self._to_db(value)
        if self.from_stdlib and self.stdlib_type and isinstance(
            value, self.stdlib_type
        ):
            return self._to_db(self.whenever_type(value))
        if not isinstance(value, self.whenever_type):
            raise TypeError(
                f"{self.__class__.__name__} expects "
                f"{self.whenever_type.__name__}, "
                f"got {type(value).__name__}. "
                f"Set from_stdlib=True to enable automatic coercion."
            )
        return self._to_db(value)

    def value_to_string(self, obj: Any) -> str:
        value = self.value_from_object(obj)
        if value is None:
            return ""
        return str(self._to_db(value))

    def _from_db(self, value: Any, connection: Any) -> Any:
        raise NotImplementedError

    def _to_db(self, value: Any) -> Any:
        raise NotImplementedError

    def _parse(self, value: str) -> Any:
        raise NotImplementedError
