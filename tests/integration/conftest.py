import os
import pytest


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    """
    Create location and filename of the docker-compose used for the integration test
    :param pytestconfig:
    :return: the path of the docker compose file
    """
    return os.path.join(str(pytestconfig.rootdir), "tests/integration", "compose.yaml")
