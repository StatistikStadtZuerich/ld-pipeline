import time

from ..base import Step, Environment, Utils


class CopyHDBToPipeTables(Step):
    def __init__(self, env):
        super().__init__()
        self._env = env
        self._utils = Utils()

    def run(self, environment: Environment):
        suffix = "TEST"
        if self._env.upper() == "PROD":
            suffix = "FINAL"
        tablenames = [
            "HDBCodeliste",
            "HDBCubeDefinition",
            f"HDBDatenattribute_{suffix}",
            f"HDBDatenattributeObjekte_{suffix}",
            f"HDBDatenobjekte_{suffix}",
            "HDBGruppenliste",
            "HDBHierarchien",
            "HDBKennzahlen",
            "HDBRaum",
            f"HDBRechtsgrundlagen_{suffix}",
            "HDBZeit",
            f"HDB_{suffix}",
        ]
        start_time = time.time()
        self._utils.print_formatted('Copying HDB data to the "pipe" tables ...')
        self._copy_hdb_data_to_pipe_tables(environment, tablenames)
        end_time = time.time()
        execution_time = end_time - start_time
        self._utils.print_formatted(
            f"Execution time for copying HDB data to the pipe tables: {execution_time:.2f} seconds"
        )

    def _copy_hdb_data_to_pipe_tables(self, environment, tablenames):
        with environment.get_db_connection() as connection:
            try:
                with connection.cursor() as cursor:
                    for tablename in tablenames:
                        self._utils.print_formatted(
                            f"Copying {tablename} to pipe_{tablename} ..."
                        )
                        cursor.execute(f"""
                                SELECT COLUMN_NAME
                                FROM INFORMATION_SCHEMA.COLUMNS
                                WHERE TABLE_NAME = 'pipe_{tablename}'
                                AND TABLE_SCHEMA = 'dbo'
                                AND COLUMN_NAME NOT IN ('hash')
                                AND NOT (TABLE_NAME IN ('pipe_HDB_TEST', 'pipe_HDB_FINAL') AND COLUMN_NAME IN ('TAG','MONAT'))
                            """)
                        columns = cursor.fetchall()
                        columns = [f'"{col["COLUMN_NAME"]}"' for col in columns]
                        columns_list = ", ".join(columns)
                        #cursor.execute(f"""
                        #        SELECT TOP 10 * FROM #pipe_{tablename}
                        #    """)
                        #rows=cursor.fetchall()
                        #for row in rows:
                        #    print(row)
                        if tablename in ("HDB_TEST", "HDB_FINAL"):
                            stmt_insert = f"""
                                INSERT INTO pipe_{tablename} ({columns_list}, hash)
                                SELECT {columns_list}, CAST(NULL AS VARBINARY) FROM #pipe_{tablename}
                            """
                        else:
                            stmt_insert = f"""
                                INSERT INTO pipe_{tablename}
                                SELECT {columns_list} FROM #pipe_{tablename}
                            """
                        print(stmt_insert)
                        cursor.execute(f"""
                                TRUNCATE TABLE pipe_{tablename};
                                DROP TABLE IF EXISTS #pipe_{tablename};
                                SELECT {columns_list} INTO #pipe_{tablename} FROM {tablename};
                                {stmt_insert};
                            """)
                        self._utils.print_formatted("Done")
                connection.commit()
            except Exception:
                connection.rollback()
                raise
