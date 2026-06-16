import gzip
import os
import shutil
from unittest.mock import Mock

from pipeline.base import Env, Environment
from pipeline.steps import Copy
from tests.unit.utils import TestUtils


def test_simple_copy():
    tmp_dir = TestUtils.abs_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    env = Environment(Env.test)
    env.config.get = Mock(
        side_effect=lambda arg: {"output_path": TestUtils.abs_path("tmp")}[arg]
    )

    try:
        input_file = TestUtils.abs_path("data/copy-text.txt")
        output_file = "copy-target.txt"

        copy = Copy(input_file, output_file, {"env": "test"})
        copy.run(env)

        with gzip.open(
            os.path.join(TestUtils.abs_path("tmp"), output_file + ".gz"), mode="rt"
        ) as f:
            assert "Hello World\n" == f.read()

    finally:
        shutil.rmtree(tmp_dir)
