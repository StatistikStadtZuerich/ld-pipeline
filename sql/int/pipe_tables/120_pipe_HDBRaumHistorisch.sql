DROP TABLE IF EXISTS [dbo].[pipe_HDBRaumHistorisch_int];

SELECT
    LDID,
    Code,
    GueltigVon,
    GueltigBis
INTO [dbo].[pipe_HDBRaumHistorisch_int]
FROM [dbo].[HDBRaumHistorisch];