import datetime
import logging
import pathlib
import sys
from argparse import ArgumentParser

import main
from pipeline import Pipeline
from pipeline.base import Env, Environment
from run_pipeline import configure_logging


def generate_fast_view(env: Environment, view_ids: set[str]):
    """Generiert eine nach view-id gefilterte LD-View nach template_output_path/locked.
    Läuft ohne initPipeTables, ohne öffentlichen Fuseki-Index-Neubau und ohne
    Rückschreiben des Publikationsstatus in die HDB."""
    logger = logging.getLogger("run_fast_view")

    options = {"view_ids": view_ids}
    step_definitions = main.get_step_definitions(env, options)
    pipeline = Pipeline(env, step_definitions)

    logger.info("Generating fast view for view id(s) %s", sorted(view_ids))

    # DB-Views aktualisieren, damit die view_vb_* aktuell sind.
    pipeline.execute("createViewsFromSQL")

    # Nur die ausgewählte(n) LD-View(s) erzeugen -> template_output_path/locked
    pipeline.execute("generateViews")

    logger.info("Fast view run finished.")


if __name__ == "__main__":
    __parser = ArgumentParser(
        description="Generates a single LD-view into the locked output folder, "
        "without running the full pipeline."
    )
    __parser.add_argument(
        "-e",
        "--env",
        help="environment name",
        choices=[e.name for e in Env],
        default=Env.test,
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
        "--view-ids",
        required=True,
        help="Kommagetrennte volle View-Id(s) (z.B. BEV411OD411A,WIR400OD100B) "
        "zur Auswahl der zu generierenden View(s)",
    )
    __args = __parser.parse_args()
    __view_ids = {v.strip() for v in __args.view_ids.split(",") if v.strip()}
    if not __view_ids:
        __parser.error("--view-ids darf nicht leer sein")

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

    __log_file = _log_dir / f"fast_view_{__config.name}_{__args.runId}.log"

    configure_logging(__config, __log_file)
    logger = logging.getLogger("main")
    if _log_fallback:
        logger.warning(
            "No log.dir configured, falling back to log.file.name's directory"
        )

    try:
        logger.info("Starting fast view run with runId %s", __args.runId)
        generate_fast_view(__config, __view_ids)
    except Exception as e:
        logger.exception("Unexpected Error while running fast view", exc_info=e)
        sys.exit(1)
