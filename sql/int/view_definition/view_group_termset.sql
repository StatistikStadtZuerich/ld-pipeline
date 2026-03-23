DROP VIEW IF EXISTS dbo.view_group_termset_int;

GO

CREATE VIEW dbo.view_group_termset_int AS

SELECT DISTINCT
    CASE 
        WHEN ag.gruppe IS NOT NULL THEN REPLACE(t.GRUPPENCODE, ag.gruppe, ag.origin)
        ELSE t.GRUPPENCODE
    END AS term_code,
  
    REPLACE(value, ' ', '') AS term_set_name,
    UPPER(REPLACE(value, ' ', '')) AS term_set
 
FROM dbo.pipe_HDBGruppenliste t
LEFT JOIN dbo.HDBAbgeleiteteGruppen ag
    ON LEFT(t.GRUPPENCODE, 3) = ag.gruppe
    OR LEFT(t.GRUPPE, 3) = ag.gruppe
    OR LEFT(t.PARENTCODE, 3) = ag.gruppe
    CROSS APPLY STRING_SPLIT(t.HIERARCHIE, ';');
