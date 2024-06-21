DROP VIEW IF EXISTS dbo.view_time_int;

GO

CREATE VIEW dbo.view_time_int AS
SELECT
	t.ZEIT AS term_code,
	ISNULL(CASE
		WHEN t.ZEIT LIKE 'ZP%' THEN
			CONVERT(VARCHAR, EOMONTH(
				CAST(
					'01-' + 
					CASE 
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'JAN' THEN 'JAN' 
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'FEB' THEN 'FEB'
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'MRZ' THEN 'MAR'
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'APR' THEN 'APR'
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'MAI' THEN 'MAY'
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'JUN' THEN 'JUN'
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'JUL' THEN 'JUL'
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'AUG' THEN 'AUG'
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'SEP' THEN 'SEP'
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'OKT' THEN 'OCT'
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'NOV' THEN 'NOV'
						WHEN SUBSTRING(t.ZEIT, 3, 3) = 'DEZ' THEN 'DEC'
					END + 
					'-' + 
					SUBSTRING(t.ZEIT, 6, 4) AS DATE
				)
			))
		   
		ELSE CONVERT(VARCHAR, SUBSTRING(t.ZEIT, 6, 4) + '-' + 
				SUBSTRING(t.ZEIT, 4, 2) + '-' +
				SUBSTRING(t.ZEIT, 2, 2))
		END, '') AS "date",
	ISNULL(t.PERIODESTART, '') AS "reference_time",
	ISNULL(t.PERIODESTART, '') AS "start_date",
	ISNULL(t.PERIODEENDE, '') AS "end_date"
FROM
	dbo.pipe_HDBZeit t;