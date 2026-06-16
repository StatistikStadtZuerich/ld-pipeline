DROP TABLE IF EXISTS [dbo].[pipe_Diffusionsereignisse_int];

SELECT
    ID,
    StartDate
INTO [dbo].[pipe_Diffusionsereignisse_int]
FROM [dbo].[Diffusionsereignisse];