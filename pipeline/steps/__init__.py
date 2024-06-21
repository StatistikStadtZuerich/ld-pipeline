import configparser
import os

config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.ini')
config = configparser.ConfigParser()
config.read(os.path.join(config_path))

if config.getboolean('DEFAULT', 'optimized'):
    from .copy import Copy
    from .templating_optimized import TemplatingOptimized as Templating
    from .compressing import Compressing
    from .upload_to_stardog_optimized import UploadToStardogOptimized as UploadToStardog
    from .upload_to_fuseki_optimized import UploadToFusekiOptimized as UploadToFuseki
else:
    from .copy import Copy
    from .templating import Templating
    from .compressing import Compressing
    from .upload_to_stardog import UploadToStardog
    from .upload_to_fuseki import UploadToFuseki
    
from .copy_hdb_to_pipe_tables import CopyHDBToPipeTables

__all__ = [
    "Copy",
    "Templating",
    "Compressing",
    "UploadToStardog",
    "UploadToFuseki",
    "CopyHDBToPipeTables"
]
