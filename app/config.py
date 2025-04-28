import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    folder_path: str = (
        r"C:\Program Files (x86)\SquareEnix\FINAL FANTASY XIV - A Realm Reborn"
    )
    target_path: str = "./resources/output"

    evaluate_folder_path: str = "./resources/output/2025.04.16.0000.0000"
    evaluate_target_path: str = "./resources/evaluate_output/"
    language: Literal[
        "Japanese",
        "English",
        "German",
        "French",
        "ChineseSimplified",
        "ChineseTraditional",
        "Korean",
    ] = "English"

    ONLY_STR_MODE: bool = True

    HEX_STR_MODE: bool = True

    log_level: str = "DEBUG"

    DEBUG_SKIP: bool = False
    SKIP_ERROR: bool = False

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=f"./config/{os.environ.get('ENV', '')}.env",
    )


settings = Settings()
