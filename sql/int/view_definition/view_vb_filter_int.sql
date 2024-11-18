DROP VIEW IF EXISTS dbo.view_vb_filter_int;
GO

CREATE VIEW dbo.view_vb_filter_int AS
SELECT
	t.SASA_Job_Output_Id as view_id,
	value as termset,
	'Raum' AS dimension
FROM
	pipe_HDBDatenobjekte_TEST t
CROSS APPLY STRING_SPLIT(t.Raum_Hierarchie, ';')
WHERE
	CHARINDEX(value, t.Filter) = 0
UNION ALL
SELECT
	t.SASA_Job_Output_Id as view_id,
	value as termset,
	'Zeit' AS dimension
FROM
	pipe_HDBDatenobjekte_TEST t
CROSS APPLY STRING_SPLIT(t.Zeit_Hierarchie, '|')
WHERE
	CHARINDEX(value, t.Filter) = 0;