DROP VIEW IF EXISTS [dbo].[view_dimension_hierarchy];

GO

CREATE VIEW [dbo].[view_dimension_hierarchy] AS
    SELECT
        CAST(NULL AS NVARCHAR(255)) AS child_code,
        CAST(NULL AS NVARCHAR(255)) AS parent_code,
        CAST(NULL AS NVARCHAR(255)) AS hierarchie_relation
    WHERE 1=0
;