DROP TABLE IF EXISTS dbo.pipe_HDBHierarchien;

SELECT
    GRUPPE,
    HIERARCHIE,
    DWHName,
    Beschreibung,
    SprechenderFeldname,
    Reihenfolge
INTO dbo.pipe_HDBHierarchien
FROM dbo.HDBHierarchien;