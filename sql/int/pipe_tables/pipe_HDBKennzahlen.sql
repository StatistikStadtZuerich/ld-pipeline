DROP TABLE IF EXISTS [dbo].[pipe_HDBKennzahlen_int];

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
INTO [dbo].[pipe_HDBKennzahlen_int]
FROM [dbo].[HDBKennzahlen];