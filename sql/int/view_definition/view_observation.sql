DROP VIEW IF EXISTS [dbo].[view_observation_int];

GO

CREATE VIEW [dbo].[view_observation_int]
AS

WITH base_data AS (
SELECT
    CONCAT(h.KENNZAHL,'-',h.Gruppencode1,'-',h.Gruppencode2,'-',h.Gruppencode3,'-',h.Gruppencode4,'-',h.Gruppencode5,'-',h.RAUM,'-',h.Zeit) AS URI,
    REPLACE(REPLACE(TRIM(h.CUBEID), 'CID_', ''), ' ', ',') AS cube_ids,
    h.KENNZAHL AS measure,
    h.WERT AS value,
    h.ZEIT AS time_code,
    FORMAT(DATEFROMPARTS(z.JAHR, z.MONAT, z.TAG), 'yyyy-MM-dd') AS [time],
    h.RAUM AS room_code,
    h.Gruppe1 AS prop1_code_short,
    h.Gruppe2 AS prop2_code_short,
    h.Gruppe3 AS prop3_code_short,
    h.Gruppe4 AS prop4_code_short,
    h.Gruppe5 AS prop5_code_short,
    COALESCE(g1.Origin + SUBSTRING(h.Gruppencode1, 4, 4), h.Gruppencode1) AS prop1_code,
    COALESCE(g2.Origin + SUBSTRING(h.Gruppencode2, 4, 4), h.Gruppencode2) AS prop2_code,
    COALESCE(g3.Origin + SUBSTRING(h.Gruppencode3, 4, 4), h.Gruppencode3) AS prop3_code,
    COALESCE(g4.Origin + SUBSTRING(h.Gruppencode4, 4, 4), h.Gruppencode4) AS prop4_code,
    COALESCE(g5.Origin + SUBSTRING(h.Gruppencode5, 4, 4), h.Gruppencode5) AS prop5_code,
    h.ANZ_GRUPPEN AS number_groups,
    h.DATENSTAND AS modified,
    CASE
        WHEN h.DATENSTATUS LIKE '%veröffentlicht%' THEN 'VEROEFFENTLICHT'
        WHEN h.DATENSTATUS LIKE '%definitiv%'      THEN 'DEFINITIV'
        ELSE 'PROVISORISCH'
    END AS status
FROM [dbo].[pipe_HDB_int] h
    LEFT JOIN [dbo].[pipe_HDBAbgeleiteteGruppen_int] g1 ON g1.Gruppe = h.Gruppe1
    LEFT JOIN [dbo].[pipe_HDBAbgeleiteteGruppen_int] g2 ON g2.Gruppe = h.Gruppe2
    LEFT JOIN [dbo].[pipe_HDBAbgeleiteteGruppen_int] g3 ON g3.Gruppe = h.Gruppe3
    LEFT JOIN [dbo].[pipe_HDBAbgeleiteteGruppen_int] g4 ON g4.Gruppe = h.Gruppe4
    LEFT JOIN [dbo].[pipe_HDBAbgeleiteteGruppen_int] g5 ON g5.Gruppe = h.Gruppe5
    LEFT JOIN [dbo].[pipe_HDBZeit_int] z ON z.ZEIT = h.ZEIT
    LEFT JOIN [dbo].[pipe_Diffusionsereignisse_int] d ON d.id = h.DiffusionsID
    WHERE h.RECORDSTATUS = '0'
      AND h.CUBEID <> ''
      AND (
            h.PUBLIKATIONSSTATUS = 'veröffentlicht'
          OR
            (h.Publikationsstatus <> 'veröffentlicht' AND COALESCE(d.StartDate, '') <= GETDATE())
      )
)
SELECT
    b.URI,
    b.cube_ids,
    b.measure,
    b.value,
    b.time_code,
    b.[time],
    --room_code durch die Codes in HDBRaumHistorisch ersetzen, wenn vorhanden
    COALESCE(rh.LDID, b.room_code) AS room_code,
    b.prop1_code_short,
    b.prop1_code,
    b.prop2_code_short,
    b.prop2_code,
    b.prop3_code_short,
    b.prop3_code,
    b.prop4_code_short,
    b.prop4_code,
    b.prop5_code_short,
    b.prop5_code,
    b.number_groups,
    b.status,
    b.modified
FROM base_data b
LEFT JOIN [dbo].[pipe_HDBRaumHistorisch_int] rh ON rh.Code = b.room_code AND b.[time] BETWEEN ISNULL(rh.GueltigVon, '0001-01-01') AND rh.GueltigBis;

GO
