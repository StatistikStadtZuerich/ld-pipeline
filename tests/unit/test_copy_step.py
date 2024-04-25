import os
import shutil
import unittest
from unittest.mock import MagicMock
from pipeline.steps import Copy
from pipeline.base import Environment, Env
from tests.unit.utils import TestUtils


class TestCopy(unittest.TestCase):
    def test_simple_copy(self):
        tmp_dir = TestUtils.abs_path("tmp")
        os.mkdir(tmp_dir)

        env = Environment(Env.test)
        env.get_config_value = MagicMock(return_value=TestUtils.abs_path("tmp") + "/")

        try:
            input_file = TestUtils.abs_path("data/copy-text.txt")
            output_file = "copy-target.txt"

            copy = Copy(input_file, output_file)
            copy.run(env)

            with open(TestUtils.abs_path("tmp/" + output_file), "r") as f:
                self.assertEqual(f.read(), "Hello World\n")

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
