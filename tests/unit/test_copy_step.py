import os
import shutil
import unittest
from unittest.mock import Mock
from pipeline.steps import Copy
from pipeline.base import Environment, Env
from tests.unit.test import UnitTest


class TestCopy(unittest.TestCase):
    def test_simple_copy(self):
        tmp_dir = UnitTest.abs_path("tmp")
        os.mkdir(tmp_dir)

        env = Environment(Env.test)
        mocked_config = {"output_path": UnitTest.abs_path("tmp/")}

        def side_effect(arg):
            return mocked_config[arg]

        env.config.get = Mock(side_effect=side_effect)

        try:
            input_file = UnitTest.abs_path("data/copy-text.txt")
            output_file = "copy-target.txt"

            copy = Copy(input_file, output_file)
            copy.run(env)

            with open(UnitTest.abs_path("tmp/" + output_file), "r") as f:
                self.assertEqual(f.read(), "Hello World\n")

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
