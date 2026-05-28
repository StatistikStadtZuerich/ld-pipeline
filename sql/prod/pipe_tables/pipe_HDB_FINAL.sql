DROP TABLE IF EXISTS [dbo].[pipe_HDB_prod];

SELECT
    GESAMTCODE,
    ZEIT,
    JAHR,
    CUBEID,
    KENNZAHL,
    RAUM,
    WERT,
    DATENSTATUS,
    ANZ_GRUPPEN,
    REFERENZNUMMER,
    RECORDSTATUS,
    CAST(NULL AS VARBINARY) as hash,
    DATENSTAND,
    PUBLIKATIONSSTATUS,
    DIFFUSIONSID,
    Gruppe1,
    Gruppencode1,
    Gruppe2,
    Gruppencode2,
    Gruppe3,
    Gruppencode3,
    Gruppe4, 
    Gruppencode4,
    Gruppe5,
    Gruppencode5
INTO [dbo].[pipe_HDB_prod]
FROM [dbo].[HDB_FINAL];