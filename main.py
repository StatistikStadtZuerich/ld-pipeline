import typer
from pipeline import Pipeline, Env, Copy

app = typer.Typer()


@app.command(short_help="Run pipeline on given environment")
def run(env: Env = Env.test):
    Pipeline(env).run(
        Copy()
    )


@app.command(short_help="Run single step on given environment")
def step(
        name: str = typer.Option(
            help="The name of the step to be executed. Get supported names with command 'list_steps'"
        ),
        env: Env = Env.test
):
    Pipeline(env).step(name)


@app.command(name="list-step-names", short_help="List names of all steps supported")
def list_step_names():
    print(Pipeline.step_names())


if __name__ == "__main__":
    app()
