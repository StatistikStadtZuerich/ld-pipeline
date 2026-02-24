import typer
from typing import Dict
import logging

from pipeline import Pipeline
from pipeline.base import Env, StepDefinition, Environment
from pipeline.steps import (
    Copy,
    Compressing,
    CopyHDBToPipeTables,
    BuildTermsetHierarchy,
    WritePublicationStatiToHDB,
    CreateViewsFromSQL,
    create_templating,
)
from pipeline.steps.views import ViewsStep
from pipe_tables import InitPipeTables

app = typer.Typer()
logger = logging.getLogger(__name__)


def get_step_definitions(env: Environment, options=None) -> Dict[str, StepDefinition]:
    if options is None:
        options = {}
    env_name = env.name
    options["env"] = env_name
    return {
        stepDef.name: stepDef
        for stepDef in [
            StepDefinition(
                "copyStatic",
                Copy("./static/static.ttl", "static.ttl", options=options),
                "Copies static.ttl files from /static to defined output folder",
            ),
            StepDefinition(
                "codeTemplating",
                create_templating(
                    env,
                    "code.ttl.jinja",
                    "code.ttl",
                    f"./sql/{env_name}/view_access/view_code.sql",
                    options=options,
                ),
                "Creates triples from the view_code data with the code.ttl template",
            ),
            StepDefinition(
                "cubeTemplating",
                create_templating(
                    env,
                    "cube.ttl.jinja",
                    "cube.ttl",
                    f"./sql/{env_name}/view_access/view_cube.sql",
                    options=options,
                ),
                "Creates triples from the view_cube data with the cube.ttl template",
            ),
            StepDefinition(
                "groupCodeTemplating",
                create_templating(
                    env,
                    "group_code.ttl.jinja",
                    "group_code.ttl",
                    f"./sql/{env_name}/view_access/view_group_code.sql",
                    options=options,
                ),
            ),
            StepDefinition(
                "hierarchyTemplating",
                create_templating(
                    env,
                    "hierarchy.ttl.jinja",
                    "hierarchy.ttl",
                    f"./sql/{env_name}/view_access/view_hierarchy.sql",
                    options=options,
                ),
                "Creates triples from the view_hierarchy data with the hierarchy.ttl template",
            ),
            StepDefinition(
                "legalFoundationTemplating",
                create_templating(
                    env,
                    "legal_foundation.ttl.jinja",
                    "legal_foundation.ttl",
                    f"./sql/{env_name}/view_access/view_legal_foundation.sql",
                    options=options,
                ),
            ),
            StepDefinition(
                "measureUnitTemplating",
                create_templating(
                    env,
                    "measure_unit.ttl.jinja",
                    "measure_unit.ttl",
                    f"./sql/{env_name}/view_access/view_measure_unit.sql",
                    options=options,
                ),
            ),
            StepDefinition(
                "measureTemplating",
                create_templating(
                    env,
                    "measure.ttl.jinja",
                    "measure.ttl",
                    f"./sql/{env_name}/view_access/view_measure.sql",
                    options=options,
                ),
                "Creates triples from the view_measure data with the measure.ttl template",
            ),
            StepDefinition(
                "observationTemplating",
                create_templating(
                    env,
                    "observation.ttl.jinja",
                    "observation.ttl",
                    f"./sql/{env_name}/view_access/view_observation.sql",
                    options=options,
                ),
                "Creates triples from the view_observation data with the observation.ttl template",
            ),
            StepDefinition(
                "propertyTemplating",
                create_templating(
                    env,
                    "property.ttl.jinja",
                    "property.ttl",
                    f"./sql/{env_name}/view_access/view_property.sql",
                    options=options,
                ),
                "Creates triples from the view_property data with the property.ttl template",
            ),
            StepDefinition(
                "roomTemplating",
                create_templating(
                    env,
                    "room.ttl.jinja",
                    "room.ttl",
                    f"./sql/{env_name}/view_access/view_room.sql",
                    options=options,
                ),
                "Creates triples from the view_room data with the room.ttl template",
            ),
            StepDefinition(
                "timeTemplating",
                create_templating(
                    env,
                    "time.ttl.jinja",
                    "time.ttl",
                    f"./sql/{env_name}/view_access/view_time.sql",
                    options=options,
                ),
                "Creates triples from the view_time data with the time.ttl template",
            ),
            StepDefinition(
                "timeTermsetTemplating",
                create_templating(
                    env,
                    "time_termset.ttl.jinja",
                    "time_termset.ttl",
                    f"./sql/{env_name}/view_access/view_time_termset_relation.sql",
                    options=options,
                ),
                "Creates triples for time termset relations",
            ),
            StepDefinition(
                "compressing",
                Compressing(),
                "Compresses all triple files to gzip files",
            ),
            # StepDefinition(
            #     "uploadToStardog",
            #     create_stardog_uploader(env),
            #     "Uploads all compressed gzip files to a configured stardog server",
            # ),
            # StepDefinition(
            #     "uploadToFuseki",
            #     create_fuseki_uploader(env),
            #     "Uploads all compressed gzip files to a configured fuseki server",
            # ),
            StepDefinition(
                "copyHDBToPipeTables",
                CopyHDBToPipeTables(),
                "Copy HDB to pipe tables",
            ),
            StepDefinition(
                "initPipeTables",
                InitPipeTables(
                    [
                        "./sql/shared/pipe_tables",
                        f"./sql/{env_name}/pipe_tables",
                    ]
                ),
                "Initiate and define pipe tables",
            ),
            StepDefinition(
                "createViewsFromSQL",
                CreateViewsFromSQL(f"./sql/{env_name}/view_definition"),
                "Create DB Views from SQL",
            ),
            StepDefinition(
                "generateViews",
                ViewsStep(),
                "Generate all RDF files for ld views",
            ),
            StepDefinition(
                "buildTermsetHierarchy",
                BuildTermsetHierarchy(
                    "raum_hierarchy.ttl.jinja",
                    "termset_hierarchy.ttl",
                    f"./sql/{env_name}/view_access/view_room_hierarchy.sql",
                    options=options,
                ),
                "Creates triples from the view_room_hierarchy data with the raum_hierarchy.ttl template",
            ),
            StepDefinition(
                "writePublicationStatiToHDB",
                WritePublicationStatiToHDB(),
                "Write publication stati back to the HDB",
            ),
        ]
    }


