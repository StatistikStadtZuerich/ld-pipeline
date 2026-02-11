WITH hierarchy AS (
    SELECT  
        r.Gruppe,
		r.GRUPPENCODE,
        case when r.HIERARCHIE LIKE '%Level4Cd%' then r.GRUPPENCODE else PARENTCODE end as PARENTCODE, 
        TRIM(s.value) AS hierarchie,
        CASE 
            WHEN PATINDEX('%[0-9]Cd%', s.value) > 0 
            THEN CAST(SUBSTRING(s.value, PATINDEX('%[0-9]Cd%', s.value), 1) AS INT)
            ELSE NULL
        END AS parent_level,
        CASE 
            WHEN PATINDEX('%[0-9]Cd%', TRIM(s.value)) > 0
            THEN LEFT(TRIM(s.value), PATINDEX('%[0-9]Cd%', TRIM(s.value)) - 1)
            ELSE NULL
        END AS group_level
    FROM HDBGruppenliste r
    CROSS APPLY STRING_SPLIT(r.HIERARCHIE, ';') s
    WHERE s.value LIKE '%EigentuemerLevel%' and r.Gruppe = 'EIG'
        AND PATINDEX('%[0-9]Cd%', s.value) > 0
)
SELECT 
    l4.gruppencode AS r0,
    l4.hierarchie AS f0,
    l3.gruppencode AS r1,
    l3.hierarchie AS f1,
    l2.gruppencode AS r2,
    l2.hierarchie AS f2,
    l1.gruppencode AS r3
FROM hierarchy l4
LEFT JOIN hierarchy l3 ON l3.parentcode = l4.gruppencode 
    AND l3.parent_level = 3 
LEFT JOIN hierarchy l2 ON (l2.parentcode = l3.gruppencode or (l2.parentcode = l4.gruppencode and l2.gruppencode=l3.gruppencode))
    AND l2.parent_level = 2 
LEFT JOIN hierarchy l1 ON (l1.parentcode = l2.gruppencode or (l1.parentcode = l3.gruppencode and l1.gruppencode=l2.gruppencode) or (l1.parentcode = l4.gruppencode and l1.gruppencode=l3.gruppencode))
    AND l1.parent_level = 1 
WHERE l4.parent_level = 4
    AND l1.gruppencode IS NOT NULL
;