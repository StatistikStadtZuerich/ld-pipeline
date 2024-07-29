import requests
import main
from pipeline.base import Utils

Utils.is_jupyter_notebook = True
env = main.Env.int


def run_pipeline():
    # pipeline = Pipeline(env)
    utils = Utils()

    # Check if start signal has arrived
    """
    if utils.check_start_signal(env):
        utils.print_formatted("Pipeline started ...")
    else:
        utils.print_formatted("There is no start signal.")
        return
    """

    # Update pipe tables
    # main.step(name="copyHDBToPipeTables", env=env)

    # Generate triple files
    generate_triple_files()

    # Generate triple files from the viewbuilder
    main.step(name="generateViews", env=env)

    # Generate termset hierarchy triples
    main.step(name="buildTermsetHierarchy", env=env)

    # Upload triple files to Stardog
    # main.step(name="uploadToStardog", env=env)

    # Upload triple files to Fuseki
    utils.print_formatted("Clearing Fuseki server ...")
    reset_fuseki_server()
    main.step(name="uploadToFuseki", env=env)

    # Set finish signal
    """
    utils.set_finish_signal(env)
    utils.print_formatted("Pipeline is finished.")
    """


def generate_triple_files():
    names = [
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
        "observation",
    ]

    options = {
        "db_batch_size": 100000,
        "write_batch_size": 600000,
        "max_iteration": None,
    }

    for name in names:
        main.step(name=f"{name}Templating", env=env, options=options)


def reset_fuseki_server():
    server_url = "http://localhost:8080/fuseki/ssz/update"
    query = """
        DELETE WHERE {
            ?s ?p ?o.
        }
    """
    response = requests.post(server_url, data={"update": query})
    if response.status_code == 200:
        print("All triples are successfully deleted.")
    else:
        print(f"Status code: {response.status_code}, Error: {response.text}")


if __name__ == "__main__":
    run_pipeline()
