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
    STRING_SPLIT(t.DIMENSION_Hierarchie, ';') AS split_values
JOIN 
    [dbo].[pipe_HDBGruppenliste_prod] h
ON 
    h.GRUPPE = LEFT(split_values.value, 3)
;
