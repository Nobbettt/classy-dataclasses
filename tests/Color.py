from classy_dataclasses import ClassyDataclass, classy_field
from dataclasses import dataclass
from enum import Enum


def deserialize_name(x: str) -> str:
    return x.replace(" ", "_").lower()


def serialize_name(x: str) -> str:
    return x.replace("_", " ").upper()


class ColorSystem(Enum):
    HEX = "HEX"
    RGB = "RGB"


@dataclass
class RGB(ClassyDataclass):
    r: int = classy_field(default=None)
    g: int = classy_field(default=None)
    b: int = classy_field(default=None)

    @property
    def is_valid(self) -> bool:
        parts: list[int] = [self.r, self.g, self.b]
        return all([True if p >= 0 and p <= 255 else False for p in parts])


@dataclass
class Color(ClassyDataclass):
    name: str = classy_field(
        default="", decoder=deserialize_name, encoder=serialize_name
    )

    hex_value: float | None = classy_field(default=None)

    rgb_value: RGB = classy_field(default_factory=lambda: RGB())

    global_color_system: ColorSystem = classy_field(
        default=ColorSystem.HEX,
        is_static=True,
    )

    color_system: ColorSystem = classy_field(
        default=ColorSystem.HEX,
    )

    tags: list[str] = classy_field(default_factory=lambda: [])

    attributes: dict = classy_field(default_factory=lambda: {})
