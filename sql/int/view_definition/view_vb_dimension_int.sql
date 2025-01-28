DROP VIEW IF EXISTS dbo.view_vb_dimension_int;
GO

CREATE VIEW dbo.view_vb_dimension_int AS
SELECT
	t.SASA_Job_Output_Id as view_id,
	LEFT(t.DIMENSION_Hierarchie, 3) as identifier,
	h.SprechenderFeldname as name,
	h.Beschreibung as description
FROM
	pipe_HDBDatenobjekte_TEST t
JOIN
	pipe_HDBHierarchien h
ON
	h.GRUPPE = LEFT(t.DIMENSION_Hierarchie, 3)
AND
	h.HIERARCHIE = RIGHT(t.DIMENSION_Hierarchie, LEN(t.DIMENSION_Hierarchie) - 4);