import unittest
from database.base_sql_step import BaseSQLStep
from pipeline.base import Environment, Env

class MockEnvironment(Environment):
    def __init__(self, env: Env):
        super().__init__(env)
    
    def table_name(self, table_name: str) -> str:
        return f"{table_name}_expanded"

class TestJinjaFilterParams(unittest.TestCase):
    def test_filter_with_param_false(self):
        env = MockEnvironment(Env.int)
        
        template = "[{{ 'HDB' | table_name(False) }}]"
        
        rendered = BaseSQLStep.render_sql(env, template)
        self.assertEqual(rendered, "[HDB_expanded]")

    def test_filter_with_param_true(self):
        env = MockEnvironment(Env.int)

        template = """[{{ "HDB" | table_name(True) }}]"""

        rendered = BaseSQLStep.render_sql(env, template)
        self.assertEqual(rendered, "[dbo].[HDB_expanded]")

    def test_filter_with_params_false_false(self):
        env = MockEnvironment(Env.int)

        template = """{{ "HDB" | table_name(False, False) }}"""

        rendered = BaseSQLStep.render_sql(env, template)
        self.assertEqual(rendered, "HDB_expanded")

    def test_filter_without_param(self):
        env = MockEnvironment(Env.int)

        template = "[{{ 'HDB' | table_name }}]"

        rendered = BaseSQLStep.render_sql(env, template)
        self.assertEqual(rendered, "[dbo].[HDB_expanded]")

    def test_behavior_investigation(self):
        env = Environment(Env.int)
        print(f"Env name: {env.name}")
        print(f"Table name for 'test': {env.table_name('test')}")
        print(f"Rendered 'test': {BaseSQLStep.render_sql(env, '[{{ \"test\" | table_name }}]')}")

if __name__ == "__main__":
    unittest.main()
