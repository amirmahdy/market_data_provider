import enum
from django.utils.translation import gettext_lazy as _


def to_snake(string_to_convert: str) -> str:
    import re

    string_to_convert = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", string_to_convert)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", string_to_convert).lower()


def to_camel(string_to_convert: str):
    converted = ""
    next_is_capital = False
    for i, c in enumerate(string_to_convert):
        if c == "_":
            next_is_capital = i != 0 and converted != ""
            continue

        if c == c.upper():
            next_is_capital = True

        if i == 0:
            converted += c.lower()
            next_is_capital = False
            continue

        if next_is_capital:
            converted += c.upper()
            next_is_capital = False
        else:
            converted += c.lower()

    return converted


def to_fullcase(string_to_convert: str):
    converted = to_camel(string_to_convert)
    return converted[0].upper() + converted[1:]


def snake_to_titlecase(string_to_convert: str) -> str:
    return string_to_convert.replace("_", " ").title()


@enum.unique
class AutoNameEnum(str, enum.Enum):
    @classmethod
    def get_members(cls):
        return [e.name for e in cls.__members__.values()]

    @classmethod
    def get_labels(cls):
        return [e.value for e in cls.__members__.values()]

    @classmethod
    def as_dict(cls):
        return [{e.name: e.value} for e in cls.__members__.values()]

    @classmethod
    def as_tuple(cls):
        return [(e.name, e.value) for e in cls.__members__.values()]

    @property
    def text(self):
        return _(snake_to_titlecase(self.value))

    @property
    def text_capital(self):
        return self.value.upper()

    def __str__(self) -> str:
        return self.value

    def _generate_next_value_(name, start, count, last_values):
        return name
