DROP VIEW IF EXISTS [dbo].[view_dimension_hierarchy_int];

GO

CREATE VIEW [dbo].[view_dimension_hierarchy_int] AS
    SELECT
        Gruppencode AS child_code,
        PARENTCODE AS parent_code,
        ParentLevelId AS hierarchie_relation
    FROM [dbo].[pipe_HDBLevelCode_int]
;