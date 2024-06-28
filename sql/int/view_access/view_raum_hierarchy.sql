SELECT c0."Raum" as r0, c0."RaumFilter" as f0, c1."Raum" as r1, c1."RaumFilter" as f1, c2."Raum" as r2, c2."RaumFilter" as f2, c3."Raum" as r3
FROM hdb_raum c0
JOIN hdb_raum c1 ON c0."Raum" = c1."RaumParent"
LEFT JOIN hdb_raum c2 ON c1."Raum" = c2."RaumParent"
LEFT JOIN hdb_raum c3 ON c2."Raum" = c3."RaumParent"
WHERE c0."RaumParent" is null;
