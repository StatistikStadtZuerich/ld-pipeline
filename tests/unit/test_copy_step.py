import os
import shutil
import unittest
from unittest.mock import Mock
from pipeline.steps import Copy
from pipeline.base import Environment, Env
from tests.unit.utils import TestUtils


class TestCopy(unittest.TestCase):
    def test_simple_copy(self):
        tmp_dir = TestUtils.abs_path("tmp")
        os.mkdir(tmp_dir)

        env = Environment(Env.test)
        mocked_config = {"test_output_path": TestUtils.abs_path("tmp/")}

        def side_effect(arg):
            return mocked_config[arg]

        env.config.get = Mock(side_effect=side_effect)

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
