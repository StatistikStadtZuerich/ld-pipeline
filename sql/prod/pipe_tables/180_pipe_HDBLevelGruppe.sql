DROP TABLE IF EXISTS [dbo].[pipe_HDBLevelGruppe_prod];

GO

SELECT
    LevelID,
    Levelbeschreibung,
    Levelname
INTO [dbo].[pipe_HDBLevelGruppe_prod]
FROM [dbo].[HDBLevelGruppe];