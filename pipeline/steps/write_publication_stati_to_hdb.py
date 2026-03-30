from database import BaseSQLStep
from ..base import Step, Environment, Utils


class WritePublicationStatiToHDB(Step):
    def __init__(self):
        super().__init__()
        self._utils = Utils()

    def run(self, environment: Environment):
        suffix = environment.table_suffix
        self.logger.info("Calculating observation hashes ...")
        self._calculate_observation_hashes(environment, suffix)
        self.logger.info("Done")

        with environment.get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    BaseSQLStep.render_sql(
                        environment,
                        """
                        SELECT COLUMN_NAME
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = '{{ 'pipe_HDB' | pipe_table_name }}'
                        AND TABLE_SCHEMA = 'dbo'
                        AND COLUMN_NAME NOT IN ('hash')
                        """)
                )
                columns = cursor.fetchall()
                column_names = [column["COLUMN_NAME"] for column in columns]
                concat_expression = " + ".join(
                    [
                        f"CONVERT(VARCHAR(MAX),ISNULL({column}, ''))"
                        for column in column_names
                    ]
                )

                self.logger.info(f"Creating temporary table #hash_HDB_{suffix} ...")
                query = BaseSQLStep.render_sql(
                    environment,
                    """
                    DROP TABLE IF EXISTS '{{ '#hash_HDB' | pipe_table_name }}';
                    CREATE TABLE '{{ '#hash_HDB' | pipe_table_name }}' (
                        GESAMTCODE nvarchar(60),
                        hash VARBINARY(16)
                    )
                """)
                cursor.execute(query)
                query = BaseSQLStep.render_sql(
                    environment,
                   f"""
                    INSERT INTO '{{ '#hash_HDB' | pipe_table_name }}' (GESAMTCODE, hash)
                    SELECT 
                        GESAMTCODE,
                        HASHBYTES('MD5', CONVERT(VARBINARY(MAX), {concat_expression}))
                    FROM
                        '{{ 'HDB' | table_name }}' h
                    WHERE
                        h.RECORDSTATUS = '0'
                    AND
                        h.CUBEID <> ''
                """)
                cursor.execute(query)
                self.logger.info("done")

                self.logger.info(f"Updating publication stati to HDB_{suffix} ...")
                query = BaseSQLStep.render_sql(
                    environment,
                    """
                    UPDATE c
                        SET 
                            c.PUBLIKATIONSSTATUS = 'veröffentlicht',
                            c.PUBLIKATIONSDATUM = GETDATE(),
                            c.GESAMTCODE_EXPORTIERT = 'Ja'
                        FROM 
                            '{{ 'pipe_HDB' | pipe_table_name }}' a
                        JOIN 
                            '{{ '#hash_HDB' | pipe_table_name }}' b
                        ON
                            b.GESAMTCODE = a.GESAMTCODE
                        AND
                            b.hash = a.hash
                        JOIN 
                            '{{ 'HDB' | table_name }}' c
                        ON
                            c.GESAMTCODE = a.GESAMTCODE
                        AND
                            c.RECORDSTATUS = 0
                        AND
                            c.CUBEID <> ''
                        JOIN 
                            Diffusionsereignisse d 
                        ON 
                            c.DiffusionsID = d.id
                        WHERE 
                            COALESCE(d.StartDate, '') <= GETDATE()
                    """,
                )
                cursor.execute(query)
                self.logger.info("done")

                connection.commit()

    def _calculate_observation_hashes(self, environment: Environment, suffix):
        with environment.get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(BaseSQLStep.render_sql(
                    environment,
                    """
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{{ 'pipe_HDB' | pipe_table_name }}'
                      AND TABLE_SCHEMA = 'dbo'
                      AND COLUMN_NAME NOT IN ('hash')
                    """,
                ))
                columns = cursor.fetchall()
                column_names = [column["COLUMN_NAME"] for column in columns]
                concat_expression = " + ".join(
                    [
                        f"CONVERT(VARCHAR(MAX),ISNULL({column}, ''))"
                        for column in column_names
                    ]
                )
                query = BaseSQLStep.render_sql(
                    environment,
                    f"""
                UPDATE
                    '{{ 'pipe_HDB' | pipe_table_name }}'
                SET
                    hash = HASHBYTES('MD5', CONVERT(VARBINARY(MAX), {concat_expression}))
                """,
                )
                cursor.execute(query)
                connection.commit()
