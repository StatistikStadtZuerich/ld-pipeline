import typer
from typing import Dict
from pipeline import Pipeline
from pipeline.base import Env, StepDefinition
from pipeline.steps import Copy, Templating, ObservationTemplating

app = typer.Typer()

steps: Dict[str, StepDefinition] = {
    "copyStatic": StepDefinition(
        Copy("static/static.n3", "static.n3"),
        "Copies static.n3 files from /static to defined output folder",
    ),
    "dimensionsTemplating": StepDefinition(
        Templating(
            "dimensionen.ttl.jinja",
            "dimensions.ttl",
            "./tmp/sources/HDB_DIMENSIONEN.csv",
        )
    ),
    "observationTemplating": StepDefinition(
        ObservationTemplating(
            "observations.ttl.jinja",
            "observations.ttl",
            "./HDB_small.csv",
        )
    ),
    "cubeTemplating": StepDefinition(
        Templating("cubes.ttl.jinja", "cubes.ttl", "./tmp/sources/HDB_CUBES.csv")
    ),
}


@app.command(short_help="Run pipeline on given environment")
def run(env: Env = Env.test):
    Pipeline(env).run(
        steps["copyStatic"].step,
        steps["dimensionsTemplating"].step,
        steps["observationTemplating"].step,
        steps["cubeTemplating"].step,
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
