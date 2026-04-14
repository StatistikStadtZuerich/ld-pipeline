DROP VIEW IF EXISTS [dbo].[view_group_termset];

GO

CREATE VIEW [dbo].[view_group_termset] AS

SELECT DISTINCT
    CASE 
        WHEN ag.gruppe IS NOT NULL THEN REPLACE(t.GRUPPENCODE, ag.gruppe, ag.origin)
        ELSE t.GRUPPENCODE
    END AS term_code,
  
    REPLACE(value, ' ', '') AS term_set_name,
    UPPER(REPLACE(REPLACE(value, ' ', ''), '-', '')) AS term_set
 
FROM [dbo].[pipe_HDBGruppenliste_prod] t
LEFT JOIN [dbo].[pipe_HDBAbgeleiteteGruppen_prod] ag
    ON LEFT(t.GRUPPENCODE, 3) = ag.gruppe
    OR LEFT(t.GRUPPE, 3) = ag.gruppe
    OR LEFT(t.PARENTCODE, 3) = ag.gruppe
    CROSS APPLY STRING_SPLIT(t.HIERARCHIE, ';');
