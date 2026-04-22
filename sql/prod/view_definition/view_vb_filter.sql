DROP VIEW IF EXISTS [dbo].[view_vb_filter];
GO

CREATE VIEW [dbo].[view_vb_filter] AS
SELECT
    t.SASA_Job_Output_Id AS view_id,
    value AS termset,
    SUBSTRING(value, 2, 3) AS dimension
FROM
    [dbo].[pipe_HDBDatenobjekte_int] t
CROSS APPLY STRING_SPLIT(t.DimensionFilterID, ';')

UNION ALL

SELECT
    t.SASA_Job_Output_Id AS view_id,
    t.RaumFilter AS termset,
    'RAUM' AS dimension
FROM
    [dbo].[pipe_HDBDatenobjekte_prod] t

union all

SELECT
    t.SASA_Job_Output_Id AS view_id,
    value AS termset,
    'Zeit' AS dimension
FROM
    [dbo].[pipe_HDBDatenobjekte_prod] t
CROSS APPLY STRING_SPLIT(t.Zeit_Hierarchie, '|')
WHERE CHARINDEX('|', t.Zeit_Hierarchie) > 0;
