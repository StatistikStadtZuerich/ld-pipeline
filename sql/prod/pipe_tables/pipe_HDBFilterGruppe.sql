DROP TABLE IF EXISTS [dbo].[pipe_HDBFilterGruppe_prod];

GO

SELECT
    FilterID,
    Filterbeschreibung,
    Filtername
INTO [dbo].[pipe_HDBFilterGruppe_prod]
FROM [dbo].[HDBFilterGruppe];