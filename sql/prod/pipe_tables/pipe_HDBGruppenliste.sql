DROP TABLE IF EXISTS [dbo].[pipe_HDBGruppenliste_prod];

GO

SELECT
    GRUPPENCODE,
    GRUPPENCODENAME,
    BESCHREIBUNG,
    GRUPPE,
    GRUPPENNAME,
    PARENTCODE,
    GRUPPENCODESORT,
    GLOSSARID,
    LINK,
    HIERARCHIE,
    ORIGIN,
    SAMEAS
INTO [dbo].[pipe_HDBGruppenliste_prod]
FROM [dbo].[HDBGruppenliste];