@app.command(short_help="Run pipeline on given environment")
def run(environment: Environment):
    steps = get_step_definitions(environment)
    Pipeline(environment).run(
        steps["copyStatic"].step,
        steps["codeTemplating"].step,
        steps["cubeTemplating"].step,
        steps["groupCodeTemplating"].step,
        steps["hierarchyTemplating"].step,
        steps["legalFoundationTemplating"].step,
        steps["measureUnitTemplating"].step,
        steps["measureTemplating"].step,
        steps["observationTemplating"].step,
        steps["propertyTemplating"].step,
        steps["roomTemplating"].step,
        steps["timeTemplating"].step,
        steps["timeTermsetTemplating"].step,
        steps["compressing"].step,
        # steps["uploadToStardog"].step,
        steps["initPipeTables"].step,
        steps["copyHDBToPipeTables"].step,
        steps["InitPipeTables"].step,
        steps["createViewsFromSQL"].step,
        # steps["uploadToFuseki"].step,
    )


@app.command(short_help="Run single step on given environment")
def step(
    name: str = typer.Option(
        help="The name of the step to be executed. Get supported names with command 'list_steps'"
    ),
    env: Environment = None,
    options=None,
):
    steps = get_step_definitions(env, options)
    logger.info(f"Running step {name}")
    Pipeline(env).step(steps[name])


@app.command(name="list-step-names", short_help="List names of all steps supported")
def list_step_names():
    steps = get_step_definitions(Environment(Env.test))
    print(
        ",\n".join('* "' + key + '": ' + val.description for key, val in steps.items())
    )


if __name__ == "__main__":
    app()
