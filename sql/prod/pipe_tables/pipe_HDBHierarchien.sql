
DROP TABLE IF EXISTS [dbo].[pipe_HDBHierarchien_prod];

GO

SELECT
    GRUPPE,
    HIERARCHIE,
    DWHName,
    Beschreibung,
    SprechenderFeldname,
    Reihenfolge,
    HierarchieID
INTO [dbo].[pipe_HDBHierarchien_prod]
FROM [dbo].[HDBHierarchien];