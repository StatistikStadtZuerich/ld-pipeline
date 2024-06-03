import os
import shutil
import unittest
from unittest.mock import Mock, call, patch, ANY

from pipeline.base import Env, Environment
from pipeline.steps import UploadToStardog
from tests.unit.utils import TestUtils


class TestUploadToFusekiStep(unittest.TestCase):
    @patch("stardog.Connection")
    def test_templating(self, mock_connection):
        tmp_dir = TestUtils.abs_path("tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        env = Environment(Env.test)
        env.config.get = Mock(
            side_effect=lambda arg: {
                "compression_output_path": TestUtils.abs_path("data/compressed"),
                "stardog_endpoint": "http://localhost:3030",
                "stardog_database": "test",
                "stardog_graph_uri": "https://lindas.admin.ch/stadtzuerich",
                "stardog_username": "testuser",
                "stardog_password": "starkespasswort",
            }[arg]
        )

        try:
            UploadToStardog().run(env)
            mock_connection.assert_any_call(
                database="test",
                endpoint="http://localhost:3030",
                username="testuser",
                password="starkespasswort",
            )
            mock_connection().__enter__().add.assert_has_calls(
                [
                    call(ANY, "https://lindas.admin.ch/stadtzuerich"),
                    call(ANY, "https://lindas.admin.ch/stadtzuerich"),
                ]
            )

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
