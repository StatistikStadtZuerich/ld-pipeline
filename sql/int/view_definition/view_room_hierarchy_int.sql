DROP VIEW IF EXISTS dbo.view_room_hierarchy_int;
GO
DROP VIEW IF EXISTS dbo.view_room_hierarchy_int_old;

GO

CREATE VIEW dbo.view_room_hierarchy_int AS
SELECT
	c0."Raum" as r0,
	c0.RaumHierarchie as f0,
	c1."Raum" as r1,
	c1.RaumHierarchie as f1,
	c2."Raum" as r2,
	c2.RaumHierarchie as f2,
	c3."Raum" as r3
FROM
	pipe_HDBRaum c0
JOIN
	pipe_HDBRaum c1
ON
	c1."RaumParent" = c0."Raum"
LEFT JOIN
	pipe_HDBRaum c2
ON
	c2."RaumParent" = c1."Raum"
LEFT JOIN
	pipe_HDBRaum c3
ON
	c3."RaumParent" = c2."Raum"
WHERE
	c0."RaumParent" IS NULL;