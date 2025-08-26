DROP VIEW IF EXISTS dbo.view_observation_int;

GO

CREATE VIEW dbo.view_observation_int
AS
SELECT
    h.GESAMTCODE AS gesamtcode,
    REPLACE(REPLACE(TRIM(h.CUBEID), 'CID_', ''), ' ', ',') AS cube_ids,
    h.KENNZAHL AS measure,
    h.WERT AS value,
    SUBSTRING(h.GESAMTCODE, 1, 9)  AS time_code,
    FORMAT(DATEFROMPARTS(z.JAHR, z.MONAT, z.TAG), 'dd-MM-yyyy') AS [time],
    SUBSTRING(h.GESAMTCODE, 10, 6) AS room_code,

    -- Property 1
    SUBSTRING(h.GESAMTCODE, 19, 3) AS prop1_code_short,
    CASE 
        WHEN g1.Origin IS NOT NULL 
        THEN g1.Origin + SUBSTRING(h.GESAMTCODE, 22, 4)
        ELSE SUBSTRING(h.GESAMTCODE, 19, 7)
    END AS prop1_code,

    -- Property 2
    SUBSTRING(h.GESAMTCODE, 26, 3) AS prop2_code_short,
    CASE 
        WHEN g2.Origin IS NOT NULL 
        THEN g2.Origin + SUBSTRING(h.GESAMTCODE, 29, 4)
        ELSE SUBSTRING(h.GESAMTCODE, 26, 7)
    END AS prop2_code,

    -- Property 3
    SUBSTRING(h.GESAMTCODE, 33, 3) AS prop3_code_short,
    CASE 
        WHEN g3.Origin IS NOT NULL 
        THEN g3.Origin + SUBSTRING(h.GESAMTCODE, 36, 4)
        ELSE SUBSTRING(h.GESAMTCODE, 33, 7)
    END AS prop3_code,

    -- Property 4
    SUBSTRING(h.GESAMTCODE, 40, 3) AS prop4_code_short,
    CASE 
        WHEN g4.Origin IS NOT NULL 
        THEN g4.Origin + SUBSTRING(h.GESAMTCODE, 43, 4)
        ELSE SUBSTRING(h.GESAMTCODE, 40, 7)
    END AS prop4_code,

    -- Property 5
    SUBSTRING(h.GESAMTCODE, 47, 3) AS prop5_code_short,
    CASE 
        WHEN g5.Origin IS NOT NULL 
        THEN g5.Origin + SUBSTRING(h.GESAMTCODE, 50, 4)
        ELSE SUBSTRING(h.GESAMTCODE, 47, 7)
    END AS prop5_code,

    h.ANZ_GRUPPEN AS number_groups,

    CASE
        WHEN h.DATENSTATUS LIKE '%veröffentlicht%' THEN 'VEROEFFENTLICHT'
        WHEN h.DATENSTATUS LIKE '%definitiv%'     THEN 'DEFINITIV'
        ELSE 'PROVISORISCH'
    END AS status,
    h.REFERENZNUMMER AS reference_number,
    h.DATENSTAND as modified

FROM dbo.pipe_HDB_TEST h
    LEFT JOIN HDBAbgeleiteteGruppen g1 ON g1.Gruppe = SUBSTRING(h.GESAMTCODE, 19, 3)
    LEFT JOIN HDBAbgeleiteteGruppen g2 ON g2.Gruppe = SUBSTRING(h.GESAMTCODE, 26, 3)
    LEFT JOIN HDBAbgeleiteteGruppen g3 ON g3.Gruppe = SUBSTRING(h.GESAMTCODE, 33, 3)
    LEFT JOIN HDBAbgeleiteteGruppen g4 ON g4.Gruppe = SUBSTRING(h.GESAMTCODE, 40, 3)
    LEFT JOIN HDBAbgeleiteteGruppen g5 ON g5.Gruppe = SUBSTRING(h.GESAMTCODE, 47, 3)
    LEFT JOIN HDBZeit z ON z.ZEIT = h.ZEIT
WHERE
    h.RECORDSTATUS = '0';

GO
