DROP VIEW IF EXISTS dbo.view_vb_filter;
GO

CREATE VIEW dbo.view_vb_filter AS
SELECT
	t.SASA_Job_Output_Id as view_id,
    value AS termset,
	CASE
		WHEN value in ('Jahr'
					,'Quartal'
					,'Zeit'
					,'Monat'
					,'Tag'
					,'Periode'
					,'Quartal'
					,'Semester'
					,'Trimester'
					,'Aktuell'
					,'Jahreszeit'
					,'Sommer'
					,'Winter'
					,'Herbst'
					,'Frühling'
		)THEN 'Zeit'
		ELSE 'Raum'
	END as dimension
FROM
	pipe_HDBDatenobjekte_FINAL t
CROSS APPLY STRING_SPLIT(t.Filter, ' ');
