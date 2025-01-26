from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import DirectoryPath, field_validator, BaseModel

BASE_DIR = Path(__file__).resolve().parent


class TextToCsvConfig(BaseModel):
    DATASET_PATH: DirectoryPath
    SPLIT_CHARACTERS: int = 12500

    @field_validator("DATASET_PATH")
    def check_path_exists(cls, v: Path) -> Path:
        if not v.exists():
            raise ValueError(f"Path {v} does not exist")
        return v


class Settings(BaseSettings):
    """Configuration for the application. Values can be set via environment variables.

    Pydantic will automatically handle mapping uppercased environment variables to the corresponding fields.
    To populate nested, the environment should be prefixed with the nested field name and an underscore.
    """  # noqa: E501

    model_config = SettingsConfigDict(env_nested_delimiter="__", env_file=BASE_DIR / ".env")

    text_to_csv: TextToCsvConfig


settings = Settings()
