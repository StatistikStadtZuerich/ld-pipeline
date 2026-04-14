DROP TABLE IF EXISTS [dbo].[pipe_HDBCodeliste_prod];

GO

SELECT
    CODE,
    CODENAME,
    REFERENZTABELLE,
    "Index"
INTO [dbo].[pipe_HDBCodeliste_prod]
FROM [dbo].[HDBCodeliste];