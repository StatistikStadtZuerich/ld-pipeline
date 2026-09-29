DROP TABLE IF EXISTS [dbo].[pipe_HDBFilterGruppe_int];

GO

SELECT
    FilterID,
    Filterbeschreibung,
    Filtername
INTO [dbo].[pipe_HDBFilterGruppe_int]
FROM [dbo].[HDBFilterGruppe];