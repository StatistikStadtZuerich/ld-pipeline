DROP TABLE IF EXISTS [dbo].[pipe_HDBCubeKZLookup_int];

GO

SELECT
    id,
    Cubeids,
    Kennzahl,
    BEB,
    GGH, 
    STK
INTO [dbo].[pipe_HDBCubeKZLookup_int]
FROM [dbo].[HDBCubeKZLookup];