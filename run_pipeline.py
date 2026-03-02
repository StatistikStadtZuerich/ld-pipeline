import datetime
import logging
import logging.config
from argparse import ArgumentParser
from pathlib import Path

import main
from pipeline import Pipeline
from pipeline.base import Utils, Env, Environment


def run_pipeline(env: Environment):
    utils = Utils()

    # Check if start signal has arrived
    if utils.check_start_signal(env):
        logging.info("Starting Pipeline for %s", env.name)
    else:
        logging.debug(
            "Start-Signal for pipeline not found in '%s'",
            utils.start_signal_folder(env),
        )
        return

    options_batching = {
        "db_batch_size": 100000,
        "write_batch_size": 600000,
        "max_iteration": None,
    }
    step_definitions = main.get_step_definitions(env, options_batching)
    pipeline = Pipeline(env, step_definitions)

    # Update pipe tables
    pipeline.execute("initPipeTables")
    pipeline.execute("copyHDBToPipeTables")
    pipeline.execute("createViewsFromSQL")

    # Generate triple files
    generate_triple_files(pipeline=pipeline)

    # Create start signal to generate the Fuseki index
    logging.info("Create start signal to generate the Fuseki index")
    utils.set_start_signal_fuseki_index(env)

    # Write back the publication status to the HDB
    logging.info("Write back the publication status to the HDB")
    pipeline.execute("writePublicationStatiToHDB")

    # Set finish signal
    logging.debug("Set Finish-Signal for pipeline")
    utils.set_finish_signal(env)
    logging.info("Pipeline is finished.")


def generate_triple_files(pipeline: Pipeline):
    triple_types_metadata = [
        "code",
        "cube",
        "groupCode",
        "hierarchy",
        "measureUnit",
        "measure",
        "property",
        "room",
        "time",
    ]
    triple_types_observations = ["observation"]
    triple_types_others = ["copyStatic", "buildTermsetHierarchy", "generateViews"]

    for name in triple_types_metadata:
        pipeline.execute(f"{name}Templating")
    for name in triple_types_observations:
        pipeline.execute(f"{name}Templating")
    for name in triple_types_others:
        pipeline.execute(name)


def configure_logging(env: Environment):
    loggers = []
    if env.config.get("log.stdout", bool, True):
        loggers.append("console")
    if env.config.get("log.file", bool, False):
        loggers.append("file")

    logger_config = {
        "version": 1,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": datetime.datetime.now().strftime(
                    env.config.get("log.file.name", fallback="output.log")
                ),
                "when": "MIDNIGHT",
                "interval": 1,
                "backupCount": 14,
                "formatter": "default",
            },
        },
        "formatters": {
            "default": {
                "class": "logging.Formatter",
                "format": env.config.get(
                    "log.format",
                    return_type=str,
                    fallback="%(asctime)s [%(env)s] - %(name)s - %(levelname)s - %(message)s",
                ),
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "defaults": {"env": env.name},
            }
        },
        "root": {
            "handlers": loggers,
            "level": env.config.get("log.level", str, logging.DEBUG),
        },
    }

    logging.config.dictConfig(logger_config)
    logging.debug("Logging configured")


if __name__ == "__main__":
    __parser = ArgumentParser(description="The LD Pipeline")
    __parser.add_argument(
        "-e",
        "--env",
        help="environment name",
        choices=[e.name for e in Env],
        default=Env.test,
    )
    __parser.add_argument(
        "-c",
        "--config",
        action="append",
        help="config file (config.ini)",
        type=lambda p: Path(p).absolute(),
        default=["config.ini"],
    )
    __args = __parser.parse_args()
    __config = Environment(Env(__args.env), __args.config)

    configure_logging(__config)
    try:
        run_pipeline(__config)
    except Exception as e:
        logging.fatal("Unexpected Error while running pipeline", exc_info=e)
        exit(1)
