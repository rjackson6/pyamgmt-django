"""Helper functions for working with environment variables."""
import dataclasses
import os
from pathlib import Path
import typing

TRUE = ('TRUE', 'True', 'true', '1')
FALSE = ('FALSE', 'False', 'false', '0')
NONE = ('NULL', 'null',)

BASE_DIR = Path(__file__).resolve().parent.parent


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
        if self.value in NONE:
            return None
        return self.callback(self.value)


DEBUG = EnvVar('DEBUG', resolve_boolean, default=False)

SECRET_KEY = EnvVar('SECRET_KEY')
if not SECRET_KEY.value:
    with open(BASE_DIR.parent / 'etc' / 'secret-key.txt') as f:
        SECRET_KEY = f.read().strip()

ARANGO_HOST = EnvVar('ARANGO_HOST')
ARANGO_PORT = EnvVar('ARANGO_PORT')
ASSET_HOST = EnvVar('ASSET_HOST')
ASSET_PORT = EnvVar('ASSET_PORT')
ASSET_URL = EnvVar('ASSET_URL')
DATABASE_HOST = EnvVar('DATABASE_HOST')
DATABASE_NAME = EnvVar('DATABASE_NAME')

DATABASE_PASSWORD = EnvVar('DATABASE_PASSWORD')
if not DATABASE_PASSWORD.value:
    with open(BASE_DIR.parent / 'etc' / 'postgres-password.txt', 'r') as f:
        DATABASE_PASSWORD = f.read().strip()

DATABASE_PORT = EnvVar('DATABASE_PORT')
DATABASE_USER = EnvVar('DATABASE_USER')
REDIS_HOST = EnvVar('REDIS_HOST')
REDIS_PORT = EnvVar('REDIS_PORT')
SECURE_CROSS_ORIGIN_OPENER_POLICY = EnvVar('SECURE_CROSS_ORIGIN_OPENER_POLICY')
VITE_CLIENT_URL = EnvVar(
    'VITE_CLIENT_URL',
    default='http://localhost:1234/assets/@vite/client'
)

for setting in dir():
    if setting.isupper():
        obj = globals()[setting]
        if hasattr(obj, 'resolve'):
            globals()[setting] = obj.resolve()
