import pytest
import mysql.connector

def is_responsive(docker_ip, port):
    try:
        cnx = mysql.connector.connect(user='pipeline', password='pipeline', host=docker_ip, port=port, database='hdb')
        if cnx and cnx.is_connected():
            cnx.close()
            return True
        else:
            return False

    except mysql.connector.errors.DatabaseError:
        return False


@pytest.fixture(scope="session")
def mysql_service(docker_ip, docker_services):
    port = docker_services.port_for("db", 3306)
    docker_services.wait_until_responsive(
        timeout=100, pause=2, check=lambda: is_responsive(docker_ip, port)
    )
    return True


def test_mysql_connection(mysql_service):
    assert mysql_service
