import typer
from typing import Dict

from pipeline import Pipeline
from pipeline.base import Env, StepDefinition
from pipeline.steps import (
    Copy,
    Templating,
    Compressing,
    UploadToStardog,
    UploadToFuseki,
)
from pipeline.steps.views import ViewsStep

app = typer.Typer()

steps: Dict[str, StepDefinition] = {
    "copyStatic": StepDefinition(
        Copy("static/static.n3", "static.n3"),
        "Copies static.n3 files from /static to defined output folder",
    ),
    "codeTemplating": StepDefinition(
        Templating("code.ttl.jinja", "code.ttl", "./sql/view_code.sql"),
        "Creates triples from the view_code data with the code.ttl template",
    ),
    "cubeTemplating": StepDefinition(
        Templating("cube.ttl.jinja", "cube.ttl", "./sql/view_cube.sql"),
        "Creates triples from the view_cube data with the cube.ttl template",
    ),
    "groupCodeTemplating": StepDefinition(
        Templating(
            "group_code.ttl.jinja", "group_code.ttl", "./sql/view_group_code.sql"
        )
    ),
    "hierarchyTemplating": StepDefinition(
        Templating("hierarchy.ttl.jinja", "hierarchy.ttl", "./sql/view_hierarchy.sql"),
        "Creates triples from the view_hierarchy data with the hierarchy.ttl template",
    ),
    "legalFoundationTemplating": StepDefinition(
        Templating(
            "legal_foundation.ttl.jinja",
            "legal_foundation.ttl",
            "./sql/view_legal_foundation.sql",
        )
    ),
    "measureUnitTemplating": StepDefinition(
        Templating(
            "measure_unit.ttl.jinja", "measure_unit.ttl", "./sql/view_measure_unit.sql"
        )
    ),
    "measureTemplating": StepDefinition(
        Templating("measure.ttl.jinja", "measure.ttl", "./sql/view_measure.sql"),
        "Creates triples from the view_measure data with the measure.ttl template",
    ),
    "observationTemplating": StepDefinition(
        Templating(
            "observation.ttl.jinja",
            "observation.ttl",
            "./sql/view_observation.sql",
        ),
        "Creates triples from the view_observation data with the observation.ttl template",
    ),
    "propertyTemplating": StepDefinition(
        Templating("property.ttl.jinja", "property.ttl", "./sql/view_property.sql"),
        "Creates triples from the view_property data with the property.ttl template",
    ),
    "roomTemplating": StepDefinition(
        Templating("room.ttl.jinja", "room.ttl", "./sql/view_room.sql"),
        "Creates triples from the view_room data with the room.ttl template",
    ),
    "timeTemplating": StepDefinition(
        Templating("time.ttl.jinja", "time.ttl", "./sql/view_time.sql"),
        "Creates triples from the view_time data with the time.ttl template",
    ),
    "compressing": StepDefinition(
        Compressing(), "Compresses all triple files to gzip files"
    ),
    "uploadToStardog": StepDefinition(
        UploadToStardog(),
        "Uploads all compressed gzip files to a configured stardog server",
    ),
    "uploadToFuseki": StepDefinition(
        UploadToFuseki(),
        "Uploads all compressed gzip files to a configured fuseki server",
    ),
    "generateViews": StepDefinition(
        ViewsStep(),
        "Generate all RDF files for ld views"
    ),
}


@app.command(short_help="Run pipeline on given environment")
def run(env: Env = Env.test):
    Pipeline(env).run(
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
        # steps["generateViews"].step,
        steps["compressing"].step,
        steps["uploadToStardog"].step,
        # steps["uploadToFuseki"].step,
    )


@app.command(short_help="Run single step on given environment")
def step(
    name: str = typer.Option(
        help="The name of the step to be executed. Get supported names with command 'list_steps'"
    ),
    env: Env = Env.test,
):
    Pipeline(env).step(steps[name].step)


@app.command(name="list-step-names", short_help="List names of all steps supported")
def list_step_names():
    print(
        ",\n".join('* "' + key + '": ' + val.description for key, val in steps.items())
    )


if __name__ == "__main__":
    app()
