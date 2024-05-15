import typer
from typing import Dict
from pipeline import Pipeline
from pipeline.base import Env, StepDefinition
from pipeline.steps import (
    Copy,
    Templating,
    ObservationTemplating,
    Zipping,
    UploadToStardog,
)

app = typer.Typer()

steps: Dict[str, StepDefinition] = {
    "copyStatic": StepDefinition(
        Copy("static/static.n3", "static.n3"),
        "Copies static.n3 files from /static to defined output folder",
    ),
    "codeTemplating": StepDefinition(
        Templating("code.ttl.jinja", "code.ttl", "./tmp/sources/view_code.sql")
    ),
    "cubeTemplating": StepDefinition(
        Templating("cube.ttl.jinja", "cube.ttl", "./tmp/sources/view_cube.sql")
    ),
    "hierarchyTemplating": StepDefinition(
        Templating(
            "hierarchy.ttl.jinja", "hierarchy.ttl", "./tmp/sources/view_hierarchy.sql"
        )
    ),
    "measureTemplating": StepDefinition(
        Templating("measure.ttl.jinja", "measure.ttl", "./tmp/sources/view_measure.sql")
    ),
    "observationTemplating": StepDefinition(
        ObservationTemplating(
            "observation.ttl.jinja",
            "observation.ttl",
            "./tmp/sources/view_observation.sql",
        )
    ),
    "propertyTemplating": StepDefinition(
        Templating(
            "property.ttl.jinja", "property.ttl", "./tmp/sources/view_property.sql"
        )
    ),
    "room_hierarchyTemplating": StepDefinition(
        Templating(
            "room_hierarchy.ttl.jinja",
            "room_hierarchy.ttl",
            "./tmp/sources/view_room_hierarchy.sql",
        )
    ),
    "roomTemplating": StepDefinition(
        Templating("room.ttl.jinja", "room.ttl", "./tmp/sources/view_room.sql")
    ),
    "timeTemplating": StepDefinition(
        Templating("time.ttl.jinja", "time.ttl", "./tmp/sources/view_time.sql")
    ),
    "rdfZipping": StepDefinition(Zipping("rdf.zip")),
    "uploadToStardog": StepDefinition(UploadToStardog("rdf.zip")),
}


@app.command(short_help="Run pipeline on given environment")
def run(env: Env = Env.test):
    Pipeline(env).run(
        # steps["copyStatic"].step,
        # steps["codeTemplating"].step,
        steps["cubeTemplating"].step,
        steps["rdfZipping"].step,
        steps["uploadToStardog"].step,
        # steps["hierarchyTemplating"].step,
        # steps["measureTemplating"].step,
        # steps["observationTemplating"].step,
        # steps["propertyTemplating"].step,
        # steps["room_hierarchyTemplating"].step,
        # steps["roomTemplating"].step,
        # steps["timeTemplating"].step,
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
