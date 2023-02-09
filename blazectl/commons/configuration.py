import enum
from abc import ABC
from typing import Any, ClassVar

import typer
from pydantic import BaseModel


class ConfigStoreKind(str, enum.Enum):
    LOCAL = "local"
    DB = "db"


class Configuration(BaseModel, ABC):
    kind: ConfigStoreKind

    registry: ClassVar[dict] = {}

    @classmethod
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        name = cls.__fields__['kind'].default
        if name is None:
            print(f"ERROR: Default value of 'kind' shall be set for Configuration class:{cls}")
            raise typer.Abort()

        Configuration.registry[name] = cls


class DBConfiguration(Configuration):
    kind: ConfigStoreKind = ConfigStoreKind.DB
    host: str
    port: int
    user: str
    password: str
    database: str


class LocalConfiguration(Configuration):
    kind: ConfigStoreKind = ConfigStoreKind.LOCAL


def get_instance(config: dict) -> Configuration:
    target_name = config['kind']
    for name, subclass in Configuration.registry.items():
        if target_name == name:
            return subclass(**config)

    print(f"ERROR: Didn't find appropriate instance of Configuration class for config: {config}")
    raise typer.Abort()
