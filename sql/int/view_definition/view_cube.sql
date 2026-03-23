DROP VIEW IF EXISTS dbo.view_cube_int;

GO

CREATE VIEW dbo.view_cube_int AS
SELECT
	t.cube_id,
	d.titel AS title
FROM
	dbo.pipe_HDBCubeDefinition d
JOIN
	(SELECT
	    REPLACE(VALUE, 'CID_', '') AS cube_id
	FROM
	    (
			SELECT
				h.CUBEID
			FROM
				dbo.pipe_HDB_TEST h
			WHERE h.RECORDSTATUS = '0'
		) AS t
	CROSS APPLY
	    STRING_SPLIT(t.CUBEID, ' ')
	WHERE
	    TRIM(VALUE) <> ''
	GROUP BY
		REPLACE(VALUE, 'CID_', '')) t
ON
	CONCAT('CID_', t.cube_id) = d.CID;
