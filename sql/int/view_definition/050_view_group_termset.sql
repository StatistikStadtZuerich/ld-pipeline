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
	on RTRIM(LTRIM(value)) = RTRIM(LTRIM(h.HIERARCHIE))
    and left(t.Gruppencode,3) = SUBSTRING(h.HierarchieID, 2, 3)

UNION ALL 

SELECT 
    F.Gruppencode as term_code, 
    G.FilterName as term_set_name, 
    F.FilterID as term_set
    
FROM [dbo].[pipe_HDBFilterCode_int] as F
LEFT JOIN [dbo].[pipe_HDBFilterGruppe_int] as G
ON F.FilterID = G.FilterID

UNION ALL 

SELECT DISTINCT
    L.Gruppencode as term_code,  
    G.LevelName as term_set_name, 
    L.LevelID as term_set
    
FROM [dbo].[HDBLevelCode] as L
LEFT JOIN [dbo].[HDBLevelGruppe] as G
ON G.LevelID = L.LevelID
;
    
