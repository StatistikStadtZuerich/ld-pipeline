DROP VIEW IF EXISTS dbo.view_vb_view;
GO

CREATE VIEW dbo.view_vb_view AS
SELECT
	t.SASA_Job_Output_Id AS id,
	t.Titel AS name,
	1 AS include_datenstatus,
	t.Datenowner AS author,
	t.Rechtsgrundlage AS legal_foundation,
	t.Datentyp AS data_type,
	t.Aktuelle_Version AS version,
	t.Beschreibungsdetails AS description,
	t.SASA_Job_Output_Id AS alt_name,
	t.Lieferant AS metadata_creator,
	FORMAT(CAST(t.Erstmalige_Veroeffentlichung AS DATE), 'yyyy-MM-dd') AS issued,
    t.Aktualisierungsintervall AS accrual_periodicity,
    t.Raeumliche_Beziehung AS spatial,
    4 AS publisher,
    t.Schlagworte AS keyword,
    'cc-zero' AS license,
    t.Bemerkungen AS usage_notes,
    t.Kategorie AS theme,
	t.Datenqualitaet as dataquality
FROM
	dbo.pipe_HDBDatenobjekte_FINAL t
WHERE
	t.CubeIDs IS NOT NULL 
	and FORMAT(CAST(t.Erstmalige_Veroeffentlichung AS DATE), 'yyyy-MM-dd') <= getdate();
