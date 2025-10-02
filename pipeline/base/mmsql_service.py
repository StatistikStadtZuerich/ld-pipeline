from typing import TYPE_CHECKING

import pymssql

from pipeline.interfaces.services import DbConnection

if TYPE_CHECKING:
    from .environment import Environment


class MSSQLDbConnection(DbConnection):
    def __init__(self, environment: "Environment"):
        super().__init__()
        self._config = environment.config

    def query(self, query: str):
        """
        Executes query and returns cursor.
        """
        self._cursor.execute(query)
        return self._cursor

    def cursor(self):
        return self._cursor

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def __enter__(self):
        self._connection = pymssql.connect(
            server=self._config.get("db_host"),
            port=self._config.get("db_port", fallback=1433),
            database=self._config.get("db_dbname"),
            user=self._config.get("db_user"),
            password=self._config.get("db_password"),
        )
        self._cursor = self._connection.cursor(as_dict=True)
        self.logger.info(
            f"Database connection to {self._config.get('db_host')}:{self._config.get('db_port', fallback=1433)}/{self._config.get('db_dbname')} established..."
        )
        return self

    def __exit__(self, *exc_details):
        self._connection.close()
        self.logger.info(
            f"Database connection to {self._config.get('db_host')}:{self._config.get('db_port', fallback=1433)}/{self._config.get('db_dbname')} closed"
        )
