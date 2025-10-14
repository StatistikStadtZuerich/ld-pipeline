import logging
import pathlib

from pipeline.base import Environment, Env
from run_pipeline import run_pipeline, configure_logging

if __name__ == "__main__":
    __env = Environment(
        Env.int,
        [
            pathlib.Path("./config.ini"),
            pathlib.Path("./int.ini"),
            pathlib.Path("./config-int.ini"),
        ],
    )

    configure_logging(__env)
    logging.error("Deprecated start-script, use 'run_pipeline.py' instead!")
    run_pipeline(__env)
