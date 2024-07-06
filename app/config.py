import os
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    folder_path: str = "~/project/ff14/FINAL FANTASY XIV - A Realm Reborn"
    target_path: str = "./output"
    language: Literal[
        "Japanese",
        "English",
        "German",
        "French",
        "ChineseSimplified",
        "ChineseTraditional",
        "Korean",
    ] = "English"

    log_level: str = "DEBUG"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=f"./config/{os.environ.get('ENV','')}.env",
    )


settings = Settings()
