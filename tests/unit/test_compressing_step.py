import gzip
import os
import shutil
import unittest
from unittest.mock import Mock

from pipeline.base import Env, Environment
from pipeline.steps import Compressing
from tests.unit.utils import TestUtils


class TestCompressingStep(unittest.TestCase):
    def test_compressing(self):
        tmp_dir = TestUtils.abs_path("tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        env = Environment(Env.test)
        env.config.get = Mock(
            side_effect=lambda arg: {
                "compression_output_path": tmp_dir,
            }[arg]
        )
        triples_dir = TestUtils.abs_path("data/triples")

        try:
            Compressing(directory=triples_dir).run(env)

            self.assertTrue(os.path.isfile(os.path.join(tmp_dir, "sample_1.ttl.gz")))
            self.assertTrue(os.path.isfile(os.path.join(tmp_dir, "sample_2.ttl.gz")))
            self.assertTrue(len(os.listdir(tmp_dir)) == 2)

            sample_1_content = gzip.open(
                os.path.join(tmp_dir, "sample_1.ttl.gz")
            ).read()
            sample_2_content = gzip.open(
                os.path.join(tmp_dir, "sample_2.ttl.gz")
            ).read()
            sample_1_expected_content = open(
                os.path.join(triples_dir, "sample_1.ttl"), "rb"
            ).read()
            sample_2_expected_content = open(
                os.path.join(triples_dir, "sample_2.ttl"), "rb"
            ).read()

            self.assertEqual(sample_1_content, sample_1_expected_content)
            self.assertEqual(sample_2_content, sample_2_expected_content)

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
