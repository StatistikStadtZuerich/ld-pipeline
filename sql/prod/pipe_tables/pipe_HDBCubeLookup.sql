DROP TABLE IF EXISTS [dbo].[pipe_HDBCubeLookup_prod];

SELECT
    CID,
    CubeLookupKennzahl,
    CubeLookupDimension
INTO [dbo].[pipe_HDBCubeLookup_prod]
FROM [dbo].[HDBCubeLookup];