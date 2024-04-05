import pytest
import mysql.connector


def is_responsive(docker_ip, port):
    """
    Checks if the mysql database is accessible
    :param docker_ip: the host of the database
    :param port: the port of the database
    :return: if the connection can be established
    """
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
    """
    The fixture waits until the mysql database is up and running
    :param docker_ip: the ip address of the database container
    :param docker_services: the docker service provided by the fixture
    :return: True as soon as the connection can be established, throws error after timeout is reached
    """
    port = docker_services.port_for("db", 3306)
    docker_services.wait_until_responsive(
        timeout=100, pause=2, check=lambda: is_responsive(docker_ip, port)
    )
    return True


def test_mysql_connection(mysql_service):
    """
    assert that the mysql connection can be established
    :param mysql_service: True
    """
    assert mysql_service
