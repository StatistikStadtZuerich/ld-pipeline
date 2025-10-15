DROP TABLE IF EXISTS dbo.pipe_HDBCubeDefinition;

GO

SELECT
    CID,
    Titel,
    Referenz,
    Kennzahl,
    Gruppe1,
    Gruppe2,
    Gruppe3,
    Gruppe4,
    Gruppe5,
    Gruppe6,
    Gruppe7,
    Gruppe8
INTO dbo.pipe_HDBCubeDefinition
FROM dbo.HDBCubeDefinition;