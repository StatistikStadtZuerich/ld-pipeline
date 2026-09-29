DROP VIEW IF EXISTS [dbo].[view_vb_room_hierarchy];
GO

CREATE VIEW [dbo].[view_vb_room_hierarchy] AS

SELECT
    SASA_Job_Output_Id AS view_id,
    value AS termset,
    SUBSTRING(value, 2, 3) AS dimension
FROM
    [dbo].[pipe_HDBDatenobjekte_prod]
CROSS APPLY STRING_SPLIT(HierarchieID_List, ';')
WHERE Dimension_LevelFilter IS NULL 

UNION ALL

SELECT
    SASA_Job_Output_Id AS view_id,
    value AS termset,
    SUBSTRING(value, 1, 3) AS dimension
FROM
    [dbo].[pipe_HDBDatenobjekte_prod]
CROSS APPLY STRING_SPLIT(Dimension_LevelFilter, ';')
WHERE Dimension_LevelFilter IS NOT NULL

UNION ALL

SELECT
	t.SASA_Job_Output_Id AS view_id,
	value as termset,
	'RAUM' as dimension
FROM
	[dbo].[pipe_HDBDatenobjekte_prod] t
CROSS APPLY STRING_SPLIT(t.Raum_Hierarchie, ';')
;
