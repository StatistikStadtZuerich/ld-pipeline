# check_gzip_output.py — Anleitung

Script zum Prüfen von **Vollständigkeit und korrekter Struktur der GZIP-Output-Files**
der Pipeline (Testfall TF-12: "ZIP-File auf Vollständigkeit und korrekte Struktur
prüfen"). Liegt im `ld-pipeline`-Repo unter `tests/helper_scripts/check_gzip_output.py`.

---

## Was wird geprüft?

1. **Alle erwarteten RDF/TTL-Files enthalten** — pro Typ (code, cube, observation, …)
   muss mindestens eine Datei existieren.
2. **Struktur entspricht der Vorgabe** — jede Datei ist ein valides Gzip-Archiv,
   Namensschema stimmt (`<typ>_batchNNN.ttl.gz`, 0-gepaddet, 1-indiziert, lückenlos).
3. **Keine fehlenden / keine überzähligen Dateien** — kein Typ fehlt unerklärt, keine
   unbekannten/zusätzlichen Dateien vorhanden.

## Welchen Ordner prüfen?

Standardmässig `output/int/` (relativ zum Verzeichnis, aus dem das Script
aufgerufen wird — darum immer aus dem Repo-Root starten). Dort legt der Pipeline-Schritt `templating_optimized.py`
(`TemplatingOptimized`/`GroupedTemplatingOptimized`) die `_batchNNN.ttl.gz`-Dateien
**direkt** ab.

⚠️ **Timing beachten:** Ein separates, entkoppeltes Shell-Skript
(`create_fuseki_index.sh`) holt sich diese Dateien irgendwann automatisch aus diesem
Ordner (verschiebt sie!), kombiniert sie zu einer einzigen Datei und lädt sie in die
Fuseki-Datenbank. Danach liegen dort keine einzelnen RDF/TTL-Dateien mehr. Darum
diesen Ordner **zeitnah nach einem Pipeline-Lauf** prüfen, bevor der Fuseki-Index-Bau
angestossen wird.

---

## Voraussetzungen

- Python 3.10+ (nutzt nur Standardbibliothek, keine zusätzlichen Pakete nötig)
- Terminal im Repo-Root von `ld-pipeline` geöffnet (z.B. PowerShell in VSCode), damit
  der Standard-Pfad `output/int` stimmt
- Zugriff auf die `int`-Datenbank (für den Pipeline-Lauf im nächsten Schritt)

---

## Schritt 1: Erst die `.gz`-Batches erzeugen (Notebook)

Das Script prüft nur einen bereits vorhandenen Ordner — die `.gz`-Dateien müssen
also zuerst durch einen echten Pipeline-Lauf entstehen. Dafür `notebooks/ld_pipeline.ipynb`
öffnen und der Reihe nach ausführen:

1. **Verzeichnis bestimmen / Config laden** (erste Zellen, `_e = Env.int` ist bereits
   gesetzt)
2. **Notebook-Schritt 1** — Start-Signal prüfen
3. **Notebook-Schritt 2** — Pipe-Tabellen aktualisieren (`initPipeTables`)
4. **Notebook-Schritt 3** — DB-Views neu erstellen (`createViewsFromSQL`)
5. **Notebook-Schritt 4** — Triple-Dateien generieren. **Wichtig:** hier müssen die
   vollständigen `triple_types_metadata` / `triple_types_observations` /
   `triple_types_others`-Listen aktiv sein (keine reduzierte "just for testing"-
   Version) — sonst wird nur ein Bruchteil der Typen erzeugt und die
   Vollständigkeitsprüfung im nächsten Schritt ist nicht aussagekräftig.

   **Tipp für einen schnellen Testlauf (optional):** Ein voller Lauf gegen die echte
   `int`-Datenbank kann bei grossen Tabellen (v.a. `observation`) sehr lange dauern.
   Für einen reinen Struktur-/Vollständigkeitstest reicht ein Bruchteil der Daten.
   In derselben Zelle steht ein Dict `options_batching` mit `db_batch_size`,
   `write_batch_size` und `max_iteration` — `max_iteration` auf einen kleinen Wert
   setzen (z.B. `3`), das begrenzt jeden Templating-Schritt auf max. 3 DB-Fetch-
   Seiten. `write_batch_size` etwas absenken (z.B. auf `150000`), damit trotzdem
   mehrere Batch-Dateien pro Typ entstehen (zum Prüfen von Namensschema/Splitting).
   **Für einen vollständigen Produktionslauf** stattdessen `max_iteration: None`
   und das ursprüngliche `write_batch_size` verwenden — dann aber entsprechend Zeit
   einplanen.

Erst wenn diese Zelle fertig durchgelaufen ist, liegen die `_batchNNN.ttl.gz`-Dateien
in `output/int/` — erst dann macht Schritt 2 unten Sinn.

⚠️ **Noch nicht weiter zu Notebook-Schritt 5** ("Setze das Start-Signal für die
Generierung der Fuseki-Indexdateien") — das stösst den Prozess an, der die Dateien
aus `output/int/` wegverschiebt (siehe Timing-Hinweis oben). Erst prüfen, dann
weitermachen.

---

## Schritt 2: Script ausführen

Das Script ist Teil des Repos, es muss nichts heruntergeladen oder kopiert werden.
Im Terminal im **Repo-Root** von `ld-pipeline` ausführen (nicht im Ordner
`tests\helper_scripts`, sonst wird `output\int` nicht gefunden):

```powershell
python tests\helper_scripts\check_gzip_output.py
```

| Befehl | Wirkung |
|---|---|
| `python tests\helper_scripts\check_gzip_output.py` | Schneller Check: prüft nur den Gzip-Header jeder Datei |
| `python tests\helper_scripts\check_gzip_output.py --deep` | Vollständige Dekompressions-Prüfung — erkennt auch Trunkierung/Korruption mitten in der Datei. Dauert bei grossen/vielen Dateien länger. |
| `python tests\helper_scripts\check_gzip_output.py --verbose` | Zeigt zusätzlich eine Fortschrittszeile pro geprüfter Datei |
| `python tests\helper_scripts\check_gzip_output.py "anderer\pfad"` | Prüft einen anderen Ordner statt `output/int` |

Ergebnis speichern (optional, Script schreibt selbst nichts in eine Datei):
```powershell
python tests\helper_scripts\check_gzip_output.py > ergebnis.txt
```

---

## Ergebnis lesen

Beispiel:
```
Ordner: C:\...\output\int  |  89 .gz-Dateien (14 Typen + 71x ldview_*)  |  FAST
1) Alle erwarteten Files enthalten .. ✓ PASS  (bestaetigt leer: termset_dimension_hierarchy)
2) Struktur (Gzip + Namensschema) ... ✓ PASS
3) Keine fehlenden/ueberzaehligen .... ✓ PASS
GESAMTERGEBNIS: ✓ PASS
```

- Jeder der 3 Punkte hat ein eigenes **✓ PASS** (grün) oder **✗ FAIL** (rot) — Farbe
  nur im echten Terminal sichtbar, nicht bei Umleitung in eine Datei.
- **GESAMTERGEBNIS** ist nur PASS, wenn alle 3 Punkte PASS sind.
- Bei FAIL steht direkt darunter die konkrete Ursache (Datei/Typ).

---

## Konfiguration anpassen

Am Anfang von `tests/helper_scripts/check_gzip_output.py`, zwei Listen:

- **`EXPECTED_TYPES`** — welche Typen vorhanden sein müssen. Aktuell abgestimmt auf
  `notebooks/ld_pipeline.ipynb` (Zelle "4 Generiere die Triple-Dateien"). Ändert sich
  die Notebook-Zelle, diese Liste nachziehen.
- **`KNOWN_EMPTY_TYPES`** — Typen, die in einem konkreten Testlauf bestätigt 0 Zeilen
  geliefert haben (Pipeline-Log: `"No rows left."`). Werden bei Punkt 1 separat als
  "bestätigt leer" ausgewiesen statt als Fehler gezählt. **Vor jedem neuen Testlauf
  prüfen, ob das noch zutrifft** — sonst wird ein echtes Fehlen versehentlich
  verdeckt.

---

## Selbst einen Fehlerfall testen (negative Testing)

**Nie die echten Dateien in `output/int` anfassen** — immer auf einer Kopie
arbeiten:
```powershell
Copy-Item -Path "output\int" -Destination "output\int_broken_test" -Recurse
```

**Punkt 1 (ein Typ fehlt):**
```powershell
Remove-Item "output\int_broken_test\property_batch001.ttl.gz"
```

**Punkt 2 (Batch-Lücke):**
```powershell
Remove-Item "output\int_broken_test\room_batch001.ttl.gz"
```

**Punkt 2 (Korruption — nur `--deep` erkennt das):** Datei kürzen, nicht mittendrin
Bytes überschreiben (der Gzip-Header kann ein Feld mit dem Original-Dateinamen
enthalten; wird das überschrieben, fällt es nicht auf, weil es die eigentlichen
Daten nicht betrifft):
```powershell
$path = "output\int_broken_test\code_batch001.ttl.gz"
$fs = [System.IO.File]::Open($path, 'Open', 'ReadWrite')
$fs.SetLength($fs.Length - 500)
$fs.Close()
```

**Punkt 3 (unerwartete Datei):** muss echtes, gültiges Gzip sein, sonst schlägt
Punkt 2 an statt Punkt 3 — einfach eine bestehende Datei kopieren, neuer Name passt
zu keinem erwarteten Typ:
```powershell
Copy-Item "output\int_broken_test\property_batch001.ttl.gz" "output\int_broken_test\unbekannt_batch001.ttl.gz"
```

**Prüfen:**
```powershell
python tests\helper_scripts\check_gzip_output.py "output\int_broken_test" --deep
```

**Aufräumen:**
```powershell
Remove-Item -Recurse -Force "output\int_broken_test"
```

---
