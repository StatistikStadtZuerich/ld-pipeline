from .base import Base
from .config import Env, Config
from .environment import Environment
from .services import JinjaTemplateEngine, CompressionEngine
from .step import Step, StepDefinition
from .utils import Utils
from extended_configparser.interpolator import EnvInterpolation
import configparser
import os

os.environ.setdefault("SSZ_DB_TYPE", "mssql")
config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.ini")
config = configparser.ConfigParser(interpolation=EnvInterpolation())
config.read(os.path.join(config_path))

db = config.get("DEFAULT", "db")
if db == "mssql":
    from .mmsql_environment import MMSqlEnvironment as Environment
else:
    from .environment import Environment


__all__ = [
    "Base",
    "Env",
    "Config",
    "Environment",
    "JinjaTemplateEngine",
    "CompressionEngine",
    "Step",
    "StepDefinition",
    "Utils",
]
