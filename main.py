import typer
from pipeline import Pipeline, Env, Copy

app = typer.Typer()

steps = {"copyStatic": Copy("static/static.n3", "static.n3")}


@app.command(short_help="Run pipeline on given environment")
def run(env: Env = Env.test):
    Pipeline(env).run(steps["copyStatic"])


@app.command(short_help="Run single step on given environment")
def step(
    name: str = typer.Option(
        help="The name of the step to be executed. Get supported names with command 'list_steps'"
    ),
    env: Env = Env.test,
):
    Pipeline(env).step(steps[name])


@app.command(name="list-step-names", short_help="List names of all steps supported")
def list_step_names():
    print([key for key in steps.keys()])


if __name__ == "__main__":
    app()
