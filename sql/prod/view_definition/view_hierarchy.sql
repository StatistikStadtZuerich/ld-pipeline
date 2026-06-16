DROP VIEW IF EXISTS [dbo].[view_hierarchy];

GO

CREATE VIEW [dbo].[view_hierarchy] AS
SELECT DISTINCT
    t.GRUPPE AS term_group_code,

    UPPER(REPLACE(t.GRUPPENCODE, '-', '')) AS term,

    t.GRUPPENNAME AS name
    
FROM
    [dbo].[pipe_HDBGruppenliste_prod] t
WHERE
    t.GRUPPE = t.ORIGIN;
