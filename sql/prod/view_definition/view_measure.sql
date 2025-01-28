DROP VIEW IF EXISTS dbo.view_measure;

GO

CREATE VIEW dbo.view_measure AS
SELECT
	t.KennzahlCode AS measure_code,
	t.Kennzahlname AS title,
	t.Einheit AS name,
	t.Einheit_Kurz AS identifier,
	t.Methode AS method,
	REPLACE(t.Einheit_URI, ' ', '_') AS unit,
	REPLACE(REPLACE(
        REPLACE(
            REPLACE(t.Methode, CHAR(13) + CHAR(10), ' '), 
            CHAR(13), ' '
        ), 
        CHAR(10), ' '
    ), '"', '') AS description
FROM
	dbo.pipe_HDBKennzahlen t;
