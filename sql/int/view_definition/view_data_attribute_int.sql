DROP VIEW IF EXISTS dbo.view_data_attribute_int;
GO
DROP VIEW IF EXISTS dbo.view_data_attribute_int_old;

GO

CREATE VIEW dbo.view_data_attribute_int_old AS
SELECT
	CAST(t.id AS VARCHAR) AS attribute_id,
	t."Sprechender Feldname" AS name,
	t.Feldbeschreibung AS description,
	t."Technischer Feldname" AS alternate_name,
	ISNULL(STRING_AGG(a.DatenobjektID, ','), '') AS object_id_set
FROM
	dbo.pipe_HDBDatenattribute_TEST t
LEFT JOIN
	dbo.pipe_HDBDatenattributeObjekte_TEST a
ON
	a.DatenattributID = t.id
GROUP BY
	t.id,
	t."Sprechender Feldname",
	t.Feldbeschreibung,
	t."Technischer Feldname";
