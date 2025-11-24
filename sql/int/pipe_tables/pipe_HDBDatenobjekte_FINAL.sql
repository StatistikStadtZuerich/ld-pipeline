DROP TABLE IF EXISTS dbo.pipe_HDBDatenobjekte_FINAL;

SELECT
    ID,
    Titel,
    Element_Status,
    SASA_Job_Output_Id,
    Beschreibungsdetails,
    Raeumliche_Beziehung,
    Lieferant,
    Quelle,
    Zeitraum_Anfang,
    Zeitraum_ENDE,
    Erstmalige_Veroeffentlichung,
    Aktualisierungsdatum,
    Schlagworte,
    Aktuelle_Version,
    Bemerkungen,
    Metadaten_Publikations_Umgebung,
    Lizenz,
    Aktualisierungsintervall,
    Kategorie,
    Rechtsgrundlage,
    Datentyp,
    Kennzahl_GGH_STK_BEB,
    Raum_Hierarchie,
    Zeit_Hierarchie,
    Dimension_Hierarchie,
    CubeIDs,
    Filter,
    Datenowner,
    Datenqualitaet
INTO dbo.pipe_HDBDatenobjekte_FINAL
FROM dbo.HDBDatenobjekte_FINAL;