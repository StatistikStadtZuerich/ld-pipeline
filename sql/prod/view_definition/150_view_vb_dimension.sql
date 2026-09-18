DROP VIEW IF EXISTS [dbo].[view_vb_dimension];
GO

CREATE VIEW [dbo].[view_vb_dimension] AS
SELECT DISTINCT
    t.SASA_Job_Output_Id AS view_id,
    h.GRUPPE AS identifier,
    h.Gruppenname AS name,
    h.Gruppenname as description
FROM 
    [dbo].[pipe_HDBDatenobjekte_prod] t
CROSS APPLY 
    STRING_SPLIT(t.HierarchieID_List, ';') AS split_values
JOIN 
    [dbo].[pipe_HDBGruppenliste_prod] h
ON 
    h.GRUPPE = substring(split_values.value,2, 3)
       WHERE t.Dimension_LevelFilter IS NULL

UNION ALL

SELECT DISTINCT
    t.SASA_Job_Output_Id AS view_id,
    h.GRUPPE AS identifier,
    h.Gruppenname AS name,
    h.Gruppenname as description
FROM 
    [dbo].[pipe_HDBDatenobjekte_int] t
CROSS APPLY 
    STRING_SPLIT(t.Dimension_LevelFilter, ';') AS split_values
JOIN 
    [dbo].[pipe_HDBGruppenliste_prod] h
ON 
    h.GRUPPE = substring(split_values.value,1, 3)
    WHERE t.Dimension_LevelFilter IS NOT NULL
;
