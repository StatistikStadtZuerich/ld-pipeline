import os
import shutil
import unittest
from unittest.mock import Mock, call, patch

from pipeline.base import Env, Environment
from pipeline.steps import UploadToFuseki
from tests.unit.utils import TestUtils


class TestUploadToFusekiStep(unittest.TestCase):
    @patch("requests.put")
    def test_templating(self, mock_request_put):
        tmp_dir = TestUtils.abs_path("tmp")
        os.mkdir(tmp_dir)

        env = Environment(Env.test)
        env.config.get = Mock(
            side_effect=lambda arg: {
                "compression_output_path": TestUtils.abs_path("data/compressed"),
                "fuseki_endpoint": "http://localhost:3030",
                "fuseki_dataset": "test",
                "fuseki_graph": "eingraph",
                "fuseki_username": "testuser",
                "fuseki_password": "starkespasswort",
            }[arg]
        )

        try:
            UploadToFuseki().run(env)
            mock_request_put.assert_has_calls(
                [
                    call(
                        url="http://localhost:3030/test/data?eingraph",
                        data=open(
                            os.path.join(
                                TestUtils.abs_path("data/compressed"), "sample_1.ttl.gz"
                            ),
                            "rb",
                        ).read(),
                        auth=("testuser", "starkespasswort"),
                        headers={
                            "Content-Type": "text/turtle",
                            "Content-Encoding": "gzip",
                        },
                    ),
                    call(
                        url="http://localhost:3030/test/data?eingraph",
                        data=open(
                            os.path.join(
                                TestUtils.abs_path("data/compressed"), "sample_2.ttl.gz"
                            ),
                            "rb",
                        ).read(),
                        auth=("testuser", "starkespasswort"),
                        headers={
                            "Content-Type": "text/turtle",
                            "Content-Encoding": "gzip",
                        },
                    ),
                ],
                any_order=True,
            )

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
