from configparser import ConfigParser
from extended_configparser.interpolator import EnvInterpolation
from enum import Enum
import os

from .base import Base


class Env(str, Enum):
    test = "test"
    local = "local"
    int = "int"
    prod = "prod"


class Config(Base):
    def __init__(self, env: Env, config_files: list[os.PathLike] = None):
        super().__init__()
        self._env = env.value
        self._config_parser = ConfigParser(interpolation=EnvInterpolation())
        if config_files:
            loaded = self._config_parser.read(config_files)
            if not loaded:
                self.logger.error("No config file loaded!")

    def get(self, name, return_type=str, fallback=None):
        if return_type is int:
            return self._config_parser.getint(self._env, name, fallback=fallback)
        elif return_type is float:
            return self._config_parser.getfloat(self._env, name, fallback=fallback)
        elif return_type is bool:
            return self._config_parser.getboolean(self._env, name, fallback=fallback)
        return self._config_parser.get(self._env, name, fallback=fallback)
