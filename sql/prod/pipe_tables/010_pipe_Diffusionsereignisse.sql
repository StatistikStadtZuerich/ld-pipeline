DROP TABLE IF EXISTS [dbo].[pipe_Diffusionsereignisse_prod];

SELECT
    ID,
    StartDate
INTO [dbo].[pipe_Diffusionsereignisse_prod]
FROM [dbo].[Diffusionsereignisse];