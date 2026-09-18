DROP VIEW IF EXISTS [dbo].[view_dimension_hierarchy];

GO

CREATE VIEW [dbo].[view_dimension_hierarchy] AS
    SELECT
        Gruppencode AS child_code,
        PARENTCODE AS parent_code,
        ParentLevelId AS hierarchie_relation
    FROM [dbo].[pipe_HDBLevelCode_prod]
;