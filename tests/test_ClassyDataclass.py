import pytest
from os.path import dirname, abspath, join
from enum import Enum
from typing import Callable

from . import Color, ColorSystem, load_json_files_with_prefix
from classy_dataclasses.ClassyDataclass import ClassyDataclass


data_folder = join(dirname(abspath(__file__)), "data")
json_data_dict = load_json_files_with_prefix(data_folder, prefix="test_")


@pytest.mark.parametrize("json_dict, test_name", json_data_dict)
def test_color_serialization_deserialization(json_dict: dict, test_name: str):
    """
    Tests the serialization and deserialization by loading a json file, converting it to a dataclass and back.

    Args:
        json_dict (dict): JSON serialized dictionary representing Color dataclass.
        test_name (str): Name of the test file.
    """
    color_obj: Color = Color.from_dict(json_dict)
    color_dict: dict = color_obj.to_dict(serialize_fields=True)
    color_obj2: Color = Color.from_dict(color_dict)

    assert (json_dict == color_dict) or (
        not json_dict and not color_dict
    ), f"Serialize & deserialize {test_name} failed (1)"

    assert (color_obj == color_obj2) or (
        not color_obj and not color_obj2
    ), f"Serialize & deserialize {test_name} failed (2)"


def test_static_variable():
    """Test if static dataclass variable acts static ."""
    c1 = Color(name="red")
    c2 = Color(name="pink")
    c2.global_color_system = ColorSystem.RGB
    c1.global_color_system = ColorSystem.HEX
    assert (
        c1.global_color_system == c2.global_color_system
    ), "Static variable test failed (1)"

    assert c1.name != c2.name, "Static variable test failed (2)"


def modify_values(var_value):
    """Helper function for testing copy function.

    Args:
        var_value (Any): Any values which an attribute of a dataclass can have.

    Returns:
        _type_: Returns modified value of the same type as the input.
    """
    if isinstance(var_value, bool):
        # Modify boolean value by negating it
        var_value = not var_value
    elif isinstance(var_value, (int, float)):
        # Modify numeric values
        var_value += 1
    elif isinstance(var_value, str):
        # Modify string values
        var_value += "_"
    elif isinstance(var_value, list):
        # Modify list type of values
        if len(var_value) > 0:
            var_value = var_value.copy()
            var_value.append(var_value[0])
    elif isinstance(var_value, dict):
        # Change values in nested dict
        new_var_value = {}
        for k, v in var_value.items():
            tmp = modify_values(v)
            assert tmp != v
            new_var_value[k] = tmp

        var_value = new_var_value
    elif isinstance(var_value, ClassyDataclass):
        # Change values in nested ClassyDataclass
        for k, v in var_value.__dict__.items():
            tmp = modify_values(v)
            assert tmp != v
            var_value.__setattr__(k, tmp)
    elif isinstance(var_value, Enum):
        # Replace enum value with another valid enum value within the same class
        valid_enum_values = var_value.__class__._member_names_
        valid_enum_values.remove(var_value.value)
        if len(valid_enum_values) > 0:
            var_value = var_value.__class__[valid_enum_values[0]]
        else:
            var_value = None
    else:
        # For types lacking implemented ways to modify them
        var_value = None

    return var_value


@pytest.mark.parametrize("json_dict, test_name", json_data_dict)
def test_copy_dataclass_method(json_dict, test_name):
    color_obj: Color = Color.from_dict(json_dict)
    color_obj_copy = color_obj.copy()

    assert color_obj == color_obj_copy, f"Copy dataclass test failed for {test_name}"


@pytest.mark.parametrize("json_dict, test_name", json_data_dict)
def test_copy_dataclass_method_deep(json_dict, test_name):
    color_obj: Color = Color.from_dict(json_dict)

    for var_name in color_obj.__dict__:
        color_obj_copy = color_obj.copy()

        var_value = color_obj_copy.__getattribute__(var_name)
        var_value = modify_values(var_value)
        if var_value is None:
            continue

        color_obj_copy.__setattr__(var_name, var_value)

        assert (
            color_obj != color_obj_copy
        ), f"Copy dataclass deep test failed for {test_name}"


@pytest.mark.parametrize("json_dict, test_name", json_data_dict)
def test_to_and_from_json(json_dict, test_name):
    color_obj: Color = Color.from_dict(json_dict)

    color_json = color_obj.to_json(indent=4)

    color_obj2 = Color.from_json(color_json)

    color_json2 = color_obj2.to_json(indent=4)

    assert (color_obj == color_obj2) or (
        not color_obj and not color_obj2
    ), f"Load and dump json {test_name} failed (1)"

    assert (color_json == color_json2) or (
        not color_json and not color_json2
    ), f"Load and dump json {test_name} failed (2)"


@pytest.mark.parametrize("json_dict, test_name", json_data_dict)
def test_reset_values(json_dict, test_name):
    color_obj: Color = Color.from_dict(json_dict)

    color_obj_default = color_obj.copy().reset_to_default_values()
    print(color_obj_default)
    for (
        field_name,
        field_obj,
    ) in color_obj_default.__class__.__dataclass_fields__.items():

        default = (
            field_obj.default_factory()
            if isinstance(field_obj.default_factory, Callable)
            else field_obj.default
        )

        assert (
            color_obj_default.__getattribute__(field_name) == default
        ), f"Test reset values {test_name} failed (1)"
