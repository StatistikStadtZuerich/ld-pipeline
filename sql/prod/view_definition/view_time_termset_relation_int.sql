DROP VIEW IF EXISTS dbo.view_time_termset_relation_int;

GO

CREATE VIEW dbo.view_time_termset_relation_int AS
SELECT
    t.ZEIT AS term_code,
    trim(value) as termset_code
FROM
    dbo.pipe_HDBZeit t
    CROSS APPLY STRING_SPLIT(t.BEZUGSZEIT, ';');
