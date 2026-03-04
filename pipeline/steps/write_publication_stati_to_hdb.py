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
                cursor.execute(f"""
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'pipe_HDB_{suffix}'
                    AND TABLE_SCHEMA = 'dbo'
                    AND COLUMN_NAME NOT IN ('hash')
                """)
                columns = cursor.fetchall()
                column_names = [column["COLUMN_NAME"] for column in columns]
                concat_expression = " + ".join(
                    [
                        f"CONVERT(VARCHAR(MAX),ISNULL({column}, ''))"
                        for column in column_names
                    ]
                )

                self.logger.info(f"Creating temporary table #hash_HDB_{suffix} ...")
                query = f"""
                    DROP TABLE IF EXISTS #hash_HDB_{suffix};
                    CREATE TABLE #hash_HDB_{suffix} (
                        GESAMTCODE nvarchar(60),
                        hash VARBINARY(16)
                    )
                """
                cursor.execute(query)
                query = f"""
                    INSERT INTO #hash_HDB_{suffix} (GESAMTCODE, hash)
                    SELECT 
                        GESAMTCODE,
                        HASHBYTES('MD5', CONVERT(VARBINARY(MAX), {concat_expression}))
                    FROM
                        HDB_{suffix} h
                    WHERE
                        h.RECORDSTATUS = '0'
                    AND
                        h.CUBEID <> ''
                """
                cursor.execute(query)
                self.logger.info("done")

                self.logger.info(f"Updating publication stati to HDB_{suffix} ...")
                query = f"""
                    UPDATE c
                        SET 
                            c.PUBLIKATIONSSTATUS = 'veröffentlicht',
                            c.PUBLIKATIONSDATUM = GETDATE(),
                            c.GESAMTCODE_EXPORTIERT = 'Ja'
                        FROM 
                            pipe_hdb_{suffix} a
                        JOIN 
                            #hash_HDB_{suffix} b
                        ON
                            b.GESAMTCODE = a.GESAMTCODE
                        AND
                            b.hash = a.hash
                        JOIN 
                            HDB_{suffix} c
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
                """
                cursor.execute(query)
                self.logger.info("done")

                connection.commit()

    def _calculate_observation_hashes(self, environment: Environment, suffix):
        with environment.get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT COLUMN_NAME
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = 'pipe_HDB_{suffix}'
                    AND TABLE_SCHEMA = 'dbo'
                    AND COLUMN_NAME NOT IN ('hash')
                """)
                columns = cursor.fetchall()
                column_names = [column["COLUMN_NAME"] for column in columns]
                concat_expression = " + ".join(
                    [
                        f"CONVERT(VARCHAR(MAX),ISNULL({column}, ''))"
                        for column in column_names
                    ]
                )
                query = f"""
                UPDATE
                    pipe_HDB_{suffix}
                SET
                    hash = HASHBYTES('MD5', CONVERT(VARBINARY(MAX), {concat_expression}))
                """
                cursor.execute(query)
                connection.commit()
