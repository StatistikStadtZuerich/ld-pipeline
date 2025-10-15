DROP TABLE IF EXISTS dbo.pipe_HDBRaum;

SELECT
    Raum,
    RaumLang,
    RaumParent,
    RaumParentLang,
    NULL as wikidataURI,
    Beschreibung,
    GueltigkeitsbereicheID,
    RaumSort,
    RaumHierarchie
INTO dbo.pipe_HDBRaum
FROM dbo.HDBRaum;