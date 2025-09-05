DROP VIEW IF EXISTS dbo.view_vb_measure_int;
GO

CREATE VIEW dbo.view_vb_measure_int AS
WITH exploded_k AS (
    SELECT
        t.SASA_Job_Output_Id,
        j.[key] + 1 AS rn_k,
        j.value AS kennzahl
    FROM dbo.pipe_HDBDatenobjekte_TEST t
    CROSS APPLY OPENJSON(
        '["' + REPLACE(REPLACE(t.Kennzahl_GGH_STK_BEB, '"', '\"'), ';', '","') + '"]'
    ) j
),
exploded_c AS (
    SELECT
        t.SASA_Job_Output_Id,
        j.[key] + 1 AS rn_c,
        j.value AS cube_id
    FROM dbo.pipe_HDBDatenobjekte_TEST t
    CROSS APPLY OPENJSON(
        '["' + REPLACE(REPLACE(t.CubeIDS, '"', '\"'), ' ', '","') + '"]'
    ) j
),
paired AS (
    SELECT
        k.SASA_Job_Output_Id,
        c.cube_id,
        REPLACE(k.kennzahl, '|', '_') AS identifier_full_raw,
        k.rn_k
    FROM exploded_k k
    JOIN exploded_c c
      ON c.SASA_Job_Output_Id = k.SASA_Job_Output_Id
     AND c.rn_c = k.rn_k
),
trimmed AS (
    SELECT
        SASA_Job_Output_Id AS view_id,
        cube_id,
        identifier_full_raw,
        LEFT(identifier_full_raw,
             LEN(identifier_full_raw) - PATINDEX('%[^_]%', REVERSE(identifier_full_raw)) + 1) AS identifier_full,
        SUBSTRING(
            LEFT(identifier_full_raw,
                 LEN(identifier_full_raw) - PATINDEX('%[^_]%', REVERSE(identifier_full_raw)) + 1),
            1, 3
        ) AS identifier
    FROM paired
),
view_cube AS (
    SELECT
        t.SASA_Job_Output_Id AS view_id,
        j.value AS cube_id
    FROM dbo.pipe_HDBDatenobjekte_TEST t
    CROSS APPLY OPENJSON(
        '["' + REPLACE(REPLACE(t.CubeIDS, '"', '\"'), ' ', '","') + '"]'
    ) j
)
SELECT DISTINCT
    t.view_id,
    t.identifier,
    t.identifier_full,
    REPLACE(t.cube_id, 'CID_', '') AS cube_id,
    k.Kennzahlname AS name,
    k.Beschreibung AS description
FROM trimmed t
JOIN dbo.pipe_HDBKennzahlen k
    ON k.KennzahlCode = t.identifier
JOIN dbo.pipe_HDBCubeDefinition c
    ON c.CID = t.cube_id
JOIN view_cube vc
    ON vc.cube_id = t.cube_id
   AND vc.view_id = t.view_id;
