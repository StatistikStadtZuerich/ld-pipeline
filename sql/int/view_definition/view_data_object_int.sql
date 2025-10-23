DROP VIEW IF EXISTS dbo.view_data_object_int;
GO
DROP VIEW IF EXISTS dbo.view_data_object_int_old;
GO

CREATE VIEW dbo.view_data_object_int_old AS
SELECT
    CAST(t.ID AS VARCHAR) AS "object_id",
    FORMAT(CAST(t.Erstmalige_Veroeffentlichung AS DATE), 'yyyy-MM-dd') AS issued,
    t.Titel AS name,
    t.Schlagworte AS keywords,
    t.Beschreibungsdetails AS description,
    t.SASA_Job_Output_Id AS alternate_name,
    FORMAT(CAST(t.Aktualisierungsdatum AS DATE), 'yyyy-MM-dd') AS modified,
    t.Bemerkungen AS notes,
    t.Raeumliche_Beziehung AS spatial,
    t.Lieferant AS author,
    t.Aktuelle_Version AS version,
    t.Lizenz AS license,
    t.Aktualisierungsintervall AS update_interval,
    t.Kategorie AS theme,
    t.Rechtsgrundlage AS legal_foundation,
    t.Datentyp AS type
FROM
    dbo.pipe_HDBDatenobjekte_TEST t
WHERE
    t.Element_Status = 'veröffentlicht'
AND
	t.Metadaten_Publikations_Umgebung = 'INT';
