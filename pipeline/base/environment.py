from enum import Enum
from .services import Connection, Template
from .base import Base
import configparser


class Env(str, Enum):
    test = 'test'
    int = 'int'
    prod = 'prod'


class Config(Base):

    def __init__(self, env: Env):
        super().__init__()
        self._env = env.value
        self._config = configparser.ConfigParser()
        self._config.read('config.ini')

    def get(self, name, return_type=str, fallback=None):
        if return_type == int:
            return self._config.getint(self._env, name, fallback=fallback)
        elif return_type == float:
            return self._config.getfloat(self._env, name, fallback=fallback)
        elif return_type == bool:
            return self._config.getboolean(self._env, name, fallback=fallback)
        return self._config.get(self._env, name, fallback=fallback)


class Environment(Base):

    def __init__(self, env: Env):
        super().__init__()
        self._config = Config(env)

    def get_db_connection(self) -> Connection:
        # TODO implement
        pass

    def get_template_engine(self, template_filepath: str, output_filepath: str) -> Template:
        # TODO implement
        pass

    def get_config_value(self, name: str, return_type=str, fallback=None):
        return self._config.get(name, return_type, fallback)

