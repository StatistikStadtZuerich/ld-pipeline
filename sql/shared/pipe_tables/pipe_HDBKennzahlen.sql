DROP TABLE IF EXISTS dbo.pipe_HDBKennzahlen;

GO

SELECT
    KennzahlCode,
    Kennzahlname,
    Einheit,
    Einheit_Kurz,
    Einheit_URI,
    Methode,
    Beschreibung,
    equivalentProperty
INTO dbo.pipe_HDBKennzahlen
FROM dbo.HDBKennzahlen;