DROP TABLE IF EXISTS [dbo].[pipe_HDBCodeliste_int];

GO

SELECT
    CODE,
    CODENAME,
    REFERENZTABELLE,
    "Index"
INTO [dbo].[pipe_HDBCodeliste_int]
FROM [dbo].[HDBCodeliste];