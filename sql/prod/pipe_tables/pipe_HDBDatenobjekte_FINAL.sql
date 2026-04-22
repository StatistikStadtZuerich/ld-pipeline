DROP TABLE IF EXISTS [dbo].[pipe_HDBDatenobjekte_prod];

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
    HierarchieID_List,
    CubeIDs,
    RaumFilter,
    DimensionFilterID,
    Datenowner,
    Datenqualitaet
INTO [dbo].[pipe_HDBDatenobjekte_prod]
FROM [dbo].[HDBDatenobjekte_FINAL];