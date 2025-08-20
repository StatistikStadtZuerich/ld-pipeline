DROP VIEW IF EXISTS dbo.view_observation_int;

GO

CREATE VIEW dbo.view_observation_int
AS
SELECT
	h.GESAMTCODE AS gesamtcode,
	REPLACE(REPLACE(TRIM(h.CUBEID), 'CID_', ''), ' ', ',') as cube_ids,
	h.KENNZAHL AS measure,
	h.WERT AS value,
	SUBSTRING(h.GESAMTCODE, 1, 9) AS time_code,
	SUBSTRING(h.GESAMTCODE, 10, 6) AS room_code,
    SUBSTRING(h.GESAMTCODE, 19, 3) AS prop1_code_short,
    CASE 
        WHEN g1.Origin IS NOT NULL 
        THEN g1.Origin + SUBSTRING(h.GESAMTCODE, 22, 4)
        ELSE SUBSTRING(h.GESAMTCODE, 19, 7)
    END AS prop1_code,
    SUBSTRING(h.GESAMTCODE, 26, 3) AS prop2_code_short,
    CASE 
        WHEN g2.Origin IS NOT NULL 
        THEN g2.Origin + SUBSTRING(h.GESAMTCODE, 29, 4)
        ELSE SUBSTRING(h.GESAMTCODE, 26, 7)
    END AS prop2_code,
    SUBSTRING(h.GESAMTCODE, 33, 3) AS prop3_code_short,
    CASE 
        WHEN g3.Origin IS NOT NULL 
        THEN g3.Origin + SUBSTRING(h.GESAMTCODE, 36, 4)
        ELSE SUBSTRING(h.GESAMTCODE, 33, 7)
    END AS prop3_code,
    SUBSTRING(h.GESAMTCODE, 40, 3) AS prop4_code_short,
    CASE 
        WHEN g4.Origin IS NOT NULL 
        THEN g4.Origin + SUBSTRING(h.GESAMTCODE, 43, 4)
        ELSE SUBSTRING(h.GESAMTCODE, 40, 7)
    END AS prop4_code,
    SUBSTRING(h.GESAMTCODE, 47, 3) AS prop5_code_short,
    CASE 
        WHEN g5.Origin IS NOT NULL 
        THEN g5.Origin + SUBSTRING(h.GESAMTCODE, 50, 4)
        ELSE SUBSTRING(h.GESAMTCODE, 47, 7)
    END AS prop5_code,

	h.ANZ_GRUPPEN AS number_groups,
	CASE
		WHEN h.DATENSTATUS LIKE '%veröffentlicht%' THEN 'VEROEFFENTLICHT'
		WHEN h.DATENSTATUS LIKE '%definitiv%' THEN 'DEFINITIV'
		ELSE 'PROVISORISCH'
	END as status
	
FROM
	dbo.pipe_HDB_TEST h
WHERE
	h.RECORDSTATUS = '0'
AND
	h.CUBEID <> '';
GO
