import pymssql

from pipeline.interfaces.services import DbConnection


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
            server=self._config.get("mssql_host"),
            database=self._config.get("mssql_database"),
            user=self._config.get("mssql_user"),
            password=self._config.get("mssql_password"),
        )
        self._cursor = self._connection.cursor(as_dict=True)
        self.logger.info(
            f"Database connection to {self._config.get('mssql_server')}/{self._config.get('mssql_database')} established..."
        )
        return self

    def __exit__(self, *exc_details):
        self._connection.close()
        self.logger.info(
            f"Database connection to {self._config.get('mssql_server')}/{self._config.get('mssql_database')} closed"
        )
