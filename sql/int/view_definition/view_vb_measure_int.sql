DROP VIEW IF EXISTS dbo.view_vb_measure_int;
GO

CREATE VIEW dbo.view_vb_measure_int AS
WITH split_cube_ids AS (
    SELECT
        t.sasa_job_output_id AS view_id,
        value AS cube_id
    FROM
        pipe_HDBDatenobjekte_TEST t
        CROSS APPLY STRING_SPLIT(t.cubeids, ' ') 
),
split_kennzahlen AS (
    SELECT
        t.sasa_job_output_id AS view_id,
        value AS kennzahl
    FROM
        pipe_HDBDatenobjekte_TEST t
        CROSS APPLY STRING_SPLIT(t.kennzahl_ggh_stk_beb, ';')
)
SELECT
	t.view_id,
	t.identifier,
	CASE
		WHEN RIGHT(t.identifier_full, 2) = '__' THEN LEFT(t.identifier_full, LEN(t.identifier_full) - 2)
		WHEN RIGHT(t.identifier_full, 1) = '_' THEN LEFT(t.identifier_full, LEN(t.identifier_full) - 1)
		ELSE t.identifier_full
	END as identifier_full,
	t.cube_id,
	t.name,
	t.description
FROM
(SELECT
    s1.view_id,
    LEFT(s2.kennzahl, CHARINDEX('|', s2.kennzahl) - 1) AS identifier,
    LEFT(REPLACE(s2.kennzahl, '|', '_'), LEN(REPLACE(s2.kennzahl, '|', '_')) - 1) AS identifier_full,
	REPLACE(s1.cube_id, 'CID_', '') as cube_id,
	c.Titel as name,
	k.Beschreibung as description
FROM
    split_cube_ids s1
JOIN
	split_kennzahlen s2
ON
	s1.view_id = s2.view_id
JOIN
	dbo.pipe_HDBCubeDefinition c
ON
	c.CID = s1.cube_id
JOIN
	dbo.pipe_HDBKennzahlen k
ON
	k.KennzahlCode = LEFT(s2.kennzahl, CHARINDEX('|', s2.kennzahl) - 1)) t;

