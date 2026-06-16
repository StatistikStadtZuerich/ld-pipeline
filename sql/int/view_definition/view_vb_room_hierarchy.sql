DROP VIEW IF EXISTS [dbo].[view_vb_room_hierarchy_int];
GO

CREATE VIEW [dbo].[view_vb_room_hierarchy_int] AS

SELECT
    SASA_Job_Output_Id AS view_id,
    value AS termset,
    SUBSTRING(value, 2, 3) AS dimension
FROM
    [dbo].[pipe_HDBDatenobjekte_int]
CROSS APPLY STRING_SPLIT(HierarchieID_List, ';')

UNION ALL

SELECT
	t.SASA_Job_Output_Id AS view_id,
	value as termset,
	'RAUM' as dimension
FROM
	[dbo].[pipe_HDBDatenobjekte_int] t
CROSS APPLY STRING_SPLIT(t.Raum_Hierarchie, ';')
;
