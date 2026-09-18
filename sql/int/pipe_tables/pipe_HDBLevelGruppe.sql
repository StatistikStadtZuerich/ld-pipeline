DROP TABLE IF EXISTS [dbo].[pipe_HDBLevelGruppe_int];

GO

SELECT
    LevelID,
    Levelbeschreibung,
    Levelname
INTO [dbo].[pipe_HDBLevelGruppe_int]
FROM [dbo].[HDBLevelGruppe];