import typer
from typing import Dict

from pipeline import Pipeline
from pipeline.base import Env, StepDefinition
from pipeline.steps import (
    Copy,
    Templating,
    ObservationTemplating,
    Compressing,
    UploadToStardog,
    UploadToFuseki,
)


app = typer.Typer()

steps: Dict[str, StepDefinition] = {
    "copyStatic": StepDefinition(
        Copy("static/static.n3", "static.n3"),
        "Copies static.n3 files from /static to defined output folder",
    ),
    "codeTemplating": StepDefinition(
        Templating("code.ttl.jinja", "code.ttl", "./sql/view_code.sql")
    ),
    "cubeTemplating": StepDefinition(
        Templating("cube.ttl.jinja", "cube.ttl", "./sql/view_cube.sql")
    ),
    "hierarchyTemplating": StepDefinition(
        Templating("hierarchy.ttl.jinja", "hierarchy.ttl", "./sql/view_hierarchy.sql")
    ),
    "measureTemplating": StepDefinition(
        Templating("measure.ttl.jinja", "measure.ttl", "./sql/view_measure.sql")
    ),
    "observationTemplating": StepDefinition(
        ObservationTemplating(
            "observation.ttl.jinja",
            "observation.ttl",
            "./sql/view_observation.sql",
        )
    ),
    "propertyTemplating": StepDefinition(
        Templating("property.ttl.jinja", "property.ttl", "./sql/view_property.sql")
    ),
    "room_hierarchyTemplating": StepDefinition(
        Templating(
            "room_hierarchy.ttl.jinja",
            "room_hierarchy.ttl",
            "./sql/view_room_hierarchy.sql",
        )
    ),
    "roomTemplating": StepDefinition(
        Templating("room.ttl.jinja", "room.ttl", "./sql/view_room.sql")
    ),
    "timeTemplating": StepDefinition(
        Templating("time.ttl.jinja", "time.ttl", "./sql/view_time.sql")
    ),
    "compressing": StepDefinition(Compressing()),
    "uploadToStardog": StepDefinition(UploadToStardog()),
    "uploadToFuseki": StepDefinition(UploadToFuseki()),
}


@app.command(short_help="Run pipeline on given environment")
def run(env: Env = Env.test):
    Pipeline(env).run(
        # steps["copyStatic"].step,
        steps["codeTemplating"].step,
        steps["cubeTemplating"].step,
        # steps["hierarchyTemplating"].step,
        # steps["measureTemplating"].step,
        # steps["observationTemplating"].step,
        # steps["propertyTemplating"].step,
        # steps["room_hierarchyTemplating"].step,
        # steps["roomTemplating"].step,
        # steps["timeTemplating"].step,
        steps["compressing"].step,
        steps["uploadToStardog"].step,
        steps["uploadToFuseki"].step,
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
