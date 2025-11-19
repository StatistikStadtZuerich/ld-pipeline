DROP VIEW IF EXISTS dbo.view_measure_unit;

GO

CREATE VIEW dbo.view_measure_unit AS
SELECT
    t.KennzahlCode AS unit_code,
    STRING_AGG(t.Kennzahlname, ', ') AS title
FROM
    dbo.pipe_HDBKennzahlen t
GROUP BY
    t.KennzahlCode;
