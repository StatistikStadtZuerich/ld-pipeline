DROP TABLE IF EXISTS dbo.pipe_HDBCodeliste;

SELECT
    CODE,
    CODENAME,
    REFERENZTABELLE,
    "Index"
INTO dbo.pipe_HDBCodeliste
FROM dbo.HDBCodeliste;