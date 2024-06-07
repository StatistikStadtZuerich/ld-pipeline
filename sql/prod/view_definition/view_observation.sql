DROP VIEW IF EXISTS dbo.view_observation;

GO

CREATE VIEW dbo.view_observation
AS
SELECT
    t.gesamtcode,
    REPLACE(VALUE, 'CID_', '') AS cube_id,
    REPLACE(REPLACE(TRIM(REPLACE(t.CUBEID, VALUE, '')), ' ', ','), 'CID_', '') AS same_as,
    t.kennzahl AS measure,
    t.wert AS value,
    t.zeit_code AS time_code,
    t.zeit_wert AS "time",
    t.raum_code AS room_code,
    t.prop1_code_short,
    t.prop1_code,
    t.prop2_code_short,
    t.prop2_code,
    t.prop3_code_short,
    t.prop3_code,
    t.prop4_code_short,
    t.prop4_code,
    t.prop5_code_short,
    t.prop5_code,
    t.number_groups,
    t.status
FROM
    (
        SELECT
            h.GESAMTCODE AS gesamtcode,
            h.CUBEID,
            h.KENNZAHL AS kennzahl,
            h.WERT AS wert,
            SUBSTRING(h.GESAMTCODE, 1, 9) AS zeit_code,
            CASE
                WHEN SUBSTRING(h.GESAMTCODE, 1, 9) LIKE 'ZP%' THEN
                    CONVERT(VARCHAR, EOMONTH(
                        CAST(
                            '01-' + 
                            CASE 
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'JAN' THEN 'JAN' 
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'FEB' THEN 'FEB'
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'MRZ' THEN 'MAR'
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'APR' THEN 'APR'
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'MAI' THEN 'MAY'
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'JUN' THEN 'JUN'
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'JUL' THEN 'JUL'
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'AUG' THEN 'AUG'
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'SEP' THEN 'SEP'
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'OKT' THEN 'OCT'
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'NOV' THEN 'NOV'
                                WHEN SUBSTRING(h.GESAMTCODE, 3, 3) = 'DEZ' THEN 'DEC'
                            END + 
                            '-' + 
                            SUBSTRING(h.GESAMTCODE, 6, 4) AS DATE
                        )
                    ))
                ELSE CONVERT(VARCHAR, SUBSTRING(h.GESAMTCODE, 6, 4) + '-' + 
                        SUBSTRING(h.GESAMTCODE, 4, 2) + '-' +
                        SUBSTRING(h.GESAMTCODE, 2, 2))
             END AS zeit_wert,
            SUBSTRING(h.GESAMTCODE, 10, 6) AS raum_code,
            SUBSTRING(h.GESAMTCODE, 19, 3) AS prop1_code_short,
            SUBSTRING(h.GESAMTCODE, 19, 7) AS prop1_code,
            SUBSTRING(h.GESAMTCODE, 26, 3) AS prop2_code_short,
            SUBSTRING(h.GESAMTCODE, 26, 7) AS prop2_code,
            SUBSTRING(h.GESAMTCODE, 33, 3) AS prop3_code_short,
            SUBSTRING(h.GESAMTCODE, 33, 7) AS prop3_code,
            SUBSTRING(h.GESAMTCODE, 40, 3) AS prop4_code_short,
            SUBSTRING(h.GESAMTCODE, 40, 7) AS prop4_code,
            SUBSTRING(h.GESAMTCODE, 47, 3) AS prop5_code_short,
            SUBSTRING(h.GESAMTCODE, 47, 7) AS prop5_code,
            h.ANZ_GRUPPEN AS number_groups,
            CASE
                WHEN h.DATENSTATUS LIKE '%veröffentlicht%' THEN 'VEROEFFENTLICHT'
                WHEN h.DATENSTATUS LIKE '%definitiv%' THEN 'DEFINITIV'
                ELSE 'PROVISORISCH'
            END as status
        FROM
            dbo.pipe_HDB_FINAL h
        WHERE
            h.RECORDSTATUS = '0'
    ) t
CROSS APPLY
    STRING_SPLIT(t.CUBEID, ' ')
WHERE
    LTRIM(RTRIM(VALUE)) <> ''
GROUP BY
    t.gesamtcode,
    t.CUBEID,
    VALUE,
    t.kennzahl,
    t.wert,
    t.zeit_code,
    t.zeit_wert,
    t.raum_code,
    t.prop1_code_short,
    t.prop1_code,
    t.prop2_code_short,
    t.prop2_code,
    t.prop3_code_short,
    t.prop3_code,
    t.prop4_code_short,
    t.prop4_code,
    t.prop5_code_short,
    t.prop5_code,
    t.CUBEID,
    t.number_groups,
    t.status;
GO
