DROP VIEW IF EXISTS dbo.view_room_int;

GO

CREATE VIEW dbo.view_room_int AS
SELECT
    t.Raum AS term_code,
    t.RaumLang AS title,
    t.RaumParent AS raum_parent,
    t.RaumParentLang AS raum_parent_lang,
    t.WikidataURI AS same_as,
    t.Beschreibung AS description,
    t.GueltigkeitsbereicheID AS available,
    t.RaumSort AS position
FROM
	dbo.pipe_HDBRaum t;
