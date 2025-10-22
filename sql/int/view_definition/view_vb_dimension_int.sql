DROP VIEW IF EXISTS dbo.view_vb_dimension_int;
GO

CREATE VIEW dbo.view_vb_dimension_int AS
SELECT 
    t.SASA_Job_Output_Id AS view_id,
    h.GRUPPE AS identifier,
    STRING_AGG(h.SprechenderFeldname, ' / ') AS name,
    STRING_AGG(h.Beschreibung, ' / ') AS description
FROM 
    pipe_HDBDatenobjekte_TEST t
CROSS APPLY 
    STRING_SPLIT(t.DIMENSION_Hierarchie, ';') AS split_values
JOIN 
    pipe_HDBHierarchien h
ON 
    h.GRUPPE = LEFT(split_values.value, 3)
AND
    h.HIERARCHIE = SUBSTRING(split_values.value, 5, LEN(split_values.value) - 4)
GROUP BY 
    t.SASA_Job_Output_Id, 
    h.GRUPPE;
