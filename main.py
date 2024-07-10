import logging
import os

from app.sqpack import SQPack
from app.config import settings

from app.excel import exd_handler

logging.getLogger().setLevel(settings.log_level)
sqpack = SQPack(settings.folder_path)


success_count = 0
fail_count = 0
for file_path in sqpack.files.keys():
    logging.debug("Processing file: {}".format(file_path))

    target_folder = os.path.join(
        os.path.normpath(os.path.expanduser(settings.target_path)),
        sqpack.game_version,
    )
    exd_handler.write_csv(
        sqpack=sqpack, target_folder=target_folder, file_path=file_path
    )

    success_count += 1

logging.info(f"{success_count} files exported, {fail_count} failed")
