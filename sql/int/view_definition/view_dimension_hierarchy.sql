DROP VIEW IF EXISTS [dbo].[view_dimension_hierarchy_int];

GO

CREATE VIEW [dbo].[view_dimension_hierarchy_int] AS
    SELECT
        CAST(NULL AS NVARCHAR(255)) AS child_code,
        CAST(NULL AS NVARCHAR(255)) AS parent_code,
        CAST(NULL AS NVARCHAR(255)) AS hierarchie_relation
    WHERE 1=0
;