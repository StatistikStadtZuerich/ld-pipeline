DROP VIEW IF EXISTS [dbo].[view_dimension_hierarchy];

GO

CREATE VIEW [dbo].[view_dimension_hierarchy] AS
    SELECT 
        h.GRUPPENCODE as child_code,
        h.PARENTCODE as parent_code,
        TRIM(value) AS hierarchie_relation
    FROM [dbo].[pipe_HDBGruppenliste_prod] h
    JOIN [dbo].[pipe_HDBGruppenliste_prod] p
        ON p.GRUPPENCODE = h.PARENTCODE
        CROSS APPLY STRING_SPLIT(p.HIERARCHIEIDLIST, ';')
;