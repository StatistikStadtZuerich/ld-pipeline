import datetime
import logging
import logging.config
import pathlib
import sys
from argparse import ArgumentParser

import main
from pipeline import Pipeline
from pipeline.base import Env, Environment, Utils, derive_reference_number


def run_pipeline(
    env: Environment,
    target_env: str | None = None,
    embargo: bool = False,
    view_ids: list[str] | None = None,
):
    utils = Utils()
    logger = logging.getLogger("run_pipeline")

    options_batching = {
        "db_batch_size": 100000,
        "write_batch_size": 600000,
        "max_iteration": None,
    }
    step_definitions = main.get_step_definitions(env, options_batching)
    pipeline = Pipeline(env, step_definitions)

    # Update pipe tables
    pipeline.execute("initPipeTables")
    # pipeline.execute("copyHDBToPipeTables")
    pipeline.execute("createViewsFromSQL")

    # Generate triple files
    generate_triple_files(pipeline=pipeline)

    # Optional: nach Referenznummer/view gefilterte Auswahl (veröffentlicht
    # und/oder embargoed) kann zusätzlich generiert werden (manuell per Flag).
    if view_ids:
        _generate_locked_output(env, options_batching, embargo, view_ids)

    # Create the start signal to generate the Fuseki index
    logger.info("Create start signal to generate the Fuseki index")
    utils.set_start_signal_fuseki_index(env, target_env)

    # Write back the publication status to the HDB
    logger.info("Write back the publication status to the HDB")
    pipeline.execute("writePublicationStatiToHDB")

    logger.info("Pipeline is finished.")


def run_fast_views(
    env: Environment, embargo: bool = False, view_ids: list[str] | None = None
):
    """Fast-View: generiert nur die LD-View-TTLs (ein ttl.gz je View), ohne initPipeTables, 
    Fuseki-Index-Neuaufbau, Rückschreiben in HDB. Hier können nach Referenznummer/view id gefilterte 
    Daten generiert und in template_output_path/locked gespeichert werden."""
    options = {}
    step_definitions = main.get_step_definitions(env, options)
    pipeline = Pipeline(env, step_definitions)

    # DB-Views aktualisieren, damit die view_vb_* aktuell sind.
    pipeline.execute("createViewsFromSQL")

    # Nur die LD-Views erzeugen -> <env>_ldview_<ts>_<uuid>.ttl.gz
    pipeline.execute("generateViews")

    if view_ids:
        _generate_locked_output(env, options, embargo, view_ids)

    logging.getLogger("run_pipeline").info("Fast-View run finished.")


def _generate_locked_output(
    env: Environment,
    options: dict,
    embargo: bool,
    view_ids: list[str],
):
    """
    Generiert eine nach Referenznummer/view id gefilterte Auswahl (Views + Observations) 
    nach template_output_path/locked (kein öffentlicher Fuseki-Index-Zugriff).
    - embargo=False: veröffentlichte Observations für die selektierten Views
    - embargo=True: embargoed Observations für die selektierten Views (nur für interne Nutzung, nicht öffentlich)
    """
    logger = logging.getLogger("run_pipeline")
    view_ids = set(view_ids)
    reference_numbers = {derive_reference_number(v) for v in view_ids}
    locked_defs = main.get_step_definitions(
        env,
        {**options, "view_ids": view_ids, "reference_numbers": reference_numbers},
    )
    locked_pipeline = Pipeline(env, locked_defs)
    logger.info(
        "Generating Fast-View selection into locked output: %s", sorted(view_ids)
    )
    locked_pipeline.execute("generateViews")
    if embargo:
        locked_pipeline.execute("observationFastViewEmbargoedTemplating")
    else:
        locked_pipeline.execute("observationFastViewPublicTemplating")


