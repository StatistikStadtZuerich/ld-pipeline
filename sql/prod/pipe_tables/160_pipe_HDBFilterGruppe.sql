DROP TABLE IF EXISTS [dbo].[pipe_HDBFilter_prod];

GO

SELECT
    FilterID,
    Filterbeschreibung,
    Filtername
INTO [dbo].[pipe_HDBFilter_prod]
FROM [dbo].[HDBFilter];