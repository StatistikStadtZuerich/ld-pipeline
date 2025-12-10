DROP TABLE IF EXISTS dbo.pipe_HDBRaum;

GO

SELECT
    Raum,
    RaumLang,
    RaumParent,
    RaumParentLang,
    -- FIXME: warum NULL und nicht die Daten aus der HDBRaum-Tabelle?
    CAST(NULL AS VARCHAR(MAX)) as wikidataURI,
    Beschreibung,
    GueltigkeitsbereicheID,
    RaumSort,
    RaumHierarchie
INTO dbo.pipe_HDBRaum
FROM dbo.HDBRaum;