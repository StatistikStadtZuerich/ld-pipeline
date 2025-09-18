import requests
import main
from pipeline.base import Utils

Utils.is_jupyter_notebook = False
env = main.Env.int


def run_pipeline():
    utils = Utils()

    # Check if start signal has arrived
    if utils.check_start_signal(env):
        utils.print_formatted("Pipeline started ...")
    else:
        # utils.print_formatted("There is no start signal.")
        return

    # Update pipe tables
    main.step(name="copyHDBToPipeTables", env=env)
    try:
        main.step(name="syncPipeSharepointSasaOutput", env=env)
    except Exception as e:
        utils.print_formatted(f"Could not synchronize sharepoint: {e}")

    # Generate triple files
    generate_triple_files()

    # Create start signal to generate the Fuseki index
    utils = Utils()
    utils.set_start_signal_fuseki_index(env)

    # Write back the publication status to the HDB
    main.step(name="writePublicationStatiToHDB", env=env)

    # Set finish signal
    utils.set_finish_signal(env)
    utils.print_formatted("Pipeline is finished.")


def generate_triple_files():
    triple_types_metadata = [
        "code",
        "cube",
        "groupCode",
        "hierarchy",
        "legalFoundation",
        "measureUnit",
        "measure",
        "property",
        "room",
        "time",
    ]
    triple_types_observations = ["observation"]
    triple_types_others = ["copyStatic", "buildTermsetHierarchy", "generateViews"]

    options_batching = {
        "db_batch_size": 100000,
        "write_batch_size": 600000,
        "max_iteration": None,
    }
    for name in triple_types_metadata:
        main.step(name=f"{name}Templating", env=env, options=options_batching)
    for name in triple_types_observations:
        main.step(name=f"{name}Templating", env=env, options=options_batching)
    for name in triple_types_others:
        main.step(name=name, env=env)


if __name__ == "__main__":
    run_pipeline()
