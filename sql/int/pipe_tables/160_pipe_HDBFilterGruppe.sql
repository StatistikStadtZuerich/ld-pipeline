DROP TABLE IF EXISTS [dbo].[pipe_HDBFilter_int];

GO

SELECT
    FilterID,
    Filterbeschreibung,
    Filtername
INTO [dbo].[pipe_HDBFilter_int]
FROM [dbo].[HDBFilter];