DROP VIEW IF EXISTS dbo.view_hierarchy_int;

GO

CREATE VIEW dbo.view_hierarchy_int AS
SELECT DISTINCT
    t.GRUPPE AS term_group_code,

    UPPER(REPLACE(t.GRUPPENCODE, '-', '')) AS term,

    t.GRUPPENNAME AS name
    
FROM
    dbo.pipe_HDBGruppenliste t
WHERE
    t.GRUPPE = t.ORIGIN;
