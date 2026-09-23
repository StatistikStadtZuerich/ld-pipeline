DROP TABLE IF EXISTS [dbo].[pipe_HDBLevelCode_int];

GO

SELECT
    Gruppe,
    Gruppencode,
    Gruppencodename,
    LevelId,
    ParentLevelId,
    Parentcode
INTO [dbo].[pipe_HDBLevelCode_int]
FROM [dbo].[HDBLevelCode];