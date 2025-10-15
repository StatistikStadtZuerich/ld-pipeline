DROP TABLE IF EXISTS dbo.pipe_HDBDatenattribute_TEST;

SELECT
    id,
    SASA_OutputsId,
    Title,
    Feldbeschreibung,
    "Sprechender Feldname",
    "Technischer Feldname"
INTO dbo.pipe_HDBDatenattribute_TEST
FROM dbo.HDBDatenattribute_TEST;