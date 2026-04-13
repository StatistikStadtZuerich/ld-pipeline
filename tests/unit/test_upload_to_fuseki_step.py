import os
import secrets
import shutil
import string
from unittest.mock import Mock, call, patch

from pipeline.base import Env, Environment
from pipeline.steps import UploadToFuseki
from tests.unit.utils import TestUtils


@patch("requests.put")
def test_upload_to_fuseki(mock_request_put):
    tmp_dir = TestUtils.abs_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    def generate_password(length: int = 16) -> str:
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return "".join(secrets.choice(alphabet) for _ in range(length))

    password = generate_password()

    env = Environment(Env.test)
    env.config.get = Mock(
        side_effect=lambda arg: {
            "compression_output_path": TestUtils.abs_path("data/compressed"),
            "fuseki_endpoint": "http://localhost:3030",
            "fuseki_dataset": "test",
            "fuseki_graph": "eingraph",
            "fuseki_username": "testuser",
            "fuseki_password": password,
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
                    auth=("testuser", password),
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
                    auth=("testuser", password),
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
