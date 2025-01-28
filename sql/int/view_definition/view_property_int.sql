DROP VIEW IF EXISTS dbo.view_property_int;

GO

CREATE VIEW dbo.view_property_int AS
SELECT DISTINCT
	t.GRUPPE AS property_code,
	t.GRUPPENNAME AS title
FROM
	dbo.pipe_HDBGruppenliste t;
