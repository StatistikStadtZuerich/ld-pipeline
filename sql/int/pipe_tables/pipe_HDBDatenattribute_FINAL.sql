DROP TABLE IF EXISTS dbo.pipe_HDBDatenattribute_FINAL;

GO

SELECT
    id,
    SASA_OutputsId,
    Title,
    Feldbeschreibung,
    "Sprechender Feldname",
    "Technischer Feldname"
INTO dbo.pipe_HDBDatenattribute_FINAL
FROM dbo.HDBDatenattribute_FINAL;