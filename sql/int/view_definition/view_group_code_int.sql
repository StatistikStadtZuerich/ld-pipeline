DROP VIEW IF EXISTS dbo.view_group_code_int;

GO

CREATE VIEW dbo.view_group_code_int AS
SELECT
	t.GRUPPENCODE AS term_code,
	t.GRUPPENCODENAME AS title,
	t.BESCHREIBUNG AS description,
	t.GRUPPE AS term_group_code,
	t.GRUPPENCODESORT AS position,
	t.GLOSSARID AS glossarid,
	t.PARENTCODE AS part_of,
	REPLACE(t.HIERARCHIE, ' ', '') AS term_sets
FROM
	dbo.pipe_HDBGruppenliste t;