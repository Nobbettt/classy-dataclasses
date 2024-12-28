# Classy Dataclasses

**Classy Dataclasses** is a Python library that extends the functionality of Python's built-in dataclasses, making it easier to serialize, deserialize, manage nested structures, and more.

## Features ✅

- **Serialization**: Effortless serialization and deserialization of dataclasses to and from JSON and Python dictionaries. Supports:
  - Supports nested dataclasses and enums
  - Customizable encoders and decoders.
- **Data storage**: Save dataclasses to JSON files and recreate them from JSON data.
- **Copyable**: Easily deep-copy dataclasses.
- **Static variables**: Support for static class variables in dataclasses.
- **Improved data modelling**: Model your data in a structured way without limitations.

## Installation 🛠️

To install Classy Dataclasses, you can use pip:

```bash
pip install classy-dataclasses
```

```bash
# Alternatively, using poetry:
poetry add classy-dataclasses
```

Requires Python 3.10 or higher.

## Usage 💡

Here’s a quick example of how to use Classy Dataclasses showcasing the main features.

### Data Modelling

Note in the example,

- **color_system** and **global_color_system** are of type Enum<ColorSystem>,
- **rgb_value** is a nested dataclass
- **global_color_system** is a static class variable

```python
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
    name: str = classy_field(default="", decoder=deserialize_name, encoder=serialize_name)
    hex_value: float | None = classy_field(default=None)
    rgb_value: RGB = classy_field(default_factory=lambda: RGB())
    global_color_system: ColorSystem = classy_field(default=ColorSystem.HEX, is_static=True)
    color_system: ColorSystem = classy_field(default=ColorSystem.HEX)
    tags: list[str] = classy_field(default_factory=lambda: [])
    attributes: dict = classy_field(default_factory=lambda: {})
```

## Deserialization and Load

```python
# Example data
color_dict: dict = {
"name": "SKY BLUE",
  "hex_value": "#1425e0",
  "rgb_value": {
    "r": 20,
    "g": 37,
    "b": 224
  },
  "global_color_system": "HEX",
  "color_system": "RGB",
  "tags": ["sky", "ocean"],
  "attributes": {
    "like": True,
    "favorite": False
  }
}

color_json_str: str = json.dumps(color_dict)

color_json_path: str = "path_to_your_file/sky_blue.json"

# Initialize from dictionary (use this when you have a dictionary representing the dataclass)
color_dataclass: Color = Color.from_dict(color_dict)

# Initialize form JSON string (use this when you have a JSON-formatted string)
color_dataclass: Color = Color.from_json(color_dict)

# Initialize from json file (use this when you have a path to a JSON file)
color_dataclass: Color = Color.load_from_json(color_json_path)
```

### Serialization and Save

```python
Serialize to dictionary
color_dict: dict = color_dataclass.to_dict(serialize_fields=True)

# Serialize JSON string
color_dict: str = color_dataclass.to_json(serialize_fields=True)
```

Note, setting **serialize_fields=False** will convert the dataclass to a dictionary or JSON string without serializing its fields.

## Contributing ❤️‍🩹

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License 📃

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

For more information, please refer to the documentation or the source code.
