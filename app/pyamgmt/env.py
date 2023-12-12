"""Helper functions for working with environment variables."""
import dataclasses
import os
import typing

TRUE = ('TRUE', 'True', 'true', '1')
FALSE = ('FALSE', 'False', 'false', '0')


def resolve_boolean(value: str) -> bool | None:
    if value.lower() in FALSE:
        return False
    if value.lower() in TRUE:
        return True


@dataclasses.dataclass
class EnvVar:
    key: str
    callback: typing.Callable = str
    value: typing.Any = None
    default: typing.Any = None

    def __post_init__(self):
        self.value = os.getenv(self.key, None)

    def resolve(self):
        if not self.value:
            if self.default is not None:
                return self.default
            else:
                return None
        return self.callback(self.value)


DEBUG = EnvVar('DEBUG', resolve_boolean, default=False)

ARANGO_HOST = EnvVar('ARANGO_HOST')
ARANGO_PORT = EnvVar('ARANGO_PORT')
DATABASE_HOST = EnvVar('DATABASE_HOST')
DATABASE_PASSWORD = EnvVar('DATABASE_PASSWORD')
DATABASE_PORT = EnvVar('DATABASE_PORT')

VITE_CLIENT_URL = EnvVar('VITE_CLIENT_URL')
ASSET_URL = EnvVar('ASSET_URL')

for setting in dir():
    if setting.isupper():
        obj = globals()[setting]
        if hasattr(obj, 'resolve'):
            globals()[setting] = obj.resolve()
