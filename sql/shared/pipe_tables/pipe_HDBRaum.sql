DROP TABLE IF EXISTS dbo.pipe_HDBRaum;

GO

SELECT
    r.RAUM,
    r.RAUMLANG,
    r.RAUMPARENT,
    r.RAUMPARENTLANG,
    r.WIKIDATAURI,
    r.BESCHREIBUNG,
    r.GUELTIGKEITSBEREICHEID,
    r.RAUMSORT,
    r.RAUMHIERARCHIE,
    CASE 
        WHEN r.GUELTIGKEITSBEREICHEID IN ('alle', 'keine')
             OR r.GUELTIGKEITSBEREICHEID IS NULL
        THEN NULL
        WHEN LEFT(r.GUELTIGKEITSBEREICHEID,4) LIKE '[0-9][0-9][0-9][0-9]'
        THEN DATEFROMPARTS(CAST(LEFT(r.GUELTIGKEITSBEREICHEID,4) AS int), 1,1)
        ELSE NULL
    END AS GueltigVon,
    CASE 
        WHEN r.GUELTIGKEITSBEREICHEID IN ('alle', 'keine')
             OR r.GUELTIGKEITSBEREICHEID IS NULL
        THEN NULL
        WHEN CHARINDEX('heute', r.GUELTIGKEITSBEREICHEID) > 0
        THEN CAST('9999-12-31' AS date)
        WHEN RIGHT(r.GUELTIGKEITSBEREICHEID,4) LIKE '[0-9][0-9][0-9][0-9]'
        THEN DATEFROMPARTS(CAST(RIGHT(r.GUELTIGKEITSBEREICHEID,4) AS int), 12,31)
        ELSE NULL
    END AS GueltigBis

INTO dbo.pipe_HDBRaum
FROM dbo.HDBRaum r

UNION ALL

SELECT
    h.LDID    AS RAUM,
    h.Name    AS RAUMLANG,
    h.RaumParent,
    h.RaumParentLang,
    h.WikidataURI,
    h.Beschreibung,
    h.GueltigkeitsbereicheID,
    h.RaumSort,
    h.RaumHierarchie,
    h.GueltigVon,
    h.GueltigBis
FROM dbo.HDBRaumHistorisch h;