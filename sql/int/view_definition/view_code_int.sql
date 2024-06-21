DROP VIEW IF EXISTS dbo.view_code_int;

GO

CREATE VIEW dbo.view_code_int AS
SELECT
	t.CODE AS term_code,
	t.CODENAME AS title,
	t.REFERENZTABELLE AS term_group_code
FROM
	dbo.pipe_HDBCodeliste t;
