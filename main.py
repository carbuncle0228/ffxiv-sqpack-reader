import logging
import os

from tqdm import tqdm

from app.config import settings
from app.excel import exd_handler
from app.sqpack import SQPack
from debug import language_files, non_language_files, variant1_files, variant2_files

logging.basicConfig(
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=settings.log_level,
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)

sqpack = SQPack(settings.folder_path)


success_count = 0
fail_count = 0
for file_path in tqdm(sqpack.files.keys()):
    logging.debug("Processing file: {}".format(file_path))
    try:
        target_folder = os.path.join(
            os.path.normpath(os.path.expanduser(settings.target_path)),
            sqpack.game_version,
        )
        exd_handler.write_csv(
            sqpack=sqpack, target_folder=target_folder, file_path=file_path
        )
    except Exception as e:
        fail_count += 1
        logging.error(f"process {file_path} fail")
        logging.error(e, exc_info=True)

    success_count += 1

logging.info(f"{success_count} files exported, {fail_count} failed")

logging.debug("language_files")
logging.debug(language_files)
logging.debug("non_language_files")
logging.debug(non_language_files)
logging.debug("variant1_files")
logging.debug(variant1_files)
logging.debug("variant2_files")
logging.debug(variant2_files)
logging.debug("language_files but not in variant1")
logging.debug(language_files.difference(variant1_files))
