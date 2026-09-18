DROP TABLE IF EXISTS [dbo].[pipe_HDBCubeKZLookup_prod];

GO

SELECT
    id,
    Cubeid,
    Kennzahl,
    BEB,
    GGH, 
    STK
INTO [dbo].[pipe_HDBCubeKZLookup_prod]
FROM [dbo].[HDBCubeKZLookup];