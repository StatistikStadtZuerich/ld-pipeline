DROP VIEW IF EXISTS dbo.view_vb_measure_int;
GO

CREATE VIEW dbo.view_vb_measure_int AS
WITH exploded_k_raw AS (
    SELECT
        t.SASA_Job_Output_Id AS view_id,
        j.value AS raw_value
    FROM dbo.pipe_HDBDatenobjekte_TEST t
    CROSS APPLY OPENJSON(
        '["' + REPLACE(REPLACE(t.Kennzahl_GGH_STK_BEB, '"', '\"'), ';', '","') + '"]'
    ) j
),
exploded_k AS (
    SELECT
        r.view_id,
        tr.identifier_full_raw
    FROM exploded_k_raw r
    CROSS APPLY ( SELECT REPLACE(r.raw_value, '|', '_') AS replaced ) rr
    CROSS APPLY ( SELECT PATINDEX('%[^_]%', REVERSE(rr.replaced)) AS pos ) p
    CROSS APPLY (
        SELECT
            CASE
                WHEN p.pos = 0 THEN rr.replaced
                ELSE LEFT(rr.replaced, LEN(rr.replaced) - p.pos + 1)
            END AS identifier_full_raw
    ) tr
),
exploded_c AS (
    SELECT
        t.SASA_Job_Output_Id AS view_id,
        j.value AS cube_id
    FROM dbo.pipe_HDBDatenobjekte_TEST t
    CROSS APPLY OPENJSON(
        '["' + REPLACE(REPLACE(t.CubeIDS, '"', '\"'), ' ', '","') + '"]'
    ) j
),
mapped AS (
    SELECT
        k.view_id,
        LEFT(k.identifier_full_raw, 3) AS identifier,
        k.identifier_full_raw AS identifier_full,
        c.CID AS cube_id,
        c.Titel AS name,
        h.Beschreibung AS description
    FROM exploded_k k
    JOIN exploded_c ec
      ON ec.view_id = k.view_id
    JOIN dbo.pipe_HDBCubeDefinition c
      ON c.Kennzahl = LEFT(k.identifier_full_raw, 3)
     AND c.CID = ec.cube_id
    JOIN dbo.pipe_HDBKennzahlen h
      ON h.KennzahlCode = LEFT(k.identifier_full_raw, 3)
),
deduped AS (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY view_id, identifier_full
               ORDER BY cube_id
           ) AS rn
    FROM mapped
)
SELECT
    view_id,
    identifier,
    identifier_full,
    REPLACE(cube_id,'CID_','') AS cube_id,
    name,
    description
FROM deduped
WHERE rn = 1;