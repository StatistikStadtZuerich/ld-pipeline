DROP VIEW IF EXISTS dbo.view_room_parent;

GO

CREATE VIEW dbo.view_room_parent AS
SELECT
	r.term_code,
	h.term_code AS term_code_parent,
	h.hierarchy AS hierarchy_parent
FROM
	dbo.view_room r
JOIN
	dbo.view_room_hierarchy h
ON
	h.term_code = r.raum_parent
WHERE
	r.raum_parent <> '';
