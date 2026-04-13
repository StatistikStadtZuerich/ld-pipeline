from database.base_sql_step import BaseSQLStep
from pipeline.base import Environment, Env

class MockEnvironment(Environment):
    def __init__(self, env: Env):
        super().__init__(env)
    
    def table_name(self, table_name: str) -> str:
        return f"{table_name}_expanded"

def test_filter_with_param_false():
    env = MockEnvironment(Env.int)
    
    template = "[{{ 'HDB' | table_name(False) }}]"
    
    rendered = BaseSQLStep.render_sql(env, template)
    assert rendered == "[HDB_expanded]"

def test_filter_with_param_true():
    env = MockEnvironment(Env.int)

    template = """[{{ "HDB" | table_name(True) }}]"""

    rendered = BaseSQLStep.render_sql(env, template)
    assert rendered == "[dbo].[HDB_expanded]"

def test_filter_with_params_false_false():
    env = MockEnvironment(Env.int)

    template = """{{ "HDB" | table_name(False, False) }}"""

    rendered = BaseSQLStep.render_sql(env, template)
    assert rendered == "HDB_expanded"

def test_filter_without_param():
    env = MockEnvironment(Env.int)

    template = "[{{ 'HDB' | table_name }}]"

    rendered = BaseSQLStep.render_sql(env, template)
    assert rendered == "[dbo].[HDB_expanded]"
