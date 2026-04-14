DROP TABLE IF EXISTS [dbo].[pipe_HDBHierarchien_int];

GO

SELECT
    GRUPPE,
    HIERARCHIE,
    DWHName,
    Beschreibung,
    SprechenderFeldname,
    Reihenfolge
INTO [dbo].[pipe_HDBHierarchien_int]
FROM [dbo].[HDBHierarchien];