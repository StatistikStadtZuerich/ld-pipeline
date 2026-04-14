DROP TABLE IF EXISTS [dbo].[pipe_HDBZeit_int];

GO

SELECT
    ZEIT,
    JAHR,
    MONAT,
    TAG,
    PERIODESTART,
    PERIODEENDE,
	BEZUGSZEIT
INTO [dbo].[pipe_HDBZeit_int]
FROM [dbo].[HDBZeit];