DROP TABLE IF EXISTS [dbo].[pipe_HDBAbgeleiteteGruppen_prod];

SELECT
    GRUPPE,
    ORIGIN
INTO [dbo].[pipe_HDBAbgeleiteteGruppen_prod]
FROM [dbo].[HDBAbgeleiteteGruppen];