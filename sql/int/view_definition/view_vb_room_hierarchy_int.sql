DROP VIEW IF EXISTS dbo.view_vb_room_hierarchy_int;
GO

CREATE VIEW dbo.view_vb_room_hierarchy_int AS
WITH RankedTermsets AS (
    SELECT
        t.SASA_Job_Output_Id AS view_id,
        value AS termset,
        'Raum' AS dimension,
        CASE
            WHEN value = 'StadtZH' THEN 1
            WHEN value = 'KreiseZH' THEN 2
            WHEN value = 'QuartiereZH' THEN 3
            ELSE 4
        END AS termset_rank,
        ROW_NUMBER() OVER (PARTITION BY t.SASA_Job_Output_Id ORDER BY 
        CASE
            WHEN value = 'StadtZH' THEN 1
            WHEN value = 'KreiseZH' THEN 2
            WHEN value = 'QuartiereZH' THEN 3
            ELSE 4
        END) AS rn
    FROM
        pipe_HDBDatenobjekte_TEST t
    CROSS APPLY STRING_SPLIT(t.Raum_Hierarchie, ';')
)
SELECT
    view_id,
    termset,
    dimension
FROM
    RankedTermsets
WHERE
    rn = 1;
