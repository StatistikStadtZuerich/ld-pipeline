DROP VIEW IF EXISTS dbo.view_time;

GO

CREATE VIEW dbo.view_time AS
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
    ISNULL(t.PERIODEENDE, '') AS "end_date",
    CASE
        WHEN (t.ZEIT LIKE 'Z3112%' OR t.ZEIT LIKE 'ZXX12%'
			OR t.ZEIT LIKE 'ZXXXX%' OR t.ZEIT LIKE 'ZPJ00%') THEN 1
        ELSE 0
    END AS filter_year,
	CASE
        WHEN (t.ZEIT LIKE 'Z3006%' OR t.ZEIT LIKE 'Z3112%'
			OR t.ZEIT LIKE 'ZXX06%' OR t.ZEIT LIKE 'ZXX12%'
			OR t.ZEIT LIKE 'ZXXXX%') THEN 1
        ELSE 0
    END AS filter_semester,
	CASE
        WHEN (t.ZEIT LIKE 'Z3004%' OR t.ZEIT LIKE 'Z3108%'
			OR t.ZEIT LIKE 'Z3112%' OR t.ZEIT LIKE 'ZXX04%'
			OR t.ZEIT LIKE 'ZXX08%' OR t.ZEIT LIKE 'ZXX12%'
			OR t.ZEIT LIKE 'ZXXXX%') THEN 1
        ELSE 0
    END AS filter_trimester,
	CASE
        WHEN (t.ZEIT LIKE 'Z3006%' OR t.ZEIT LIKE 'Z3009%'
			OR t.ZEIT LIKE 'Z3103%' OR t.ZEIT LIKE 'Z3112%'
			OR t.ZEIT LIKE 'ZXX03%' OR t.ZEIT LIKE 'ZXX06%'
			OR t.ZEIT LIKE 'ZXX09%' OR t.ZEIT LIKE 'ZXX12%'
			OR t.ZEIT LIKE 'ZXXXX%' OR t.ZEIT LIKE 'ZPQ%') THEN 1
        ELSE 0
    END AS filter_quarter,
	CASE
        WHEN (t.ZEIT LIKE 'Z3101%' OR t.ZEIT LIKE 'Z2802%'
			OR t.ZEIT LIKE 'Z2902%' OR t.ZEIT LIKE 'Z3103%'
			OR t.ZEIT LIKE 'Z3004%' OR t.ZEIT LIKE 'Z3105%'
			OR t.ZEIT LIKE 'Z3006%' OR t.ZEIT LIKE 'Z3107%'
			OR t.ZEIT LIKE 'Z3108%' OR t.ZEIT LIKE 'Z3009%'
			OR t.ZEIT LIKE 'Z3110%' OR t.ZEIT LIKE 'Z3011%'
			OR t.ZEIT LIKE 'Z3112%' OR t.ZEIT LIKE 'ZPJAN%'
			OR t.ZEIT LIKE 'ZPFEB%' OR t.ZEIT LIKE 'ZPMRZ%'
			OR t.ZEIT LIKE 'ZPAPR%' OR t.ZEIT LIKE 'ZPMAI%'
			OR t.ZEIT LIKE 'ZPJUN%' OR t.ZEIT LIKE 'ZPJUL%'
			OR t.ZEIT LIKE 'ZPAUG%' OR t.ZEIT LIKE 'ZPSEP%'
			OR t.ZEIT LIKE 'ZPOKT%' OR t.ZEIT LIKE 'ZPNOV%'
			OR t.ZEIT LIKE 'ZPDEZ%' OR t.ZEIT LIKE 'ZXX%') THEN 1
        ELSE 0
    END AS filter_month,
	1 AS filter_day
FROM
    dbo.pipe_HDBZeit t;
