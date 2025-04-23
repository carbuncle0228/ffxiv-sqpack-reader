import glob
import logging
import os

import orjson

from app.excel.definition.sheet import SheetDefinition


class RelationDefinition:
    sheet_definitions: list[SheetDefinition] = []
    sheet_map: dict[str, SheetDefinition] = {}

    def __init__(self):
        for file_path in glob.glob(os.path.normpath("./Definitions/*.json")):
            with open(file_path, "r", encoding="utf-8") as file:
                def_json = file.read()
                try:
                    obj = orjson.loads(def_json)
                    self.sheet_definitions.append(SheetDefinition.from_json(obj))
                except orjson.JSONDecodeError as e:
                    logging.error(e, exc_info=True)
        self.compile()

    def compile(self):
        """
        _SheetMap = _SheetDefinitions.ToDictionary(_ => _.Name, _ => _);

           foreach (var sheet in SheetDefinitions)
               sheet.Compile();

        """
        self.sheet_map = {
            definition.name: definition for definition in self.sheet_definitions
        }
        for sheet_definition in self.sheet_definitions:
            sheet_definition.compile()
