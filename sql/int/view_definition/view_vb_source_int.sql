DROP VIEW IF EXISTS dbo.view_vb_source_int;
GO

CREATE VIEW dbo.view_vb_source_int AS
SELECT
	t.view_id,
	t.cube_id,
	c.Titel as name
FROM
	dbo.pipe_HDBCubeDefinition c
JOIN
	(SELECT
		t.SASA_Job_output_id AS view_id,
		REPLACE(LTRIM(RTRIM(value)), 'CID_', '') AS cube_id
	FROM
		pipe_HDBDatenobjekte_TEST t
	CROSS APPLY
		STRING_SPLIT(t.CubeIDs, ' ')) AS t
ON
	t.cube_id = REPLACE(c.CID, 'CID_', '');
