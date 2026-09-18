DROP TABLE IF EXISTS [dbo].[pipe_HDBLevelCode_prod];

GO

SELECT
    Gruppe,
    Gruppencode,
    Gruppencodename,
    LevelId,
    ParentLevelId,
    Parentcode
INTO [dbo].[pipe_HDBLevelCode_prod]
FROM [dbo].[HDBLevelCode];