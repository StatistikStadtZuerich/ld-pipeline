DROP VIEW IF EXISTS dbo.view_time_int;

GO

CREATE VIEW dbo.view_time_int AS
SELECT
    t.ZEIT AS term_code,
    ISNULL(CASE
        WHEN t.PERIODEENDE IS NOT NULL THEN
            t.PERIODEENDE
        ELSE CONVERT(VARCHAR, SUBSTRING(t.ZEIT, 6, 4) + '-' + 
                SUBSTRING(t.ZEIT, 4, 2) + '-' +
                SUBSTRING(t.ZEIT, 2, 2))
    END, '') AS "date",
    ISNULL(t.PERIODESTART, '') AS "reference_time",
    ISNULL(t.PERIODESTART, '') AS "start_date",
    ISNULL(t.PERIODEENDE, '') AS "end_date"
FROM
    dbo.pipe_HDBZeit t;
