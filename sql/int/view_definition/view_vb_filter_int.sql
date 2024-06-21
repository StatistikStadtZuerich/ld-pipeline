DROP VIEW IF EXISTS dbo.view_vb_filter_int;
GO

CREATE VIEW dbo.view_vb_filter_int AS
SELECT
    t.SASA_Job_Output_Id as view_id,
    value as termset,
	CASE
		WHEN value IN ('Jahr', 'Quartal') THEN 'ZEIT'
		ELSE 'RAUM'
	END as dimension
FROM
    pipe_HDBDatenobjekte_TEST t
CROSS APPLY STRING_SPLIT(t.Filter, ' ');
