DROP TABLE IF EXISTS [dbo].[pipe_HDBKennzahlen_prod];

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
INTO [dbo].[pipe_HDBKennzahlen_prod]
FROM [dbo].[HDBKennzahlen];