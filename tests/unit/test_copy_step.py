import os
import shutil
import unittest
from unittest.mock import Mock

from pipeline.base import Env, Environment
from pipeline.steps import Copy
from tests.unit.utils import TestUtils


class TestCopy(unittest.TestCase):
    def test_simple_copy(self):
        tmp_dir = TestUtils.abs_path("tmp")
        os.mkdir(tmp_dir)

        env = Environment(Env.test)
        env.config.get = Mock(
            side_effect=lambda arg: {"output_path": TestUtils.abs_path("tmp")}[arg]
        )

        try:
            input_file = TestUtils.abs_path("data/copy-text.txt")
            output_file = "copy-target.txt"

            copy = Copy(input_file, output_file)
            copy.run(env)

            with open(os.path.join(TestUtils.abs_path("tmp"), output_file)) as f:
                self.assertEqual(f.read(), "Hello World\n")

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
