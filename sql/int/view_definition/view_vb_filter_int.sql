DROP VIEW IF EXISTS dbo.view_vb_filter_int;
GO

CREATE VIEW dbo.view_vb_filter_int AS
SELECT
	t.SASA_Job_Output_Id as view_id,
    value AS termset,
	CASE
		WHEN value = 'Jahr' THEN 'Zeit'
		WHEN value = 'Quartal' THEN 'Zeit'
		WHEN value = 'Monat' THEN 'Zeit'
		WHEN value = 'Tag' THEN 'Zeit'
		ELSE 'Raum'
	END as dimension
FROM
	pipe_HDBDatenobjekte_TEST t
CROSS APPLY STRING_SPLIT(t.Filter, ' ');
