from abc import ABC, abstractmethod
from typing import List


class IDataDefinition(ABC):
    @property
    @abstractmethod
    def length(self) -> int:
        pass

    @abstractmethod
    def get_name(self, index: int) -> str:
        pass

    @abstractmethod
    def clone(self) -> "IDataDefinition":
        pass


class DataDefinitionSerializer:
    @staticmethod
    def from_json(obj: dict) -> IDataDefinition:
        type_ = obj.get("type")
        if type_ is None:
            return SingleDataDefinition.from_json(obj)
        elif type_ == "group":
            return GroupDataDefinition.from_json(obj)
        elif type_ == "repeat":
            return RepeatDataDefinition.from_json(obj)
        else:
            raise ValueError("Invalid definition type.")


class SingleDataDefinition(IDataDefinition):
    def __init__(self, name: str = None):
        self.name = name

    @property
    def length(self) -> int:
        return 1

    def clone(self) -> "SingleDataDefinition":
        return SingleDataDefinition(self.name)

    def get_name(self, index: int) -> str:
        if index != 0:
            raise IndexError("index")
        return self.name

    @staticmethod
    def from_json(obj: dict) -> "SingleDataDefinition":
        return SingleDataDefinition(obj.get("name"))


class GroupDataDefinition(IDataDefinition):
    def __init__(self, members: List[IDataDefinition] = None):
        self.members = members if members else []
        self.length = sum(member.length for member in self.members)

    @property
    def length(self) -> int:
        return self._length

    @length.setter
    def length(self, value: int):
        self._length = value

    def clone(self) -> "GroupDataDefinition":
        return GroupDataDefinition([member.clone() for member in self.members])

    def get_name(self, index: int) -> str:
        if index < 0 or index >= self.length:
            raise IndexError("index")
        pos = 0
        for member in self.members:
            new_pos = pos + member.length
            if new_pos > index:
                inner_index = index - pos
                return member.get_name(inner_index)
            pos = new_pos
        return None

    @staticmethod
    def from_json(obj: dict) -> "GroupDataDefinition":
        members = [
            DataDefinitionSerializer.from_json(m) for m in obj.get("members", [])
        ]
        return GroupDataDefinition(members)


class RepeatDataDefinition(IDataDefinition):
    def __init__(
        self,
        naming_offset: int = 0,
        repeat_count: int = 0,
        repeated_definition: IDataDefinition = None,
    ):
        self.naming_offset = naming_offset
        self.repeat_count = repeat_count
        self.repeated_definition = repeated_definition

    @property
    def length(self) -> int:
        return self.repeat_count * (
            self.repeated_definition.length if self.repeated_definition else 0
        )

    def clone(self) -> "RepeatDataDefinition":
        return RepeatDataDefinition(
            self.naming_offset, self.repeat_count, self.repeated_definition.clone()
        )

    def get_name(self, index: int) -> str:
        if index < 0 or index >= self.length:
            raise IndexError("index")
        repeat_nr = index // self.repeated_definition.length
        inner_index = index % self.repeated_definition.length
        base_name = self.repeated_definition.get_name(inner_index)
        return f"{base_name}[{repeat_nr + self.naming_offset}]"

    @staticmethod
    def from_json(obj: dict) -> "RepeatDataDefinition":
        repeat_count = obj.get("count", 0)
        repeated_definition = DataDefinitionSerializer.from_json(obj.get("definition"))
        return RepeatDataDefinition(0, repeat_count, repeated_definition)


class PositionedDataDefinition:
    def __init__(self):
        self.inner_definition: IDataDefinition = None
        self.index = 0

    @property
    def length(self):
        return self.inner_definition.length if self.inner_definition else 0

    def clone(self):
        clone = PositionedDataDefinition()
        clone.index = self.index
        clone.inner_definition = self.inner_definition.clone()
        return clone

    def get_name(self, index: int):
        inner_index = index - self.index
        if inner_index < 0 or inner_index >= self.length:
            raise IndexError("index out of range")
        return self.inner_definition.get_name(inner_index)

    @staticmethod
    def from_json(obj):
        definition = PositionedDataDefinition()
        definition.index = obj.get("index", 0)
        definition.inner_definition = DataDefinitionSerializer.from_json(obj)
        return definition
