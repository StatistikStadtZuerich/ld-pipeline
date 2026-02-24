DROP TABLE IF EXISTS dbo.pipe_HDBDatenobjekte_TEST;

SELECT
    ID,
    Titel,
    Element_Status,
    SASA_Job_Output_Id,
    Beschreibungsdetails,
    Raeumliche_Beziehung,
    Lieferant,
    Erstmalige_Veroeffentlichung,
    Schlagworte,
    Aktuelle_Version,
    Bemerkungen,
    Metadaten_Publikations_Umgebung,
    Aktualisierungsintervall,
    Kategorie,
    Rechtsgrundlage,
    Datentyp,
    Kennzahl_GGH_STK_BEB,
    Raum_Hierarchie,
    Zeit_Hierarchie,
    Dimension_Hierarchie,
    CubeIDs,
    RaumFilter,
    DimensionFilter,
    Datenowner,
    Datenqualitaet
INTO dbo.pipe_HDBDatenobjekte_TEST
FROM dbo.HDBDatenobjekte_TEST;