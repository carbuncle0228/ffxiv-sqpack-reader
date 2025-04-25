import csv
import logging
import os
from pathlib import Path

from app.config import settings
from app.se_string.evaluator import evaluated_se_string

process_count = 0
failure_count = 0
for file_path in Path(settings.evaluate_folder_path).rglob("*"):
    if file_path.is_file():
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            relative_path = file_path.relative_to(
                settings.evaluate_folder_path
            )  # Get relative path
            reader = csv.reader(csvfile, delimiter=",")  # Creates a CSV reader obj
            target_file_path = settings.evaluate_target_path + str(relative_path)
            os.makedirs(os.path.dirname(target_file_path), exist_ok=True)
            with open(
                target_file_path, "w", buffering=1024 * 1024 * 8, encoding="utf-8"
            ) as file:
                writer = csv.writer(file, delimiter=",")
                for i, row in enumerate(reader):
                    if i < 4:
                        writer.writerow(row)
                        continue
                    try:
                        new_row: list[str] = []
                        for column in row:
                            if "macro(" in column:
                                new_row.append(evaluated_se_string(column))
                            else:
                                new_row.append(column)
                        writer.writerow(new_row)
                    except Exception as e:
                        logging.error(
                            f"evaluate failed in f{file_path}:Key:{row[0]}: {e}",
                            exc_info=True,
                        )
                        failure_count += 1
                        break
                process_count += 1

logging.error(f"{process_count} files exported, {failure_count} failed")
