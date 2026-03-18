DROP VIEW IF EXISTS dbo.view_hierarchy;

GO

CREATE VIEW dbo.view_hierarchy AS
SELECT DISTINCT
    CASE 
        WHEN ag.gruppe IS NOT NULL THEN REPLACE(t.GRUPPE, ag.gruppe, ag.origin)
        ELSE t.GRUPPE
    END AS term_group_code,

    UPPER(REPLACE(t.HIERARCHIE, '-', '')) AS term

    --t.HIERARCHIE AS name
    
FROM
    dbo.pipe_HDBHierarchien t
    LEFT JOIN dbo.HDBAbgeleiteteGruppen ag
        ON t.GRUPPE = ag.Gruppe
WHERE
    t.HIERARCHIE <> '';
