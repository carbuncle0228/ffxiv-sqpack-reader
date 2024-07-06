import logging
import os

from app import exd_handler
from app.config import settings
from app.sqpack import SQPack

logging.getLogger().setLevel(settings.log_level)

sqpack = SQPack(settings.folder_path)

success_count = 0
fail_count = 0


for file_name in sqpack.files.keys():
    logging.debug("Processing file: {}".format(file_name))

    target_folder = os.path.join(
        os.path.normpath(os.path.expanduser(settings.target_path)),
        sqpack.game_version,
    )
    exd_handler.write_csv(target_folder=target_folder, file_name=file_name)

    success_count += 1

print(f"{success_count} files exported, {fail_count} failed")
