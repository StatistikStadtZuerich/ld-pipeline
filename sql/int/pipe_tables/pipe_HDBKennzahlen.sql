DROP TABLE IF EXISTS dbo.pipe_HDBKennzahlen;

SELECT
    KennzahlCode,
    Kennzahlname,
    Einheit,
    Einheit_Kurz,
    Einheit_URI,
    Methode,
    Beschreibung
INTO dbo.pipe_HDBKennzahlen
FROM dbo.HDBKennzahlen;