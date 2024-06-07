DROP VIEW IF EXISTS dbo.view_group_code_hierarchy;

GO

CREATE VIEW dbo.view_group_code_hierarchy AS
SELECT
	t.GRUPPENCODE AS term_code,
	TRIM(REPLACE(REPLACE(REPLACE(s.value, ' ', ''), '%', ''), '-', '')) AS hierarchy,
	t.GLOSSARID AS glossar_id,
	t.BESCHREIBUNG AS description,
	t.GRUPPE AS termset,
	t.PARENTCODE AS part_of,
	t.GRUPPENCODENAME AS name,
	t.GRUPPENCODESORT AS position
FROM
	dbo.pipe_HDBGruppenliste t
CROSS APPLY
	STRING_SPLIT(REPLACE(t.HIERARCHIE, ';', ','), ',') AS s
WHERE
	t.GLOSSARID IS NOT NULL
AND
	t.GLOSSARID <> ''
GROUP BY
	t.GRUPPENCODE,
	TRIM(REPLACE(REPLACE(REPLACE(s.value, ' ', ''), '%', ''), '-', '')),
	t.GLOSSARID,
	t.BESCHREIBUNG,
	t.GRUPPE,
	t.PARENTCODE,
	t.GRUPPENCODENAME,
	t.GRUPPENCODESORT;
