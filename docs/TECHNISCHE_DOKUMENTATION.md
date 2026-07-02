# Technische Dokumentation – LD Pipeline (ssz-lod)

> Stand: Juni 2026 · Zielgruppe: Entwickler:innen
> Repository: `LD-pipeline` (gespiegelt auf [GitHub](https://github.com/StatistikStadtZuerich/ld-pipeline))

Diese Dokumentation beschreibt Aufbau, Technologie und Nutzen der LD Pipeline sowie das
konkrete Vorgehen, um neue Steps, neue Triple-Dateien und neue Triples hinzuzufügen.

---

## Inhaltsverzeichnis

1. [Überblick & Nutzen](#1-überblick--nutzen)
2. [Technologie-Stack](#2-technologie-stack)
3. [Gesamtarchitektur](#3-gesamtarchitektur)
4. [Datenfluss (End-to-End)](#4-datenfluss-end-to-end)
5. [Kernkonzepte & Klassen](#5-kernkonzepte--klassen)
6. [Die Pipeline-Steps im Detail](#6-die-pipeline-steps-im-detail)
7. [Templates & Triple-Erzeugung](#7-templates--triple-erzeugung)
8. [SQL-Schicht (Pipe-Tables & Views)](#8-sql-schicht-pipe-tables--views)
9. [LD-Views (cube.link View Builder)](#9-ld-views-cubelink-view-builder)
10. [Konfiguration & Umgebungen](#10-konfiguration--umgebungen)
11. [Ausführung (CLI, Docker, Skripte)](#11-ausführung-cli-docker-skripte)
12. [Tests & CI/CD](#12-tests--cicd)
13. [Erweitern der Pipeline](#13-erweitern-der-pipeline)
    - [13.1 Neuen Step hinzufügen](#131-neuen-step-hinzufügen)
    - [13.2 Neue Triple-Datei (Templating-Step) hinzufügen](#132-neue-triple-datei-templating-step-hinzufügen)
    - [13.3 Neue Triples in bestehendem Template ergänzen](#133-neue-triples-in-bestehendem-template-ergänzen)
    - [13.4 Neue Quelltabelle / neuen View hinzufügen](#134-neue-quelltabelle--neuen-view-hinzufügen)
14. [Glossar](#14-glossar)

---

## 1. Überblick & Nutzen

Die **LD Pipeline** (Linked-Data-Pipeline, früher „LD Pipeline 2024") überführt
statistische Daten der Stadt Zürich aus der **Harmonisierten Datenbank (HDB)** in
**RDF-Triples** und lädt diese in eine RDF-/Triplestore-Datenbank (**Apache Jena
Fuseki**). Ziel ist die Veröffentlichung der Daten als **Linked Open Data** unter
`https://ld.stadt-zuerich.ch`.

Der Nutzen im Kern:

- **Extrahieren** der relevanten Daten aus der HDB (MS SQL Server) über aufbereitete
  Tabellen und Views.
- **Transformieren** der tabellarischen Daten in standardkonforme RDF-Triples
  (Vokabulare u.a. [cube.link](https://cube.link), [schema.org](https://schema.org),
  Dublin Core, DCAT) per Jinja-Templates.
- **Laden** der komprimierten Triple-Dateien in einen Fuseki-Index, der die
  öffentliche SPARQL-/Linked-Data-Schnittstelle speist.

Gegenüber der Vorgängerpipeline liegt der Fokus auf **Flexibilität** (Steps frei
kombinierbar, Templates austauschbar), **Effizienz** (batch-basierte, „optimized"
Verarbeitung großer Datenmengen) und **Skalierbarkeit**.

---

## 2. Technologie-Stack

| Bereich | Technologie |
|---|---|
| Sprache | Python 3.10 (lauffähig ab 3.6; CI testet 3.12) |
| CLI | [Typer](https://typer.tiangolo.com/) (`main.py`) |
| Templating | [Jinja2](https://jinja.palletsprojects.com/) (`.ttl.jinja`, `.sql.jinja`) |
| RDF | [rdflib](https://rdflib.readthedocs.io/) (Literal-Encoding) |
| Datenbank | MS SQL Server (`pymssql`) – produktiv; MySQL (`mysql-connector-python`) – lokal/Docker |
| Triplestore | Apache Jena Fuseki; Index-Aufbau via Jena `tdb2.xloader` (Shell-Skript) |
| Konfiguration | `configparser` + `extended_configparser` (Env-Interpolation) |
| Tests | `pytest`, `pytest-docker` |
| Linting/Format | `ruff` |
| Containerisierung | Docker (`Dockerfile`, `compose.yaml`) |
| CI/CD | GitLab CI (`.gitlab-ci.yml`), Mirror nach GitHub |
| Benachrichtigung | MS Teams (`scripts/teams-notify.sh`) |

Abhängigkeiten siehe `requirements.txt`.

---

## 3. Gesamtarchitektur

Die Anwendung ist als **Step-basierte Pipeline** aufgebaut. Jeder Verarbeitungsschritt
ist eine eigene Klasse, die vom abstrakten `Step` erbt und eine `run(environment)`-Methode
implementiert. Die `Pipeline` führt Steps in definierter Reihenfolge aus. Eine
`Environment`-Instanz kapselt Konfiguration, Datenbankverbindung, Template- und
Kompressions-Engine für die jeweilige Umgebung (`test`, `local`, `int`, `prod`, `dev`).

```
ssz-lod-pipeline/
├── main.py                  # Typer-CLI: Step-Definitionen + Befehle (run / step / list-step-names)
├── run_pipeline.py          # Orchestrierung des Voll-Laufs inkl. Batching & Signale
├── config.ini               # Konfiguration je Umgebung
├── pipeline/
│   ├── pipeline.py          # Pipeline-Runner (run / step / execute)
│   ├── base/                # Querschnittsfunktionen
│   │   ├── base.py          #   Base (Logger)
│   │   ├── config.py        #   Env-Enum + Config-Wrapper
│   │   ├── environment.py   #   Environment: DB/Template/Compression-Factories, Namens-Logik
│   │   ├── services.py      #   JinjaTemplateEngine, GzipEngine, MySQLDbConnection
│   │   ├── mmsql_service.py #   MSSQLDbConnection (pymssql)
│   │   ├── step.py          #   Step (abstrakt) + StepDefinition
│   │   └── utils.py         #   Start/Stopp-Signale, Fuseki-Index-Trigger (Singleton)
│   ├── interfaces/services.py  # Abstrakte Interfaces (DbConnection, TemplateEngine, ...)
│   ├── steps/               # Konkrete Steps (s. Abschnitt 6)
│   │   └── ldview/          # cube.link View-Builder (Model, Builder, Serializer)
│   └── templates/           # Jinja-Templates für Triples (*.ttl.jinja)
├── database/                # SQL-Step-Basis + Pipe-Table-Initialisierung
├── sql/                     # SQL-Definitionen je Umgebung + Jinja-Vorlagen
│   ├── templates/           #   *.sql.jinja (parametrisiert)
│   ├── int/  prod/          #   gerenderte/feste SQL je Umgebung
│   ├── pipe_tables/         #   Aufbereitung der Quelltabellen
│   └── view_definition/     #   DB-Views, die die Templates speisen
├── static/static.ttl        # Statische Triples (Vokabular/Präfixe/Organisation)
├── scripts/                 # Fuseki-Index-Skripte, Teams-Notify
└── tests/                   # unit/ + integration/
```

---

## 4. Datenfluss (End-to-End)

Der vollständige Lauf (`run_pipeline.py`) verläuft in vier Phasen:

1. **DB-Aufbereitung**
   - `initPipeTables`: erzeugt aus den HDB-Quelltabellen aufbereitete `pipe_*`-Tabellen
     (umgebungsspezifisch benannt).
   - `createViewsFromSQL`: legt die DB-Views an, die die Templating-Steps abfragen.

2. **Triple-Erzeugung** (`generate_triple_files`)
   - Metadaten-Triples: `code`, `cube`, `groupCode`, `groupTermset`, `hierarchy`,
     `measureUnit`, `measure`, `property`, `room`, `time`, `timeRelation`,
     `timeTermset`, `dimensionTermset` (jeweils `…Templating`).
   - Beobachtungen: `observationTemplating` (Massendaten).
   - Sonstiges: `copyStatic`, `buildInfo`, `buildTermsetHierarchy`, `generateViews`.
   - Jeder Step liest aus einem View, rendert je Zeile ein Jinja-Template und schreibt
     `.ttl`-Dateien (im optimierten Modus direkt gezippte `.ttl.gz`-Batches).

3. **Index-Signal**
   - `Utils.set_start_signal_fuseki_index(...)` schreibt eine Signaldatei. Ein separates
     Shell-Skript (`create_fuseki_index.sh`) baut daraufhin den Fuseki-Index neu auf.

4. **Rückschreiben Publikationsstatus**
   - `writePublicationStatiToHDB`: berechnet Hashes je Beobachtung und schreibt
     Publikationsstatus/-datum zurück in die HDB.

```
run_pipeline.py
│
├─ Phase 1 · DB-Aufbereitung
│     HDB (MS SQL)
│       ├─ initPipeTables      ──►  pipe_*-Tabellen
│       └─ createViewsFromSQL  ──►  view_*-Views (DB-Sichten)
│
├─ Phase 2 · Triple-Erzeugung   (liest view_*, rendert Jinja-Templates)
│     …Templating · observationTemplating · generateViews
│     copyStatic · buildInfo · buildTermsetHierarchy
│       └──►  *.ttl.gz  (in output_path; inkl. static.ttl, info.ttl, view.*.ttl)
│
├─ Phase 3 · Index-Signal
│     Utils.set_start_signal_fuseki_index()  ──►  start_fuseki_index_*.txt
│
└─ Phase 4 · Rückschreiben
      writePublicationStatiToHDB  ──►  HDB


┄┄ entkoppelt über die Signaldatei · extern getaktet (Cron/Timer, nicht im Repo) ┄┄

run_fuseki_index.sh  ──(findet Signal)──►  create_fuseki_index.sh
      riot --validate  →  tdb2.xloader (Offline-Index-Bau)
                                          │
                                          ▼
                       Apache Jena Fuseki  ──►  ld.stadt-zuerich.ch (Linked Open Data)
```

> Hinweis: Der Index-Aufbau ist von der Python-Pipeline **entkoppelt**. `run_pipeline.py`
> schreibt nur die Signaldatei (Phase 3); das extern getaktete `run_fuseki_index.sh`
> erkennt sie und ruft `create_fuseki_index.sh` auf, das den Index per Jena `tdb2.xloader`
> offline baut (kein HTTP-Upload).

---

## 5. Kernkonzepte & Klassen

### `Base` (`pipeline/base/base.py`)
Abstrakte Basisklasse, stellt allen Komponenten einen `self.logger` bereit
(`logging.getLogger(self.__class__.__name__)`).

### `Step` & `StepDefinition` (`pipeline/base/step.py`)
- `Step` (abstrakt): erzwingt `run(self, environment: Environment)`.
- `StepDefinition`: bündelt `name` (CLI-Name), `step` (Instanz) und `description`.
  Die Registry aller Steps wird in `main.get_step_definitions()` aufgebaut.

### `Pipeline` (`pipeline/pipeline.py`)
Hält das `Environment` und ein Dict von `StepDefinition`s. Methoden:
- `run(*steps)` – führt mehrere Steps in Reihenfolge aus.
- `step(step_def)` – führt einen einzelnen Step aus (mit Logging).
- `execute(name)` – schlägt einen Step per Name in der Registry nach und führt ihn aus
  (wirft `NotImplementedError`, wenn unbekannt).

### `Environment` (`pipeline/base/environment.py`)
Zentrale Factory und Namens-Logik je Umgebung:
- `get_db_connection()` → `MSSQLDbConnection` (`db_type=mssql`) oder `MySQLDbConnection`
  (`db_type=mysql`).
- `get_template_engine(template, output)` → `JinjaTemplateEngine`.
- `get_compression_engine()` → `GzipEngine`.
- **Namens-Helfer** (wichtig für Mehr-Umgebungs-Betrieb):
  - `table_name(name)` – hängt z.B. `_FINAL`/`_TEST`-Suffix an HDB-Tabellen an.
  - `pipe_table_name(name)` – hängt den Umgebungsnamen an (`pipe_HDB_int`).
  - `view_name(name)` – in `prod`/`dev` unverändert, sonst `…_<env>` (`view_code_int`).

> ℹ️ **Hinweis:** Die Namens-Helfer (`table_name` / `pipe_table_name` / `view_name`) werden
> im Zuge von
> [Issue #467](https://cmp-sdlc.stzh.ch/OE-7035/ssz-taskmanagement/team-projekte/ld-2025/-/issues/467)
> angepasst – dieser Abschnitt ist entsprechend nachzuführen.

### `Config` & `Env` (`pipeline/base/config.py`)
- `Env`: Enum der Umgebungen (`test`, `local`, `int`, `prod`, `dev`).
- `Config.get(name, return_type, fallback)`: typsicherer Zugriff auf `config.ini`
  (mit `EnvInterpolation`, d.h. Umgebungsvariablen werden interpoliert).

### Services (`pipeline/base/services.py`)
- `JinjaTemplateEngine`: lädt Templates aus `template_path`, registriert eigene
  **Jinja-Filter** und schreibt gerenderte Inhalte in die Ausgabedatei. Die Filter:
  - `uri_encode` – Umlaute ersetzen, Nicht-`[A-Za-z0-9-]` entfernen, URL-encodieren
    (für IRI-Bestandteile).
  - `literal_encode` – Whitespace normalisieren, als RDF-Literal in N3-Notation ausgeben.
  - `is_numeric`, `is_valid_date` – Hilfsprädikate für bedingte Triples.
- `GzipEngine`: gzip-Kompression einzelner Dateien in `compression_output_path`.
- `MySQLDbConnection` / `MSSQLDbConnection`: Context-Manager um die DB-Verbindung
  (`__enter__`/`__exit__`), Cursor liefert Zeilen als Dict.

### `Utils` (`pipeline/base/utils.py`)
Singleton mit Datei-Signal-Logik für die Orchestrierung über Verzeichnisse:
`check_start_signal`, `is_pipeline_running`, `set_finish_signal` und
`set_start_signal_fuseki_index` (löst den Index-Neuaufbau aus).

---

## 6. Die Pipeline-Steps im Detail

Alle Steps werden in `main.get_step_definitions()` als `StepDefinition` registriert.
Aktuelle Liste lässt sich jederzeit per `python main.py list-step-names` ausgeben.

| Step-Name (CLI) | Klasse | Zweck |
|---|---|---|
| `copyStatic` | `Copy` | Kopiert `static/static.ttl` ins Output und zippt es (`info`/Vokabular). |
| `buildInfo` | `BuildInfo` (erbt `Copy`) | Erzeugt `info.ttl` mit Build-Zeitstempel (`dcterms:created`). |
| `codeTemplating` | `Templating`* | Triples für Codes (`DefinedTerm`) aus `view_code`. |
| `cubeTemplating` | `Templating`* | Cube-Definitionen aus `view_cube`. |
| `groupCodeTemplating` | `Templating`* | Gruppen-Codes aus `view_group_code`. |
| `groupTermsetTemplating` | `Templating`* | Gruppen-Termsets aus `view_group_termset`. |
| `hierarchyTemplating` | `Templating`* | Hierarchien aus `view_hierarchy`. |
| `measureUnitTemplating` | `Templating`* | Maßeinheiten aus `view_measure_unit`. |
| `measureTemplating` | `Templating`* | Kennzahlen/Measures aus `view_measure`. |
| `observationTemplating` | `Templating`* | **Beobachtungen** (Massendaten) aus `view_observation`. |
| `propertyTemplating` | `Templating`* | Properties aus `view_property`. |
| `roomTemplating` | `Templating`* | Raum-Codes aus `view_room`. |
| `timeTemplating` | `Templating`* | Zeit-Codes aus `view_time`. |
| `timeRelationTemplating` | `Templating`* | Zeit-Termset-Relationen aus `view_time_termset_relation`. |
| `timeTermsetTemplating` | `GroupedTemplatingOptimized` | Gruppierte Zeit-Termsets (`group_by=termset_code`). |
| `dimensionTermsetTemplating` | `Templating`* | Dimensions-Hierarchien aus `view_dimension_hierarchy`. |
| `compressing` | `Compressing` | gzip-Kompression aller `.ttl` im Triple-Output. |
| `initPipeTables` | `InitPipeTables` | Erzeugt/aktualisiert `pipe_*`-Tabellen aus SQL. |
| `createViewsFromSQL` | `CreateViewsFromSQL` | Legt DB-Views aus SQL an. |
| `generateViews` | `ViewsStep` | Erzeugt cube.link-LD-Views (s. Abschnitt 9). |
| `buildTermsetHierarchy` | `BuildTermsetHierarchy` | Raum-Hierarchie-Relationen aus `view_room_hierarchy`. |
| `writePublicationStatiToHDB` | `WritePublicationStatiToHDB` | Schreibt Publikationsstatus zurück in die HDB. |

\* Die `…Templating`-Steps werden über die Factory **`create_templating(env, …)`**
(`pipeline/steps/optimized.py`) erzeugt. Sie wählt zur Laufzeit die Implementierung:
- `GroupedTemplatingOptimized`, falls `options["grouped"]` gesetzt ist,
- `TemplatingOptimized`, falls `optimized=true` (in `int`/`prod`),
- ansonsten das einfache `Templating`.

### Wichtige Step-Implementierungen

**`Copy` / `BuildInfo`** (`steps/copy.py`, `steps/buildInfo.py`)
Kopiert eine Quelldatei ins Output-Verzeichnis und erzeugt eine gzip-Variante. `BuildInfo`
schreibt zuvor dynamisch eine temporäre `info.ttl` mit aktuellem UTC-Zeitstempel.

**`Templating`** (`steps/templating.py`)
Lädt die SQL-Query (entweder generisch `SELECT * FROM <view_name>` oder aus Datei),
öffnet DB-Verbindung + Template-Engine und rendert je Cursor-Zeile das Template. Über
die überschreibbare Methode `pre_process(row)` lässt sich eine Zeile vor dem Rendern in
mehrere Datensätze aufspalten (genutzt z.B. von `BuildTermsetHierarchy`).

**`TemplatingOptimized`** (`steps/templating_optimized.py`)
Für große Datenmengen. Legt eine temporäre Tabelle `#<view>` mit `_sort_order`-Spalte und
Index an, lädt die Daten paginiert (`OFFSET … FETCH NEXT`, `db_batch_size`), rendert die
Triples und schreibt gezippte Batch-Dateien (`…_batchNNN.ttl.gz`) ab `write_batch_size`.
Ein adaptives `_cooldown()` drosselt die Last bei langsamen Iterationen. Bei
`observation` + `only_vb_cubes=true` werden nur Cubes des View-Builders berücksichtigt.
`GroupedTemplatingOptimized` gruppiert zusätzlich Zeilen nach `group_by`, ohne Gruppen
über Batch-Grenzen zu zerschneiden.

**`Compressing`** (`steps/compressing.py`)
Komprimiert alle Dateien aus `template_output_path` über die `GzipEngine`.

**`InitPipeTables`** / **`CreateViewsFromSQL`** (`database/`, `steps/`)
Beide erben von `BaseSQLStep`. Sie lesen SQL-Dateien (`.sql` oder gerenderte `.sql.jinja`)
aus konfigurierten Ordnern, splitten an `GO`-Batchgrenzen und führen sie gegen die DB aus.

**`ViewsStep`** (`steps/views.py`)
Baut über `LdViewBuilder` alle LD-Views, serialisiert sie nach `ldviews/view.<id>.ttl`
und packt sie in eine einzige gezippte Datei `<env>_ldview_<ts>_<uuid>.ttl.gz`.

**`WritePublicationStatiToHDB`** (`steps/write_publication_stati_to_hdb.py`)
Berechnet MD5-Hashes über alle Spalten von `pipe_HDB`, vergleicht sie und setzt für
unveränderte, freigegebene Datensätze `PUBLIKATIONSSTATUS`, `PUBLIKATIONSDATUM` und
`GESAMTCODE_EXPORTIERT` in der HDB.

---

## 7. Templates & Triple-Erzeugung

Triples werden über **Jinja-Templates** in `pipeline/templates/` erzeugt. Jede Zeile aus
dem zugehörigen View wird als Dict an `template.render(row)` übergeben; die Template-Platzhalter
greifen auf die Spaltennamen zu.

Beispiel `code.ttl.jinja` (1 Triple-Block pro Code):

```jinja
<https://ld.stadt-zuerich.ch/statistics/code/{{ term_code|uri_encode }}> a <https://schema.org/DefinedTerm> ;
    <https://schema.org/name> {{ title|literal_encode }} ;
    <https://schema.org/termCode> {{ term_code|literal_encode }} ;
    <https://schema.org/inDefinedTermSet> <https://ld.stadt-zuerich.ch/statistics/termset/{{ term_group_code|uri_encode }}> .
```

Beobachtungen (`observation.ttl.jinja`) sind komplexer: dynamische Properties
(`prop1..prop5`, übersprungen bei Wert `"XXX"`), typisierte Werte (decimal vs.
`cube:Undefined`) und mehrere `cube:observation`-Zuordnungen je Cube-ID.

Die wichtigsten Vokabulare/IRIs: `https://cube.link/*`, `https://schema.org/*`,
`http://purl.org/dc/terms/*`, `http://www.w3.org/ns/dcat#*`. Basis-Präfixe und statische
Aussagen liegen in `static/static.ttl`.

**Zentrale Filter** (registriert in `JinjaTemplateEngine`):
- `uri_encode` – sicheres Erzeugen von IRI-Bestandteilen.
- `literal_encode` – korrekt escaptes RDF-Literal (N3).
- `is_numeric` / `is_valid_date` – Bedingungen für typisierte Triples.

---

## 8. SQL-Schicht (Pipe-Tables & Views)

Die SQL-Schicht ist dreistufig organisiert und über **Jinja** parametrisiert, damit
dieselbe Logik für mehrere Umgebungen funktioniert.

```
sql/
├── templates/                # Quelle der Wahrheit: parametrisierte *.sql.jinja
│   ├── pipe_tables/          #   Aufbereitung der HDB-Quelltabellen → pipe_*
│   └── view_definition/      #   DB-Views, die die Templating-Steps lesen
├── int/   prod/              # gerenderte/feste SQL je Umgebung (Referenz)
```

Die Jinja-SQL-Filter werden in `BaseSQLStep._init_jinja_env()` registriert:
- `pipe_table_name` → `pipe_HDB` ⇒ `pipe_HDB_int` usw.
- `table_name` → HDB-Tabellen mit `_FINAL`/`_TEST`-Suffix.
- `view_name` → Views mit Umgebungssuffix (außer `prod`/`dev`).

> ℹ️ **Hinweis:** Diese Namens-/Suffix-Logik wird im Zuge von
> [Issue #467](https://cmp-sdlc.stzh.ch/OE-7035/ssz-taskmanagement/team-projekte/ld-2025/-/issues/467)
> angepasst – dieser Abschnitt ist entsprechend nachzuführen.

Jeder Filter unterstützt optionale Parameter `(fqa, square_brackets)` für vollständig
qualifizierte Namen (`[dbo].[…]`).

Beispiel `view_code.sql.jinja`:

```jinja
DROP VIEW IF EXISTS [{{ 'dbo.view_code' | view_name }}];
GO
CREATE VIEW [{{ 'dbo.view_code' | view_name }}] AS
SELECT t.CODE AS term_code, t.CODENAME AS title, t.REFERENZTABELLE AS term_group_code
FROM [{{ 'dbo.pipe_HDBCodeliste' | pipe_table_name }}] t;
```

`BaseSQLStep` splittet Skripte an `GO`-Zeilen in Batches und führt sie einzeln aus
(`InitPipeTables` mit Rollback bei Fehler, `CreateViewsFromSQL` mit Commit am Ende).

---

## 9. LD-Views (cube.link View Builder)

Die LD-Views (`pipeline/steps/ldview/`) modellieren konfigurierbare, gefilterte Sichten
auf die Cubes nach dem [cube.link View](https://cube.link/)-Standard.

- **`ld_view_model.py`** – Datenklassen: `View`, `BasicDimension`, `LookupDimension`,
  `Source`, `Attribute`, `Filter`, `FilterOperation`, `ViewMetadata`.
- **`ld_view_builder.py`** – `LdViewBuilder.build_all()` liest die `view_vb_*`-Views
  (`view_vb_view`, `view_vb_source`, `view_vb_dimension`, `view_vb_filter`,
  `view_vb_measure`, `view_vb_room_hierarchy`) und baut daraus `View`-Objekte:
  statische Dimensionen (`ZEIT`, `RAUM`, optional `DATENSTATUS`), Lookup-Dimensionen
  (`_LANG`/`_CODE`/`_SORT`), Filter, Measures und Hierarchien. Ergebnisse werden je View
  gecacht.
- **`ld_view_serializer.py`** – serialisiert ein `View` über mehrere Teil-Templates
  (`ldviews/metadata`, `filters`, `sources`, `dimensions`, `projection`) nach
  `ldviews/view.<id>.ttl`.

Der `ViewsStep` orchestriert Build + Serialisierung + Verpacken (siehe Abschnitt 6).

---

## 10. Konfiguration & Umgebungen

Konfiguriert wird über `config.ini`. Der `[DEFAULT]`-Block liefert Basiswerte, die
Sektionen `[test]`, `[local]`, `[int]`, `[prod]` überschreiben gezielt. Wichtige Keys:

| Key | Bedeutung |
|---|---|
| `db_type` | `mssql` (prod/int) oder `mysql` (lokal/Docker) |
| `db_host`, `db_dbname`, `db_user`, `db_password`, `db_port` | DB-Zugang |
| `output_path` | Basis-Ausgabeverzeichnis |
| `template_output_path` | Zielordner für `.ttl`/`.ttl.gz` |
| `compression_output_path` | Zielordner für gzip (nicht-optimiert) |
| `template_path` | Ordner der Jinja-Templates |
| `optimized` | `true` ⇒ batch-/gzip-optimierte Templating-Steps |
| `only_vb_cubes` | `true` ⇒ Beobachtungen nur für View-Builder-Cubes |
| `start_signal_folder` | Verzeichnis für Start/Stopp-Signaldateien |
| `log.*` | Logging (Level, Format, stdout/Datei) |

`EnvInterpolation` erlaubt das Einsetzen von Umgebungsvariablen in Werte (z.B. Secrets).
Geheimnisse gehören in Umgebungsvariablen bzw. CI-Variablen, **nicht** ins Repo.

---

## 11. Ausführung (CLI, Docker, Skripte)

**Setup**

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

**CLI (Typer, `main.py`)**

```bash
python main.py --help                            # Hilfe
python main.py list-step-names                    # Alle Step-Namen + Beschreibungen
python main.py step --env test --name copyStatic  # Einzelnen Step ausführen
python main.py run test                           # Step-Ablauf (Environment positional)
```

Hinweise:
- Bei `run` ist das Environment ein **positionales** Argument (`run test`), bei `step`
  eine Option (`--env`). Der `--name`-Wert von `step` muss einem Eintrag aus
  `list-step-names` entsprechen.
- Für vollständige Produktivläufe ist **`run_pipeline.py` der maßgebliche Einstiegspunkt**
  (Batching, Signale, Reihenfolge). `main.py run` eignet sich v.a. zum Anstoßen von
  Teilabläufen; die dort verdrahtete Step-Liste sollte vor Gebrauch gegen die Registry in
  `get_step_definitions()` abgeglichen werden.

**Voller orchestrierter Lauf (mit Batching & Signalen)**

```bash
python run_pipeline.py --env int --targetEnv int --runId $(date +%Y%m%d_%H%M%S)
```

**Docker**

```bash
docker build -t ssz/ld-pipeline .
docker run ssz/ld-pipeline --help
docker run --mount type=bind,source="$(pwd)"/tmp,target=/out \
  ssz/ld-pipeline step --env local --name copyStatic
```

> In Docker nur `local`, `int` oder `prod` als Umgebung verwenden.
> Eine lokale Datenbank + Fuseki lassen sich über `compose.yaml` starten.

**Fuseki-Index**

Die Skripte `create_fuseki_index.sh` / `run_fuseki_index.sh` bauen aus den erzeugten
`.gz`-Dateien einen neuen Jena-Fuseki-Index auf (gesteuert über Signaldateien aus
`run_pipeline.py`). `run_pipeline.sh` ist der Signal-Wächter für den geplanten Betrieb.

---

## 12. Tests & CI/CD

**Tests**

```bash
SSZ_DB_TYPE=mock python -m pytest tests/unit                       # Unit-Tests
python -m pytest --container-scope=session tests/integration       # Integration (Docker)
```

Unit-Tests decken u.a. Templating, Jinja-Filter, SQL-Templating, LD-Views, Kompression
und Termset-Hierarchie ab (`tests/unit/`).

**Linting/Format**

```bash
ruff check     # Linting
ruff format    # Formatierung
```

**CI/CD (`.gitlab-ci.yml`)**

Stages `prepare → test → package → publish`:
- `ruff-check`, `ruff-format`, `python-test` (Unit-Tests, Python 3.12) im Test-Stage.
- `sync-to-github`: spiegelt geschützte Branches nach GitHub.
- Integrationstests sind als optionaler Job auskommentiert hinterlegt.

---

## 13. Erweitern der Pipeline

Dieser Abschnitt beschreibt die häufigsten Erweiterungen. Die drei typischen Fälle:
**neuer Step**, **neue Triple-Datei**, **neue Triples im bestehenden Template**.

### 13.1 Neuen Step hinzufügen

1. **Step-Klasse anlegen** in `pipeline/steps/<mein_step>.py`, von `Step` erben und
   `run(self, environment)` implementieren:

   ```python
   from ..base import Step, Environment

   class MeinStep(Step):
       def __init__(self, options=None):
           super().__init__()
           self._options = options or {}

       def run(self, environment: Environment):
           self.logger.info("MeinStep läuft ...")
           # ... Logik, z.B. DB-Zugriff:
           # with environment.get_db_connection() as conn:
           #     with conn.query("SELECT ...") as cursor: ...
   ```

   Braucht der Step DB-Zugriff über SQL-Dateien, von `database.BaseSQLStep` erben und
   `_get_sql_files()` / `render_sql_file()` nutzen.

2. **Exportieren** in `pipeline/steps/__init__.py` (Import + `__all__`).

3. **Registrieren** in `main.get_step_definitions()` als `StepDefinition`:

   ```python
   StepDefinition(
       "meinStep",
       MeinStep(options=options),
       "Kurzbeschreibung des Steps",
   ),
   ```

4. **In den Ablauf einhängen**: entweder in `main.run()` (für `python main.py run`)
   und/oder in `run_pipeline.py` (`pipeline.execute("meinStep")` an passender Stelle).

5. **Testen**: `python main.py step --env test --name meinStep` und einen Unit-Test in
   `tests/unit/` ergänzen.

> Die `Pipeline` ruft ausschließlich `step.run(environment)` auf – ein Step ist damit
> völlig frei in seiner Logik (DB, Datei, HTTP …), solange er diese Signatur erfüllt.

### 13.2 Neue Triple-Datei (Templating-Step) hinzufügen

Soll ein neuer RDF-Datentyp aus einem View erzeugt werden, sind in der Regel **vier**
Artefakte nötig:

1. **DB-View** in `sql/templates/view_definition/view_<name>.sql.jinja` definieren
   (liefert die Spalten, die das Template erwartet). Bei Bedarf zugrundeliegende
   `pipe_*`-Tabelle in `sql/templates/pipe_tables/` ergänzen (siehe 13.4).

   > ⚠️ **Unit-Test:** Für die Laufzeit reicht das Jinja-Template, für grüne Tests müssen
   > aber die gerenderten SQL-Dateien `sql/int/view_definition/view_<name>.sql` **und**
   > `sql/prod/view_definition/view_<name>.sql` committet werden (`test_view_definitions`
   > in `tests/unit/test_sql_templating.py` vergleicht zeichengenau). Fehlen sie, legt der
   > Test sie mit `-- FIXME:`-Header an und schlägt fehl: einmal laufen lassen, prüfen,
   > Header entfernen, erneut testen.

2. **Jinja-Template** in `pipeline/templates/<name>.ttl.jinja` anlegen. Spaltennamen des
   Views als Platzhalter verwenden, Filter `uri_encode`/`literal_encode` einsetzen:

   ```jinja
   <https://ld.stadt-zuerich.ch/statistics/.../{{ id|uri_encode }}> a <...> ;
       <https://schema.org/name> {{ title|literal_encode }} .
   ```

3. **Step registrieren** in `main.get_step_definitions()` über die Factory
   `create_templating(...)`:

   ```python
   StepDefinition(
       "myTypeTemplating",
       create_templating(
           env,
           "my_type.ttl.jinja",   # Template
           "my_type.ttl",         # Ausgabedatei
           "view_my_type",        # Quell-View
           options=options,
       ),
       "Creates triples from view_my_type with the my_type.ttl template",
   ),
   ```

   - Für gruppierte Ausgaben (mehrere Zeilen → ein Triple-Block):
     `options={**options, "grouped": True, "group_by": "<spalte>"}` setzen und ein
     Template schreiben, das über `rows` iteriert (vgl. `time_termset.ttl.jinja`).
   - Müssen Zeilen vor dem Rendern aufgeteilt werden, eine eigene `Templating`-Subklasse
     mit überschriebenem `pre_process(row)` schreiben (Vorbild: `BuildTermsetHierarchy`).

4. **In den Ablauf einhängen**: in `run_pipeline.generate_triple_files()` den Namen zu
   `triple_types_metadata` (bzw. der passenden Liste) hinzufügen und/oder in `main.run()`
   ergänzen.

5. **Verifizieren**: `python main.py step --env test --name myTypeTemplating` und die
   erzeugte `.ttl` prüfen; Unit-Test analog zu `tests/unit/test_templating_step.py`.
   Wurde ein neuer View hinzugefügt, zusätzlich die SQL-Tests laufen lassen:
   `SSZ_DB_TYPE=mock python -m pytest tests/unit/test_sql_templating.py` – dieser
   erzeugt fehlende `int`/`prod`-SQL-Dateien (mit FIXME-Header) und schlägt fehl, bis
   sie geprüft und committet sind.

### 13.3 Neue Triples in bestehendem Template ergänzen

Um einem bestehenden Datentyp zusätzliche Aussagen hinzuzufügen:

1. Sicherstellen, dass die benötigte Spalte aus dem **View** kommt – ggf. die
   `view_<name>.sql.jinja` um die Spalte erweitern (und neu anwenden via
   `createViewsFromSQL`).
2. Im Template (`pipeline/templates/<name>.ttl.jinja`) das zusätzliche Prädikat ergänzen,
   z.B. optional via Bedingung:

   ```jinja
   {% if my_new_field %}
       <https://ld.stadt-zuerich.ch/schema/myProperty> {{ my_new_field|literal_encode }} ;
   {% endif %}
   ```

   Auf korrekte Turtle-Syntax achten (`;` zwischen Prädikaten, `.` am Ende des Subjekts).
3. Erzeugte Datei prüfen und ggf. den zugehörigen Unit-Test/Erwartungsdatei anpassen
   (vgl. `tests/unit/data/expected_view.WIR100OD100A.ttl`).

### 13.4 Neue Quelltabelle / neuen View hinzufügen

1. **Pipe-Table-Template** in `sql/templates/pipe_tables/pipe_<Tabelle>.sql.jinja`
   anlegen (mit `pipe_table_name`/`table_name`-Filtern). Wird automatisch von
   `InitPipeTables` über `_get_sql_files()` eingelesen (alle `*.sql`/`*.sql.jinja` im
   Ordner, sortiert).
2. **View-Template** in `sql/templates/view_definition/` anlegen (siehe 13.2).
3. **Gerenderte SQL für `int` und `prod` committen** (analog 13.2, Test `test_pipe_tables`):
   `sql/int/pipe_tables/<name>.sql` und `sql/prod/pipe_tables/<name>.sql`. Dateiname meist
   identisch zum Template-Basisnamen, bei `pipe_HDB`/`pipe_HDBDatenobjekte` mit Suffix
   (`…_TEST.sql` für `int`, `…_FINAL.sql` für `prod`).
4. Lauf `initPipeTables` → `createViewsFromSQL` ausführen, dann den Templating-Step.

> Reihenfolge beachten: Tabellen vor Views, Views vor Templating. `InitPipeTables` und
> `CreateViewsFromSQL` verarbeiten **alle** Dateien des jeweiligen Ordners alphabetisch –
> bei Abhängigkeiten ggf. über Dateinamen-Präfixe ordnen.

---

## 14. Glossar

| Begriff | Bedeutung |
|---|---|
| **HDB** | Harmonisierte Datenbank der Stadt Zürich (MS SQL Server), Datenquelle. |
| **Triple** | RDF-Aussage `Subjekt – Prädikat – Objekt`; Grundbaustein von Linked Data. |
| **Turtle / `.ttl`** | Textformat für RDF-Triples. |
| **cube.link** | Vokabular zur Modellierung statistischer „Cubes" und Views. |
| **Cube** | Mehrdimensionaler statistischer Datenwürfel (Dimensionen + Measures). |
| **Observation** | Einzelner Datenpunkt eines Cubes (eine Messung). |
| **Termset / DefinedTermSet** | Codeliste / Menge zusammengehöriger Codes. |
| **Pipe-Table** | Aus der HDB aufbereitete Zwischentabelle (`pipe_*`). |
| **View** | DB-Sicht, die genau die Spalten liefert, die ein Template erwartet. |
| **LD-View** | cube.link-View-Definition als RDF (konfigurierbare Datensicht). |
| **Fuseki** | Apache Jena Fuseki, der eingesetzte RDF-Triplestore. |
| **Step** | Atomarer Pipeline-Verarbeitungsschritt (`Step.run`). |
| **optimized** | Batch-/gzip-optimierter Verarbeitungsmodus für große Datenmengen. |

---

*Diese Dokumentation wurde auf Basis des Repository-Stands (Code, SQL, Templates, CI)
erstellt. Bei Code-Änderungen sollten die betroffenen Abschnitte (insb. Step-Tabelle in
Abschnitt 6 und die Erweiterungs-Anleitungen) mitgepflegt werden.*
