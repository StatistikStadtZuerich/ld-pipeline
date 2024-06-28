DROP VIEW IF EXISTS dbo.view_vb_room_hierarchy_int;
GO

CREATE VIEW dbo.view_vb_room_hierarchy_int AS
SELECT
    t.SASA_Job_Output_Id as view_id,
    value as termset,
	'Raum' as dimension
FROM
    pipe_HDBDatenobjekte_TEST t
CROSS APPLY STRING_SPLIT(t.Raum_Hierarchie, ';');
