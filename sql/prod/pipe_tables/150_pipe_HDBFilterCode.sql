DROP TABLE IF EXISTS [dbo].[pipe_HDBFilterCode_prod];

GO

SELECT
    Gruppe,
    Gruppencode,
    Gruppencodename,
    FilterId
INTO [dbo].[pipe_HDBFilterCode_prod]
FROM [dbo].[HDBFilterCode];