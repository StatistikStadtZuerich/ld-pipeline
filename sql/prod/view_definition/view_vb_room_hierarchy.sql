DROP VIEW IF EXISTS dbo.view_vb_room_hierarchy;
GO

CREATE VIEW dbo.view_vb_room_hierarchy AS
SELECT
	t.SASA_Job_Output_Id AS view_id,
	value as termset,
	'Raum' as dimension
FROM
	pipe_HDBDatenobjekte_FINAL t
CROSS APPLY STRING_SPLIT(t.Raum_Hierarchie, ';')
;
