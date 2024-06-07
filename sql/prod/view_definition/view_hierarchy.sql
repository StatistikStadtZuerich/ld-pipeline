DROP VIEW IF EXISTS dbo.view_hierarchy;

GO

CREATE VIEW dbo.view_hierarchy AS
SELECT
	t.GRUPPE AS term_group_code,
	REPLACE(t.HIERARCHIE, '-', '') AS term,
	t.HIERARCHIE AS name
FROM
	dbo.pipe_HDBHierarchien t
WHERE
	t.HIERARCHIE <> '';