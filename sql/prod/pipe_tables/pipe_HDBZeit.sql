DROP TABLE IF EXISTS [dbo].[pipe_HDBZeit_prod];

GO

SELECT
    ZEIT,
    JAHR,
    MONAT,
    TAG,
    PERIODESTART,
    PERIODEENDE,
	BEZUGSZEIT
INTO [dbo].[pipe_HDBZeit_prod]
FROM [dbo].[HDBZeit];