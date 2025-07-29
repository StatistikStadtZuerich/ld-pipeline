DROP VIEW IF EXISTS dbo.view_vb_measure_int;
GO

CREATE VIEW dbo.view_vb_measure_int AS
WITH exploded AS (
    SELECT
        t.SASA_Job_Output_Id,
        t.CubeIDS,
        t.Kennzahl_GGH_STK_BEB,
        k.value AS kennzahl,
        c.value AS cube_id,
        ROW_NUMBER() OVER (PARTITION BY t.SASA_Job_Output_Id ORDER BY (SELECT NULL)) AS rn_k,
        ROW_NUMBER() OVER (PARTITION BY t.SASA_Job_Output_Id ORDER BY (SELECT NULL)) AS rn_c
    FROM dbo.pipe_HDBDatenobjekte_TEST t
    CROSS APPLY STRING_SPLIT(t.Kennzahl_GGH_STK_BEB, ';') k
    CROSS APPLY STRING_SPLIT(t.CubeIDS, ' ') c
),
paired AS (
    SELECT
        SASA_Job_Output_Id,
        cube_id,
        REPLACE(kennzahl, '|', '_') AS identifier_full_raw,
        ROW_NUMBER() OVER (PARTITION BY SASA_Job_Output_Id ORDER BY (SELECT NULL)) AS rn
    FROM exploded
    WHERE rn_k = rn_c
),
trimmed AS (
    SELECT
        SASA_Job_Output_Id AS view_id,
        cube_id,
        identifier_full_raw,
        LEFT(identifier_full_raw, LEN(identifier_full_raw) - 
            PATINDEX('%[^_]%', REVERSE(identifier_full_raw)) + 1) AS identifier_full,
        SUBSTRING(
            LEFT(identifier_full_raw, LEN(identifier_full_raw) - 
                PATINDEX('%[^_]%', REVERSE(identifier_full_raw)) + 1),
            1, 3
        ) AS identifier
    FROM paired
),
view_cube AS (
	SELECT
        t.SASA_Job_Output_Id AS view_id,
        value AS cube_id
    FROM dbo.pipe_HDBDatenobjekte_TEST t
    CROSS APPLY STRING_SPLIT(t.CubeIDS, ' ')
)
SELECT DISTINCT
    MAX(t.view_id) AS view_id,
    MAX(t.identifier) AS identifier,
    MAX(t.identifier_full) AS identifier_full,
    MAX(REPLACE(t.cube_id, 'CID_', '')) AS cube_id,
    MAX(k.Kennzahlname) AS name,
    MAX(k.Beschreibung) AS description
FROM trimmed t
JOIN dbo.pipe_HDBKennzahlen k
    ON k.KennzahlCode = t.identifier
JOIN dbo.pipe_HDBCubeDefinition c
    ON c.CID = t.cube_id
JOIN view_cube vc
    ON vc.cube_id = t.cube_id AND vc.view_id = t.view_id
GROUP BY
	t.view_id, t.identifier, t.identifier_full;
