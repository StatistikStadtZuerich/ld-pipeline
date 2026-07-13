DROP VIEW IF EXISTS [dbo].[view_group_termset_int];

GO

CREATE VIEW [dbo].[view_group_termset_int] AS

SELECT DISTINCT
    CASE 
        WHEN ag.gruppe IS NOT NULL THEN REPLACE(t.GRUPPENCODE, ag.gruppe, ag.origin)
        ELSE t.GRUPPENCODE
    END AS term_code,
  
    REPLACE(value, ' ', '') AS term_set_name,
    h.HierarchieID AS term_set
 
FROM [dbo].[pipe_HDBGruppenliste_int] t
CROSS APPLY STRING_SPLIT(t.HIERARCHIE, ';')
LEFT JOIN [dbo].[pipe_HDBAbgeleiteteGruppen_int] ag
    ON LEFT(t.GRUPPENCODE, 3) = ag.gruppe
    OR LEFT(t.GRUPPE, 3) = ag.gruppe
    OR LEFT(t.PARENTCODE, 3) = ag.gruppe
LEFT JOIN [dbo].[pipe_HDBHierarchien_int] h
	on value = h.HIERARCHIE and left(t.Gruppencode,3) = SUBSTRING(h.HierarchieID, 2, 3)
    ;
