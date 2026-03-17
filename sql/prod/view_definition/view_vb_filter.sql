DROP VIEW IF EXISTS dbo.view_vb_filter;
GO

CREATE VIEW dbo.view_vb_filter AS
SELECT
    t.SASA_Job_Output_Id AS view_id,
    SUBSTRING(value, CHARINDEX('|', value) + 1, LEN(value)) AS termset,
    SUBSTRING(value, 1, CHARINDEX('|', value) - 1) AS dimension
FROM
    dbo.pipe_HDBDatenobjekte_FINAL t
CROSS APPLY STRING_SPLIT(t.DimensionFilter, ';')
WHERE CHARINDEX('|', value) > 0 

UNION ALL

SELECT
    t.SASA_Job_Output_Id AS view_id,
    t.RaumFilter AS termset,
    'Raum' AS dimension
FROM
    dbo.pipe_HDBDatenobjekte_FINAL t

union all

SELECT
    t.SASA_Job_Output_Id AS view_id,
    value AS termset,
    'Zeit' AS dimension
FROM
    dbo.pipe_HDBDatenobjekte_FINAL t
CROSS APPLY STRING_SPLIT(t.Zeit_Hierarchie, '|')
WHERE CHARINDEX('|', t.Zeit_Hierarchie) > 0;
