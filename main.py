import typer
from typing import Dict
from pipeline import Pipeline, Env, StepDefinition, Copy, Templating

app = typer.Typer()

steps: Dict[str, StepDefinition] = {
    "copyStatic": StepDefinition(
        Copy("static/static.n3", "static.n3"),
        "Copies static.n3 files from /static to defined output folder",
    ),
    "dimensionTemplating": StepDefinition(
        Templating("ttl_template.jinja", "dimensionen.ttl", "./HDB_DIMENSIONEN.csv"),
        "Creates a .ttl file out of the given csv data.",
    ),
}


@app.command(short_help="Run pipeline on given environment")
def run(env: Env = Env.test):
    Pipeline(env).run(steps["copyStatic"].step, steps["dimensionTemplating"].step)


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
