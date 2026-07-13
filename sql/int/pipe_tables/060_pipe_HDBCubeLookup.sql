DROP TABLE IF EXISTS [dbo].[pipe_HDBCubeLookup_int];

SELECT
    CID,
    CubeLookupKennzahl,
    CubeLookupDimension
INTO [dbo].[pipe_HDBCubeLookup_int]
FROM [dbo].[HDBCubeLookup];