DROP VIEW IF EXISTS dbo.view_property;

GO

CREATE VIEW dbo.view_property AS
SELECT DISTINCT
	t.GRUPPE AS property_code,
	t.GRUPPENNAME AS title
FROM
	dbo.pipe_HDBGruppenliste t;
