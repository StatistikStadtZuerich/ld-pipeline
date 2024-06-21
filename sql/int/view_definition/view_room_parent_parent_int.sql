DROP VIEW IF EXISTS dbo.view_room_parent_parent_int;

GO

CREATE VIEW dbo.view_room_parent_parent_int AS
SELECT
	r.term_code,
	h.term_code AS term_code_parent_parent,
	h.hierarchy AS hierarchy_parent_parent
FROM
	dbo.view_room r
JOIN
	dbo.view_room rParent
ON
	rParent.term_code = r.raum_parent
JOIN
	dbo.view_room_hierarchy h
ON
	h.term_code = rParent.raum_parent
WHERE
	r.raum_parent <> '';
