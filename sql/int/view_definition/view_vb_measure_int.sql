DROP VIEW IF EXISTS dbo.view_vb_measure_int;
GO

CREATE VIEW dbo.view_vb_measure_int AS
WITH split_kennzahl AS (
    SELECT
        value AS kennzahl,
        ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rownum
    FROM 
        dbo.pipe_HDBDatenobjekte_TEST
    CROSS APPLY 
        STRING_SPLIT(Kennzahl_GGH_STK_BEB, ';')
),
split_cube_id AS (
    SELECT
        value AS cube_id,
        ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rownum
    FROM 
        dbo.pipe_HDBDatenobjekte_TEST
    CROSS APPLY 
        STRING_SPLIT(CubeIDS, ' ')
),
initial_trim AS (
    SELECT 
        split_cube_id.cube_id,
        split_kennzahl.kennzahl,
        REPLACE(split_kennzahl.kennzahl, '|', '_') AS identifier,
        REPLACE(split_kennzahl.kennzahl, '|', '_') AS original_identifier,
        ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS rownum
    FROM 
        split_kennzahl
    JOIN 
        split_cube_id ON split_kennzahl.rownum = split_cube_id.rownum
),
recursive_trim AS (
    SELECT 
        cube_id,
        original_identifier,
        identifier,
        ROW_NUMBER() OVER (PARTITION BY original_identifier ORDER BY rownum) AS iter
    FROM 
        initial_trim
    UNION ALL
    SELECT 
        cube_id,
        original_identifier,
        CASE 
            WHEN RIGHT(identifier, 1) = '_' 
            THEN LEFT(identifier, LEN(identifier) - 1)
            ELSE identifier
        END AS identifier,
        iter + 1
    FROM 
        recursive_trim
    WHERE 
        RIGHT(identifier, 1) = '_'
),
cube_identifier AS (
	SELECT 
		cube_id,
		SUBSTRING(identifier, 1, 3) as identifier,
		identifier as identifier_full
	FROM 
		recursive_trim
	WHERE 
		iter = (SELECT MAX(iter) FROM recursive_trim RT WHERE RT.original_identifier = recursive_trim.original_identifier)
),
view_cube AS (
	SELECT
        t.sasa_job_output_id AS view_id,
        value AS cube_id
    FROM
        dbo.pipe_HDBDatenobjekte_TEST t
        CROSS APPLY STRING_SPLIT(t.cubeids, ' ')
)
SELECT
	vc.view_id,
	t.identifier,
	t.identifier_full,
	REPLACE(t.cube_id, 'CID_', '') AS cube_id,
	c.Titel as name,
	k.Beschreibung as description
FROM
	cube_identifier t
JOIN
	dbo.pipe_HDBCubeDefinition c
ON
	c.CID = t.cube_id
JOIN
	dbo.pipe_HDBKennzahlen k
ON
	k.KennzahlCode = t.identifier
JOIN
	view_cube vc
ON
	vc.cube_id = t.cube_id;