def generate_triple_files(pipeline: Pipeline):
    triple_types_metadata = [
        "code",
        "cube",
        "groupCode",
        "groupTermset",
        "hierarchy",
        "measureUnit",
        "measure",
        "property",
        "room",
        "time",
        "timeRelation",
        "timeTermset",
        "dimensionTermset",
    ]
    triple_types_observations = ["observation"]
    triple_types_others = [
        "copyStatic",
        "buildInfo",
        "buildTermsetHierarchy",
        "generateViews",
    ]

    for name in triple_types_metadata:
        pipeline.execute(f"{name}Templating")
    for name in triple_types_observations:
        pipeline.execute(f"{name}Templating")
    for name in triple_types_others:
        pipeline.execute(name)


def configure_logging(
    env: Environment, log_file_name: pathlib.Path = pathlib.Path("./pipeline.log")
):
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
                "class": "logging.handlers.RotatingFileHandler",
                "filename": log_file_name.absolute(),
                "maxBytes": 10 * 1024 * 1024,  # 10 MB
                "backupCount": 5,
                "encoding": "utf-8",
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
    logging.getLogger("logging").debug("Logging configured")


if __name__ == "__main__":
    __parser = ArgumentParser(description="The LD Pipeline")
    __parser.add_argument(
        "-e",
        "--env",
        help="environment name",
        choices=[e.name for e in Env],
        default=Env.test,
        type=Env,
    )
    __parser.add_argument(
        "-t",
        "--targetEnv",
        help="target environment for the fuseki-index",
        choices=[e.name for e in Env],
        default=None,
        type=Env,
    )
    __parser.add_argument(
        "-r",
        "--runId",
        help="the unique run id (for logging)",
        default=datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S"),
    )
    __parser.add_argument(
        "-c",
        "--config",
        action="append",
        help="config file (config.ini)",
        type=lambda p: pathlib.Path(p).absolute(),
        default=["config.ini"],
    )
    __parser.add_argument(
        "--fast-views",
        help="Fast-View-Modus: nur DB-Views/LD-Views aktualisieren, ohne "
        "initPipeTables, kompletten Fuseki-Index-Neubau oder Rückschreiben",
        action="store_true",
    )
    __parser.add_argument(
        "--embargo",
        help="Observations mit Sperrfrist statt veröffentlichte Observations für ausgewählte "
        "Views generieren (erfordert --referenznummern)",
        action="store_true",
    )
    __parser.add_argument(
        "--referenznummern",
        help="Kommagetrennte View-Id (z.B. BEV411OD411A) zur Auswahl der View",
        default=None,
    )
    __args = __parser.parse_args()
    __view_ids = (
        [v.strip() for v in __args.referenznummern.split(",") if v.strip()]
        if __args.referenznummern
        else None
    )
    if __args.embargo and not __view_ids:
        __parser.error("--embargo erfordert --referenznummern")
    __config = Environment(__args.env, __args.config, __args.runId)

    # Determine log-target
    _log_dir_name = __config.config.get("log.dir", str, None)
    _log_fallback = False
    if _log_dir_name is not None:
        _log_dir = pathlib.Path(_log_dir_name)
    else:
        __log_file_name: pathlib.Path = __config.config.get("log.file.name", str, None)
        if __log_file_name is not None:
            _log_fallback = True
            __log_file = pathlib.Path(__log_file_name)
            if __log_file.is_dir():
                _log_dir = __log_file
            elif __log_file.parent.is_dir():
                _log_dir = __log_file.parent
            else:
                _log_dir = pathlib.Path(".")
        else:
            _log_dir = pathlib.Path(".")

    __log_file = _log_dir / f"pipeline_{__config.name}_{__args.runId}.log"

    configure_logging(__config, __log_file)
    logger = logging.getLogger("main")
    if _log_fallback:
        logger.warning(
            "No log.dir configured, falling back to log.file.name's directory"
        )

    try:
        logger.info("Starting pipeline with runId %s", __args.runId)
        if __args.fast_views:
            run_fast_views(__config, embargo=__args.embargo, view_ids=__view_ids)
        else:
            run_pipeline(
                __config,
                (__args.targetEnv or __args.env),
                embargo=__args.embargo,
                view_ids=__view_ids,
            )
    except Exception as e:
        logger.exception("Unexpected Error while running pipeline", exc_info=e)
        sys.exit(1)
