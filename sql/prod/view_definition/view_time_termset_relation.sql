DROP VIEW IF EXISTS dbo.view_time_termset_relation;

GO

CREATE VIEW dbo.view_time_termset_relation AS
SELECT
    t.ZEIT AS term_code,
    REPLACE(UPPER(trim(value)),'-','') as termset_code,
    trim(value) as termset_name
FROM
    dbo.pipe_HDBZeit t
    CROSS APPLY STRING_SPLIT(t.BEZUGSZEIT, ';');
