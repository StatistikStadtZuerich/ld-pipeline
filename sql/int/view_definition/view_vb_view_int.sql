DROP VIEW IF EXISTS dbo.view_vb_view_int;
GO

CREATE VIEW dbo.view_vb_view_int AS
SELECT
	t.SASA_Job_Output_Id AS id,
	t.Titel AS name,
	1 AS include_datenstatus
FROM
	dbo.pipe_HDBDatenobjekte_TEST t;
