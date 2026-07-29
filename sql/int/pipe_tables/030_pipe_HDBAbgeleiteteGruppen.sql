DROP TABLE IF EXISTS [dbo].[pipe_HDBAbgeleiteteGruppen_int];

SELECT
    GRUPPE,
    ORIGIN
INTO [dbo].[pipe_HDBAbgeleiteteGruppen_int]
FROM [dbo].[HDBAbgeleiteteGruppen];