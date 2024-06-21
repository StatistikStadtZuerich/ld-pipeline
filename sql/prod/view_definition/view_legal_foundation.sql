DROP VIEW IF EXISTS dbo.view_legal_foundation;

GO

CREATE VIEW dbo.view_legal_foundation AS
SELECT
	CAST(t.id AS VARCHAR) AS legal_foundation_id,
	t.Title AS title,
	t.RGLink AS url
FROM
	dbo.pipe_HDBRechtsgrundlagen_FINAL t;
