import json
import inspect
import logging
from os.path import isfile
from typing import List, Tuple, Callable
from enum import Enum, EnumMeta
from dataclasses import asdict
from .ClassyField import classy_field
from copy import deepcopy


class ClassyDataclass:
    @classmethod
    def get_fields_with_meta_data_key(cls, metadata_key: str) -> list[str]:
        """Returns all fields' name which has a certain metadata @metadata_key

        Args:
            param_name (str): Key for the fields' metadata property dict

        Returns:
            list[str]: List of fields' name having the metadata property @metadata_key
        """
        return [
            key
            for key, value in cls.__dataclass_fields__.items()
            if metadata_key in value.metadata
        ]

    @classmethod
    def get_fields_with_valid_encoder(cls) -> list[str]:
        """Returns all fields' name which has a custom encoder function.

        Returns:
            list[str]: List of field names.
        """
        return [
            key
            for key, value in cls.__dataclass_fields__.items()
            if value.encoder is not None
        ]

    @classmethod
    def get_fields_with_valid_decoder(cls) -> list[str]:
        """Returns all fields' name which has a custom decoder function.

        Returns:
            list[str]: List of field names.
        """
        return [
            key
            for key, value in cls.__dataclass_fields__.items()
            if value.decoder is not None
        ]

    @classmethod
    def get_encoder_of_field(cls, field_name: str) -> Callable | None:
        """Returns encoder function of a field by its variable name.
        Returns None if no decoder was specified for the field or field name doesn't exists.

        Returns:
            callable: Encoder function.
        """
        return cls.__dataclass_fields__.get(field_name, classy_field()).encoder

    @classmethod
    def get_decoder_of_field(cls, field_name: str) -> Callable | None:
        """Returns decoder function of a field by its variable name.
        Returns None if no decoder was specified for the field or field name doesn't exists.

        Returns:
            callable: Decoder function.
        """
        return cls.__dataclass_fields__.get(field_name, classy_field()).decoder

    @classmethod
    def get_metadata_of_field(cls, field_name: str) -> dict:
        """Returns metadata dict of a field.

        Returns:
            callable: Metadata dict.
        """
        return cls.__dataclass_fields__.get(field_name, classy_field()).metadata

    @classmethod
    def from_json(cls, class_json_str: str):
        """Loads class from json string.

        Args:
            class_json_str (str): JSON string.

        Returns:
            _type_: Class extending ClassyDataclass.
        """
        class_dict = json.loads(class_json_str)
        return cls.from_dict(class_dict)

    @classmethod
    def from_dict(cls, class_dict: dict):
        """Loads class from python dict.

        Args:
            class_dict (dict): dict to deserialize.

        Raises:
            ValueError: If fail to deserialize.

        Returns:
            _type_: Class extending ClassyDataclass.
        """
        try:
            new_dataclass = cls(
                **{
                    k: v
                    for k, v in class_dict.items()
                    if k in inspect.signature(cls).parameters
                }
            )
        except AttributeError as e:
            raise ValueError(
                f'Could not serialize "{class_dict}" as object of type {str(cls)}'
            ) from e

        for field_name, field in cls.__dataclass_fields__.items():
            if field_name in class_dict:
                field_value = cls._deserialize_field(
                    class_dict[field_name], field_name, field.type
                )
                setattr(new_dataclass, field_name, field_value)

        return new_dataclass

    @classmethod
    def _deserialize_field(cls, value, field_name: str, field_type: type):
        """Deserializes a field in data class.

        Args:
            value (Any): Value of the field to deserialize.
            field_name (str): Name of the field to deserialize.
            field_type (type): Type of the field to deserialize.

        Returns:
            _type_: deserialized field.
        """
        fields_with_specified_decoder = cls.get_fields_with_valid_decoder()
        field_value = None

        if field_name in fields_with_specified_decoder:
            decoder_func = cls.get_decoder_of_field(field_name)
            field_value = decoder_func(value)
        elif isinstance(field_type, (EnumMeta, Enum)):
            try:
                field_value = field_type[value]
            except KeyError:
                logging.warning(
                    f"Could not properly deserialize {field_name}<{field_type}> of value {value}"
                )
                field_value = value
        elif isinstance(value, (list, tuple, List, Tuple)):
            field_value = []
            for val in value:
                v = cls._deserialize_field(val, "list_item", field_type.__args__[0])
                field_value.append(v)

        elif inspect.isclass(field_type) and issubclass(field_type, ClassyDataclass):
            field_value = field_type.from_dict(value)
        else:
            field_value = value

        return field_value

    @classmethod
    def load_from_json(cls, path: str, encoding="UTF-8"):
        """Loads from json file given path.

        Args:
            path (str): path to json file.

        Raises:
            FileNotFoundError: If json file not found under specified @path.

        Returns:
            _type_: Class extending ClassyDataclass.
        """
        if not isfile(path):
            raise FileNotFoundError("No file exists under specified path to load json.")

        with open(path, "r", encoding=encoding) as f:
            json_str = json.loads(f.read())
            f.close()
        new_dataclass = cls.from_dict(json_str)
        return new_dataclass

    def to_dict(self, serialize_fields=True) -> dict:
        """Serializes dataclass to python dictionary.

        Args:
            serialize_fields (bool, optional): To also serialize all fields in dataclass. Defaults to True.

        Returns:
            dict: Dict representation of dataclass.
        """
        if serialize_fields:
            class_dict = self._serialize_to_dict()
        else:
            class_dict = asdict(self)
        return class_dict

    def _serialize_to_dict(self) -> dict:
        """Serializes dataclass to python dictionary and all fields in dictionary.

        Returns:
            dict: Dict representation of dataclass.
        """
        class_dict = asdict(self)
        for field_name, field in self.__dataclass_fields__.items():
            if field_name in class_dict:
                field_value = self._serialize_field(
                    getattr(self, field_name), field_name, field.type
                )
                if field_value is not None:
                    class_dict[field_name] = field_value
        return class_dict

    @classmethod
    def _serialize_field(cls, value, field_name: str, field_type: type):
        """Serializes a field in data class.

        Args:
            value (Any): Value of the field to serialize.
            field_name (str): Name of the field to serialize.
            field_type (type): Type of the field to serialize.

        Returns:
            _type_: Serialized field.
        """
        fields_with_specified_encoder = cls.get_fields_with_valid_encoder()
        field_value = None
        if field_name in fields_with_specified_encoder:
            encoder_func = cls.get_encoder_of_field(field_name)
            field_value = encoder_func(value)
        elif isinstance(value, (EnumMeta, Enum)):
            field_value = value._name_
        elif isinstance(value, (list, tuple, List, Tuple)):
            field_value = []
            for val in value:
                field_value.append(
                    cls._serialize_field(val, "list_item", field_type.__args__[0])
                )

        elif not cls.__is_var_primitive(value) and isinstance(value, ClassyDataclass):
            field_value = value.to_dict(serialize_fields=True)
        elif cls.__is_var_primitive(value):
            field_value = value
        else:
            logging.warning(f"Could not serialize {field_name}")

        return field_value

    def to_json(self, indent: int | None = None) -> str:
        """Dumps json string representation of dataclass with all fields serialized.

        Args:
            indent (int | None, optional): Indent to use in JSON string. Defaults to None.

        Returns:
            str: JSON string.
        """
        return json.dumps(self.to_dict(serialize_fields=True), indent=indent)

    @staticmethod
    def __is_var_primitive(var) -> bool:
        """Checks if a variable is of primitive type.

        Args:
            var (_type_): Variable to validate.

        Returns:
            bool: True if @var is primitive, else, False.
        """
        return not hasattr(var, "__dict__")

    def reset_to_default_values(self):
        """Resets dataclass to its default values and returns itself.

        Returns:
            _type_: Dataclass with default values.
        """
        for field_name, field_obj in self.__class__.__dataclass_fields__.items():
            if isinstance(field_obj.default_factory, Callable):
                setattr(self, field_name, field_obj.default_factory())
            else:
                setattr(self, field_name, field_obj.default)
        return self

    def copy(self):
        return deepcopy(self)

    @classmethod
    def __is_var_static(cls, name: str) -> bool:
        """Checks if variable by @name is static or not.

        Args:
            name (str): Name of variable to validate.

        Returns:
            bool: True if var is static.
        """
        return cls.__dataclass_fields__.get(name, classy_field()).is_static or False

    def __setattr__(self, name: str, value):
        """Overrides base implementation to handle static variables' values.

        Args:
            name (str): Name of variable to set value to.
            value (_type_): New value to set.
        """
        if self.__is_var_static(name):
            cls = type(self)
            setattr(cls, name, value)
        else:
            super().__setattr__(name, value)
