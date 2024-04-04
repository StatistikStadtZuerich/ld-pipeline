from enum import Enum
import configparser
import os
from .base import Base


class Env(str, Enum):
    test = 'test'
    int = 'int'
    prod = 'prod'


class Config(Base):

    def __init__(self, env: Env):
        super().__init__()
        self._env = env.value
        self._config = configparser.ConfigParser()
        path = os.path.join(os.path.dirname(__file__), '../../', 'config.ini')
        self._config.read(path)

    def get(self, name, return_type=str, fallback=None):
        if return_type == int:
            return self._config.getint(self._env, name, fallback=fallback)
        elif return_type == float:
            return self._config.getfloat(self._env, name, fallback=fallback)
        elif return_type == bool:
            return self._config.getboolean(self._env, name, fallback=fallback)
        return self._config.get(self._env, name, fallback=fallback)
