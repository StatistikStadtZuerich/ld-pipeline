DROP VIEW IF EXISTS dbo.view_group_code_int;

GO

CREATE VIEW dbo.view_group_code_int AS

SELECT DISTINCT
    CASE 
        WHEN ag.gruppe IS NOT NULL THEN REPLACE(t.GRUPPENCODE, ag.gruppe, ag.origin)
        ELSE t.GRUPPENCODE
    END AS term_code,
 
    t.GRUPPENCODENAME AS title,
    t.BESCHREIBUNG AS description,
 
    CASE 
        WHEN ag.gruppe IS NOT NULL THEN REPLACE(t.GRUPPE, ag.gruppe, ag.origin)
        ELSE t.GRUPPE
    END AS term_group_code,
 
    t.GRUPPENCODESORT AS position,
    t.GLOSSARID AS glossarid,
 
    CASE 
        WHEN ag.gruppe IS NOT NULL THEN REPLACE(t.PARENTCODE, ag.gruppe, ag.origin)
        ELSE t.PARENTCODE
    END AS part_of,
 
    REPLACE(t.HIERARCHIE, ' ', '') AS term_sets
 
FROM dbo.pipe_HDBGruppenliste t
LEFT JOIN dbo.HDBAbgeleiteteGruppen ag
    ON LEFT(t.GRUPPENCODE, 3) = ag.gruppe
    OR LEFT(t.GRUPPE, 3) = ag.gruppe
    OR LEFT(t.PARENTCODE, 3) = ag.gruppe;
