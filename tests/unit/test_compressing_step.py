import gzip
import os
import shutil
from unittest.mock import Mock

from pipeline.base import Env, Environment
from pipeline.steps import Compressing
from tests.unit.utils import TestUtils


def test_compressing():
    tmp_dir = TestUtils.abs_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    env = Environment(Env.test)
    env.config.get = Mock(
        side_effect=lambda arg: {
            "compression_output_path": TestUtils.abs_path("tmp"),
            "template_output_path": TestUtils.abs_path("data/triples"),
        }[arg]
    )

    try:
        Compressing().run(env)

        assert os.path.isfile(
            os.path.join(TestUtils.abs_path("tmp"), "sample_1.ttl.gz")
        )
        assert os.path.isfile(
            os.path.join(TestUtils.abs_path("tmp"), "sample_2.ttl.gz")
        )
        assert len(os.listdir(TestUtils.abs_path("tmp"))) == 2

        sample_1_content = gzip.open(
            os.path.join(TestUtils.abs_path("tmp"), "sample_1.ttl.gz")
        ).read()
        sample_2_content = gzip.open(
            os.path.join(TestUtils.abs_path("tmp"), "sample_2.ttl.gz")
        ).read()
        sample_1_expected_content = open(
            os.path.join(TestUtils.abs_path("data/triples"), "sample_1.ttl"), "rb"
        ).read()
        sample_2_expected_content = open(
            os.path.join(TestUtils.abs_path("data/triples"), "sample_2.ttl"), "rb"
        ).read()

        assert sample_1_expected_content == sample_1_content
        assert sample_2_expected_content == sample_2_content

    finally:
        shutil.rmtree(tmp_dir)
