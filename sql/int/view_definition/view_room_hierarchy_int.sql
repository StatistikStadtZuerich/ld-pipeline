DROP VIEW IF EXISTS dbo.view_room_hierarchy_int;

GO

CREATE VIEW dbo.view_room_hierarchy_int AS
SELECT
    t.Raum AS term_code,
    TRIM(REPLACE(REPLACE(REPLACE(s.value, ' ', ''), '%', ''), '-', '')) AS hierarchy
FROM
	dbo.pipe_HDBRaum t
CROSS APPLY
	STRING_SPLIT(REPLACE(t.RaumHierarchie, ';', ','), ',') AS s
GROUP BY
    t.Raum,
    s.value;