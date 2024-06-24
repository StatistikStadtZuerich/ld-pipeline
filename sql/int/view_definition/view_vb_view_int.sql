DROP VIEW IF EXISTS dbo.view_vb_view_int;
GO

CREATE VIEW dbo.view_vb_view_int AS
SELECT
	t.SASA_Job_Output_Id AS id,
	t.Titel AS name,
	1 AS include_datenstatus,
	t.Quelle AS author,
	t.Rechtsgrundlage AS legal_foundation,
	t.Datentyp AS data_type,
	t.Aktuelle_Version AS version,
	t.Beschreibungsdetails AS description,
	t.SASA_Job_Output_Id AS alt_name,
	t.Lieferant AS metadata_creator,
	FORMAT(CAST(t.Erstmalige_Veroeffentlichung AS DATE), 'yyyy-MM-dd') AS issued,
	FORMAT(CAST(t.Zeitraum_Anfang AS DATE), 'yyyy-MM-dd') AS start_date,
    FORMAT(CAST(t.Zeitraum_ENDE AS DATE), 'yyyy-MM-dd') AS end_date,
    FORMAT(CAST(t.Aktualisierungsdatum AS DATE), 'yyyy-MM-dd') AS modified,
    t.Aktualisierungsdatum AS accrual_periodicity,
    4 AS publisher,
    t.Schlagworte AS keyword,
    t.Lizenz AS license,
    t.Bemerkungen AS usage_notes
FROM
	dbo.pipe_HDBDatenobjekte_TEST t;
