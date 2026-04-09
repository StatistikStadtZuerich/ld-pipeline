DROP VIEW IF EXISTS dbo.view_vb_room_hierarchy;
GO

CREATE VIEW dbo.view_vb_room_hierarchy AS
SELECT
    SASA_Job_Output_Id AS view_id,
    SUBSTRING(value, CHARINDEX('|', value) + 1, LEN(value)) AS termset,
    SUBSTRING(value, 1, CHARINDEX('|', value) - 1) AS dimension
FROM
    pipe_HDBDatenobjekte_FINAL
CROSS APPLY STRING_SPLIT(Dimension_Hierarchie, ';')
WHERE CHARINDEX('|', value) > 0 

UNION ALL

SELECT
	t.SASA_Job_Output_Id AS view_id,
	value as termset,
	'Raum' as dimension
FROM
	pipe_HDBDatenobjekte_FINAL t
CROSS APPLY STRING_SPLIT(t.Raum_Hierarchie, ';')
;
