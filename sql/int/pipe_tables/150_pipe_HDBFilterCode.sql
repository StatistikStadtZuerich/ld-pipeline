DROP TABLE IF EXISTS [dbo].[pipe_HDBFilterCode_int];

GO

SELECT
    Gruppe,
    Gruppencode,
    Gruppencodename,
    FilterId
INTO [dbo].[pipe_HDBFilterCode_int]
FROM [dbo].[HDBFilterCode];