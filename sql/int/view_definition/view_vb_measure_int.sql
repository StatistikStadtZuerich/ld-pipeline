DROP VIEW IF EXISTS dbo.view_vb_measure_int;
GO

CREATE VIEW dbo.view_vb_measure_int AS
WITH cleaned_source AS (
    SELECT DISTINCT
        t.SASA_Job_Output_Id AS view_id,
        TRIM(j.[value]) + '|' AS raw_value,
        COALESCE(
            (
                SELECT STRING_AGG(val, '|' ) WITHIN GROUP (ORDER BY val)
                FROM (
                    SELECT DISTINCT TRIM(s.[value]) AS val
                    FROM STRING_SPLIT(REPLACE(ISNULL(t.Dimension_Hierarchie,'XXX'), ';', '|'), '|') s
                    WHERE TRIM(s.[value]) <> '' AND LEN(TRIM(s.[value])) <= 3
                ) AS vals
            ),
            'XXX'
        ) + '|' AS Cleaned_Dimension_Hierarchie
    FROM dbo.pipe_HDBDatenobjekte_TEST t
    CROSS APPLY OPENJSON(
        '["' + REPLACE(REPLACE(t.Kennzahl_GGH_STK_BEB, '"','\"'), ';','","') + '"]'
    ) AS j
),
cleaned_lookup AS (
    SELECT DISTINCT
        h.CID,
        h.CubeLookupKennzahl,
        h.CubeLookupDimension,
        CASE
            WHEN RIGHT(TRIM(h.CubeLookupKennzahl),1)='|' THEN TRIM(h.CubeLookupKennzahl)
            ELSE TRIM(h.CubeLookupKennzahl)+'|'
        END AS CubeLookupKennzahlNorm,
        COALESCE(
            (
                SELECT STRING_AGG(val, '|' ) WITHIN GROUP (ORDER BY val)
                FROM (
                    SELECT DISTINCT TRIM(s.[value]) AS val
                    FROM STRING_SPLIT(REPLACE(ISNULL(h.CubeLookupDimension,''), ';', '|'), '|') s
                    WHERE TRIM(s.[value]) <> '' AND LEN(TRIM(s.[value])) <= 3
                ) AS vals
            ),
            'XXX'
        ) + '|' AS Cleaned_CubeLookupDimension
    FROM dbo.HDBCubeLookup h
)
SELECT
    cs.view_id,
    LEFT(cs.raw_value, 3) AS identifier,
    REPLACE(REPLACE(REPLACE(REPLACE(cs.raw_value, '||||', ''), '|||', ''), '||', ''), '|', '_') AS identifier_full,
    REPLACE(cl.CID,'CID_','') AS cube_id,
    c.Titel AS name,
    h.Beschreibung AS description
FROM cleaned_source cs
JOIN cleaned_lookup cl
    ON cs.raw_value = cl.CubeLookupKennzahlNorm
   AND cs.Cleaned_Dimension_Hierarchie = cl.Cleaned_CubeLookupDimension
JOIN dbo.pipe_HDBCubeDefinition c
    ON c.Kennzahl = LEFT(cs.raw_value, 3)
   AND c.CID = cl.CID
JOIN dbo.pipe_HDBKennzahlen h
    ON h.KennzahlCode = LEFT(cs.raw_value, 3)
JOIN dbo.view_vb_source_INT s
    ON s.view_id = cs.view_id
   AND s.cube_id = REPLACE(cl.CID,'CID_','');
