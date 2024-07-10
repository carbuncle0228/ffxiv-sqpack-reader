from typing import Optional

from app.excel.definition.data import PositionedDataDefinition


class SheetDefinition:
    column_definition_map: dict[int, PositionedDataDefinition] = {}
    column_index_to_name_map: dict[int, str] = {}
    column_name_to_index_map: dict[str, int] = {}

    data_definitions: list[PositionedDataDefinition] = []
    default_column_index: Optional[int] = None
    name: str = ""
    default_column: str = ""
    is_generic_reference_target: bool = False

    def __init__(self):
        pass

    def compile(self):
        self.column_definition_map = {}
        self.column_name_to_index_map = {}
        self.column_index_to_name_map = {}

        self.data_definitions = sorted(self.data_definitions, key=lambda d: d.index)

        for defn in self.data_definitions:
            for i in range(defn.length):
                offset = defn.index + i
                self.column_definition_map[offset] = defn
                name = defn.get_name(offset)
                self.column_name_to_index_map[name] = offset
                self.column_index_to_name_map[offset] = name

        if self.default_column:
            self.default_column_index = self.column_name_to_index_map.get(
                self.default_column
            )
        else:
            self.default_column_index = None

    def try_get_definition(self, index: int):
        return self.column_definition_map.get(index)

    def get_default_column_index(self):
        return self.default_column_index

    def find_column(self, column_name: str):
        return self.column_name_to_index_map.get(column_name)

    def get_all_column_names(self):
        return list(self.column_name_to_index_map.keys())

    def get_column_name(self, index: int):
        return self.column_index_to_name_map.get(index)

    @staticmethod
    def from_json(obj):
        sheet_def = SheetDefinition()
        sheet_def.name = obj.get("sheet", "")
        sheet_def.default_column = obj.get("defaultColumn", "")
        sheet_def.is_generic_reference_target = obj.get(
            "isGenericReferenceTarget", False
        )
        sheet_def.data_definitions = [
            PositionedDataDefinition.from_json(j) for j in obj["definitions"]
        ]

        return sheet_def

    def __str__(self):
        return self.name
