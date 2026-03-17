DROP VIEW IF EXISTS dbo.view_dimension_hierarchy;

GO

CREATE VIEW dbo.view_dimension_hierarchy AS
WITH rekursiv AS (
    SELECT 
        GRUPPENCODE,
        PARENTCODE,
        CAST(NULL AS VARCHAR(MAX)) AS Pfad,
        CAST(GRUPPENCODE AS VARCHAR(MAX)) AS besuchte_codes,
        0 AS Tiefe
    FROM pipe_HDBGruppenliste

    UNION ALL

    SELECT 
        r.GRUPPENCODE,
        p.PARENTCODE,
        CAST(
            CASE WHEN r.Pfad IS NULL THEN p.GRUPPENCODE
                 ELSE p.GRUPPENCODE + ', ' + r.Pfad 
            END
        AS VARCHAR(MAX)),
        CAST(r.besuchte_codes + ',' + p.GRUPPENCODE AS VARCHAR(MAX)),
        r.Tiefe + 1
    FROM rekursiv r
    JOIN pipe_HDBGruppenliste p
        ON p.GRUPPENCODE = r.PARENTCODE
    WHERE r.PARENTCODE IS NOT NULL
    AND r.besuchte_codes NOT LIKE '%' + p.GRUPPENCODE + '%'
    AND r.Tiefe < 25
)
SELECT 
    GRUPPENCODE as child_code,
    Pfad as parent_code
FROM rekursiv
WHERE PARENTCODE IS NULL
    AND Pfad IS NOT NULL
;