DROP TABLE IF EXISTS [dbo].[pipe_HDBRaumHistorisch_prod];

SELECT
    LDID,
    Code,
    GueltigVon,
    GueltigBis
INTO [dbo].[pipe_HDBRaumHistorisch_prod]
FROM [dbo].[HDBRaumHistorisch];