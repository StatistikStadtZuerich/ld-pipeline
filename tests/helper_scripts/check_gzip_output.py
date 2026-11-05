"""
GZIP-Output pruefen: Vollstaendigkeit & Struktur (Testfall TF-12).

HINTERGRUND:
Im optimierten Pipeline-Modus (optimized=true, aktiv in int/prod) schreibt der
Schritt templating_optimized.py (TemplatingOptimized / GroupedTemplatingOptimized)
die Ergebnisse nicht als eine grosse .ttl-Datei, sondern batchweise direkt als
gezippte Dateien (<typ>_batchNNN.ttl.gz) in den Ordner output/<env>/.

Ein separates, entkoppeltes Shell-Skript (create_fuseki_index.sh) holt sich diese
Dateien irgendwann automatisch aus diesem Ordner (verschiebt sie!), kombiniert sie
zu einer einzigen Datei und laedt sie in die Fuseki-Datenbank. Danach liegen dort
keine einzelnen RDF/TTL-Dateien mehr. Deshalb: diesen Ordner IMMER zeitnah nach
einem Pipeline-Lauf pruefen, bevor der Fuseki-Index-Bau angestossen wird.

WAS DIESES SCRIPT PRUEFT:
    1) Sind alle erwarteten Typen (code, cube, observation, ...) ueberhaupt da?
    2) Ist jede Datei ein valides Gzip-Archiv mit korrektem Dateinamen-Schema?
    3) Gibt es keine fehlenden UND keine unerwarteten/ueberzaehligen Dateien?


AUSFUEHREN (im Repo-Root von ld-pipeline, damit der Standardpfad "output/int" passt):
    python tests/helper_scripts/check_gzip_output.py                # schneller Check (nur Gzip-Header)
    python tests/helper_scripts/check_gzip_output.py --deep         # liest jede Datei komplett durch
                                                                    # (erkennt auch abgeschnittene/
                                                                    # korrupte Dateien, dauert laenger)
    python tests/helper_scripts/check_gzip_output.py --verbose      # zusaetzlich 1 Zeile pro Datei
    python tests/helper_scripts/check_gzip_output.py <anderer_pfad> # statt output/int einen anderen
                                                                    # Ordner pruefen
"""

import contextlib
import gzip
import os
import re
import sys
import zlib
from collections import defaultdict

# Windows-Konsolen zeigen standardmaessig oft noch das alte cp1252-Encoding an statt
# UTF-8. Ohne diese Zeile wuerde print() mit einem UnicodeEncodeError abstuerzen,
# sobald wir die Haekchen-/Kreuz-Symbole (u2713 / u2717) ausgeben wollen.
# Falls stdout kein reconfigure() unterstuetzt (AttributeError, z.B. wenn stdout
# durch ein anderes Objekt ersetzt wurde) oder das Encoding nicht mehr geaendert
# werden kann (ValueError / io.UnsupportedOperation), einfach weitermachen.
# Im schlimmsten Fall werden dann eben keine huebschen Symbole angezeigt.
with contextlib.suppress(AttributeError, ValueError):
    sys.stdout.reconfigure(encoding="utf-8")

# Standardordner: "output/int" relativ zum Verzeichnis, aus dem das Script gestartet
# wird (nicht relativ zum Speicherort der Datei selbst!). Das Script laeuft normal
# aus dem Repo-Root heraus, darum funktioniert dieser relative Pfad im Alltag.
DEFAULT_FOLDER = os.path.join(os.getcwd(), "output", "int")

# ---------------------------------------------------------------------------
# KONFIGURATION - diese zwei Listen bei Bedarf anpassen
# ---------------------------------------------------------------------------

# Welche "Basisnamen" (= Typen) MUESSEN im Ordner vorkommen, damit Punkt 1
# ("Vollstaendigkeit") als erfuellt gilt. Abgeleitet aus main.py bzw. aus dem, was
# die triple_types_*-Listen in notebooks/ld_pipeline.ipynb (Zelle 4) tatsaechlich
# erzeugen. "group_termset" und "time_relation_termset" sind zwar als eigene Steps
# in main.py vorhanden, werden dort aber aktuell NICHT aufgerufen - deshalb bewusst
# nicht in dieser Liste. "ldview_*" (aus dem generateViews-Schritt) wird separat
# behandelt, da dort pro View eine eigene Datei mit wechselndem Namen entsteht
# (ldview_<view-id>.ttl.gz) - eine feste Namensliste waere hier nicht sinnvoll.
EXPECTED_TYPES = [
    "static",
    "info",
    "termset_hierarchy",
    "code",
    "cube",
    "group_code",
    "hierarchy",
    "measure_unit",
    "measure",
    "observation",
    "property",
    "room",
    "time",
    "time_termset",
    "termset_dimension_hierarchy",
]

# Typen, die in einem KONKRETEN Testlauf bereits einmal nachweislich 0 Zeilen aus
# der Datenbank geliefert haben (im Pipeline-Log sichtbar als "No rows left.").
# Fehlt so ein Typ im Output, ist das kein Bug (kein Batch = korrektes Verhalten
# bei leerer Ergebnismenge), sondern erwartet. Das Script zaehlt einen Typ aus
# dieser Liste bei Punkt 1 darum NICHT als Fehler, sondern weist ihn separat als
# "bestaetigt leer" aus.
#
# WICHTIG: Das gilt nur so lange, wie es wirklich zutrifft! Vor jedem neuen
# Testlauf im Pipeline-Log nachschauen, ob die betroffene View wirklich (noch)
# leer ist - sonst wird ein echtes, neues Problem faelschlich als "bekannt und ok"
# durchgewunken.
KNOWN_EMPTY_TYPES = ["termset_dimension_hierarchy"]

# Die ersten 2 Bytes jeder gueltigen Gzip-Datei sind immer exakt diese beiden Werte
# (der sogenannte "Magic Number" / Datei-Signatur). Damit lässt sich sehr schnell
# pruefen, ob eine Datei ueberhaupt ein Gzip-Archiv ist, ohne sie zu entpacken.
GZIP_MAGIC = b"\x1f\x8b"

# Eine "leere" Gzip-Datei (0 Bytes Inhalt gepackt) ist trotzdem nie kleiner als ca.
# 20 Bytes, weil der Gzip-Header selbst schon Platz braucht. Eine Datei, die noch
# kleiner ist, kann also gar kein plausibles Gzip-Archiv sein.
MIN_PLAUSIBLE_SIZE = 20

# ---------------------------------------------------------------------------
# Farbige Ausgabe (grün/rot) vorbereiten
# ---------------------------------------------------------------------------
_USE_COLOR = sys.stdout.isatty()

if _USE_COLOR and sys.platform == "win32":
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except (AttributeError, OSError):
        # Falls das fehlschlaegt (z.B. altes Windows, eingeschraenkte Rechte):
        # einfach ohne Farbe weitermachen statt abzustuerzen.
        _USE_COLOR = False


def format_pass_fail(is_ok: bool) -> str:
    """
    Formatiert True/False als lesbares "PASS"/"FAIL" mit Haekchen bzw. Kreuz-Symbol,
    und - falls das Terminal es unterstuetzt - zusaetzlich in gruen bzw. rot.
    """
    symbol = "✓" if is_ok else "✗"  # Haekchen (✓) bzw. Kreuz (✗)
    label = "PASS" if is_ok else "FAIL"

    if not _USE_COLOR:
        return f"{symbol} {label}"

    green = "\033[92m"
    red = "\033[91m"
    bold = "\033[1m"
    reset = "\033[0m"  # setzt Farbe/Fettschrift wieder zurueck auf normal
    color = green if is_ok else red
    return f"{color}{bold}{symbol} {label}{reset}"


def check_gzip_content(
    path: str, chunk_size: int = 8 * 1024 * 1024
) -> tuple[bool, str]:
    """
    "Deep Check": entpackt die komplette Datei (in 8-MB-Stuecken, damit auch sehr
    grosse Dateien nicht komplett in den Arbeitsspeicher geladen werden muessen)
    und prueft dabei, ob das ueberhaupt fehlerfrei funktioniert.

    Das erkennt Faelle, die der schnelle Header-Check (nur die ersten 2 Bytes)
    NICHT erkennt: z.B. eine Datei, die mitten beim Schreiben abgebrochen wurde
    und darum am Ende unvollstaendig/kaputt ist. Der Gzip-Header am Anfang der
    Datei kann dabei trotzdem völlig intakt sein.

    Gibt (True, "") zurueck bei Erfolg, sonst (False, "<Fehlermeldung>").
    """
    try:
        with gzip.open(path, "rb") as gz_file:
            total_bytes = 0
            while True:
                chunk = gz_file.read(chunk_size)
                if not chunk:
                    # read() liefert einen leeren bytes-Wert, wenn das Dateiende
                    # erreicht ist - das ist hier der normale Abbruch der Schleife.
                    break
                total_bytes += len(chunk)

        if total_bytes == 0:
            return False, "entpackter Inhalt ist leer"
        return True, ""

    except (OSError, EOFError, zlib.error) as e:
        # gzip.open()/read() wirft gzip.BadGzipFile (Unterklasse von OSError),
        # EOFError (Datei abgeschnitten) oder zlib.error (korrupte Daten).
        # OSError deckt zusaetzlich Lesefehler wie fehlende Rechte ab. Damit
        # bricht ein einzelner kaputter Fund nicht den gesamten Testlauf ab -
        # der Fehler wird stattdessen als Text zurueckgegeben und im Bericht
        # angezeigt.
        return False, str(e)


def check_gzip_output(
    folder: str,
    expected_types: list[str] | None = None,
    known_empty_types: list[str] | None = None,
    deep: bool = False,
    verbose: bool = False,
) -> dict:
    """
    Hauptfunktion: prueft alle .gz-Dateien in `folder` und gibt einen Bericht auf
    der Konsole aus (siehe Modul-Docstring oben fuer die 3 geprueften Punkte).

    Parameter:
        folder          - der zu pruefende Ordner (z.B. output/int)
        expected_types  - Liste der Typen, die vorhanden sein muessen
                           (None = es wird nichts als "fehlend" gewertet,
                           einfach nur das gemeldet, was gefunden wurde)
        known_empty_types - Typen, die bekanntermassen leer sein duerfen
                             (siehe Erklaerung bei KNOWN_EMPTY_TYPES oben)
        deep            - True = jede Datei komplett entpacken und pruefen
                           (langsamer, aber gruendlicher)
        verbose         - True = zusaetzlich eine Fortschrittszeile pro Datei

    Rueckgabe: ein Dict mit dem Gesamtergebnis, praktisch falls man die Funktion
    aus einem anderen Python-Skript heraus aufrufen und das Ergebnis
    weiterverarbeiten moechte, statt nur die Konsolen-Ausgabe zu lesen.
    """

    # Zwei Muster, um aus einem Dateinamen den "Typ" (Basisname) herauszulesen:
    #   batch_pattern erkennt z.B. "code_batch001.ttl.gz" -> Typ "code", Nummer 1
    #   single_pattern erkennt z.B. "static.ttl.gz"        -> Typ "static"
    # (?P<name>...) ist eine "benannte Gruppe" - damit koennen wir spaeter per
    # match.group("typ") bzw. match.group("nummer") gezielt darauf zugreifen,
    # statt uns nur auf die Reihenfolge der Gruppen verlassen zu muessen.
    batch_pattern = re.compile(r"^(?P<typ>.+)_batch(?P<nummer>\d{3})\.ttl\.gz$")
    single_pattern = re.compile(r"^(?P<typ>.+)\.ttl\.gz$")

    # Alle Dateien im Ordner einlesen, die auf ".gz" enden - alphabetisch sortiert,
    # damit die Ausgabe reproduzierbar/gut lesbar ist.
    entries = sorted(f for f in os.listdir(folder) if f.endswith(".gz"))

    # Sammelstellen fuer die Auswertung, waehrend wir durch die Dateien gehen:
    batch_groups: dict[str, list[int]] = defaultdict(
        list
    )  # Typ -> Liste der Batch-Nummern
    single_types: set[str] = set()  # Typen ohne Batch-Nummer (z.B. "static")
    ldview_files: list[str] = []  # generateViews-Dateien, separat gezaehlt
    structure_errors: list[str] = []  # alles, was bei Punkt 2 ("Struktur") schiefgeht

    # ---------------------------------------------------------------
    # Schritt A: jede Datei einzeln pruefen (Struktur) und einsortieren
    # ---------------------------------------------------------------
    for index, filename in enumerate(entries, start=1):
        full_path = os.path.join(folder, filename)
        size_kb = os.path.getsize(full_path) / 1024

        if verbose:
            print(
                f"[{index}/{len(entries)}] {filename} ({size_kb:,.1f} KB) ...",
                end=" ",
                flush=True,
            )

        # A.1: Ist die Datei ueberhaupt gross genug, um ein plausibles Gzip zu sein?
        if os.path.getsize(full_path) < MIN_PLAUSIBLE_SIZE:
            structure_errors.append(f"{filename}: Datei verdaechtig klein/leer")
            if verbose:
                print("FEHLER (zu klein)")
            continue  # weiter zur naechsten Datei, diese hier ist schon als Fehler erfasst

        # A.2: Stimmt der Gzip-Header (die ersten 2 Bytes)? Das ist der schnelle
        # Standard-Check und reicht in den meisten Faellen aus.
        with open(full_path, "rb") as raw_file:
            header_ok = raw_file.read(2) == GZIP_MAGIC
        if not header_ok:
            structure_errors.append(f"{filename}: kein gueltiger Gzip-Header")
            if verbose:
                print("FEHLER (Header)")
            continue

        # A.3: Nur wenn --deep angegeben wurde, zusaetzlich die komplette Datei
        # entpacken (siehe check_gzip_content() weiter oben fuer die Begruendung).
        if deep:
            is_ok, error_message = check_gzip_content(full_path)
            if not is_ok:
                structure_errors.append(f"{filename}: {error_message}")
                if verbose:
                    print("FEHLER (Inhalt)")
                continue
            if verbose:
                print("OK (Inhalt geprueft)")
        elif verbose:
            print("OK (nur Header)")

        # A.4: Datei hat alle Struktur-Checks bestanden - jetzt anhand des
        # Dateinamens dem passenden "Typ" zuordnen.
        if filename.startswith("ldview_"):
            # generateViews-Dateien haben pro View einen eigenen, wechselnden Namen
            # (z.B. ldview_BEV411OD411A.ttl.gz) - die zaehlen wir separat als
            # Gruppe, nicht als eigenen "erwarteten Typ" mit festem Namen.
            ldview_files.append(filename)
            continue

        batch_match = batch_pattern.match(filename)
        if batch_match:
            # z.B. "code_batch001.ttl.gz" -> Typ "code" bekommt die Nummer 1
            # hinzugefuegt. So sammeln wir pro Typ alle vorkommenden Batch-Nummern.
            typ = batch_match.group("typ")
            nummer = int(batch_match.group("nummer"))
            batch_groups[typ].append(nummer)
            continue

        single_match = single_pattern.match(filename)
        if single_match:
            # z.B. "static.ttl.gz" - ein Typ ohne Batch-Nummerierung (nur 1 Datei
            # insgesamt erwartet).
            single_types.add(single_match.group("typ"))
            continue

        # Kein Muster hat gepasst - der Dateiname folgt keinem der bekannten Schemata.
        structure_errors.append(f"{filename}: unerwartetes Namensschema")

    # ---------------------------------------------------------------
    # Schritt B: Batch-Nummerierung pruefen (pro Typ mit mehreren Dateien)
    # ---------------------------------------------------------------
    # Fuer jeden Typ mit Batch-Dateien muss die Nummerierung bei 1 beginnen und
    # ohne Luecke hochzaehlen (1, 2, 3, ... - nicht z.B. 1, 3 mit fehlender 2).
    naming_errors: list[str] = []
    for typ, batch_numbers in batch_groups.items():
        sorted_numbers = sorted(batch_numbers)
        expected_sequence = list(range(1, len(sorted_numbers) + 1))
        if sorted_numbers != expected_sequence:
            naming_errors.append(
                f"{typ}: Batch-Nummerierung nicht lueckenlos: {sorted_numbers}"
            )

    # ---------------------------------------------------------------
    # Schritt C: Vollstaendigkeit auswerten (Mengen-Vergleich)
    # ---------------------------------------------------------------
    # "found" = alle Typen, die wir tatsaechlich im Ordner gefunden haben
    # (sowohl mit Batch-Nummern als auch die "single"-Typen wie static/info).
    found_types = set(batch_groups.keys()) | single_types

    # Wurde keine explizite Erwartungsliste uebergeben, vergleichen wir "found"
    # praktisch mit sich selbst - dann kann nichts als fehlend/unerwartet auffallen,
    # das Script prueft in diesem Fall nur noch die Struktur (Punkt 2).
    expected_types_set = (
        set(expected_types) if expected_types is not None else found_types
    )

    known_empty_set = set(known_empty_types or [])

    # Mengen-Differenz: was steht in "expected", fehlt aber in "found"?
    all_missing = expected_types_set - found_types
    # Davon: welche sind bereits bekannt/bestaetigt leer (kein Fehler)...
    missing_confirmed_empty = all_missing & known_empty_set
    # ...und welche sind unerklaert fehlend (das IST ein Fehler)?
    missing_unexplained = all_missing - known_empty_set

    # Umgekehrte Mengen-Differenz: was wurde gefunden, stand aber gar nicht auf
    # der Erwartungsliste? (z.B. ein Tippfehler im Dateinamen, oder ein neuer,
    # noch nicht in EXPECTED_TYPES eingetragener Typ)
    unexpected_types = found_types - expected_types_set

    # ---------------------------------------------------------------
    # Schritt D: die 3 Checks verdichten
    # ---------------------------------------------------------------
    structure_ok = not structure_errors and not naming_errors
    completeness_ok = not missing_unexplained
    no_extra_files_ok = not unexpected_types
    overall_pass = structure_ok and completeness_ok and no_extra_files_ok

    # ---------------------------------------------------------------
    # Schritt E: Bericht auf der Konsole ausgeben
    # ---------------------------------------------------------------
    print("=" * 72)
    print(" GZIP-Output: Vollstaendigkeit & Struktur")
    print("=" * 72)
    print(f"Ordner:  {folder}")
    print(
        f"Dateien: {len(entries)} .gz insgesamt "
        f"({len(found_types)} Typen"
        f"{f' + {len(ldview_files)}x ldview_*' if ldview_files else ''})"
    )
    print(
        f"Modus:   {'DEEP (vollstaendige Dekompression)' if deep else 'FAST (nur Gzip-Header)'}"
    )
    print("-" * 72)

    # Punkt 1: Vollstaendigkeit
    print(
        f"1) Alle erwarteten RDF/TTL-Files enthalten ..... {format_pass_fail(completeness_ok)}"
    )
    if missing_confirmed_empty:
        print(
            f"     bestaetigt leer (kein Fehler): {', '.join(sorted(missing_confirmed_empty))}"
        )
    if missing_unexplained:
        print(f"     FEHLEND: {', '.join(sorted(missing_unexplained))}")

    # Punkt 2: Struktur (Gzip-Validitaet + Namensschema + Batch-Nummerierung)
    print(
        f"2) Struktur entspricht der Vorgabe (Gzip + Namensschema) ... {format_pass_fail(structure_ok)}"
    )
    if structure_errors or naming_errors:
        for error in structure_errors + naming_errors:
            print(f"     - {error}")
    else:
        print(f"     alle {len(entries)} Dateien valide, Batch-Nummerierung lueckenlos")

    # Punkt 3: keine fehlenden UND keine unerwarteten Dateien
    print(
        f"3) Keine fehlenden / keine ueberzaehligen Dateien ... {format_pass_fail(completeness_ok and no_extra_files_ok)}"
    )
    if unexpected_types:
        print(f"     UNERWARTET: {', '.join(sorted(unexpected_types))}")
    elif not missing_unexplained:
        print("     keine Abweichungen")

    print("-" * 72)
    print(f"GESAMTERGEBNIS: {format_pass_fail(overall_pass)}")
    print("=" * 72)

    # Zusatzinfo am Ende: praktisch zum schnellen Ueberfliegen bzw. zum Copy-Paste
    # in einen Testbericht.
    print("\nGefundene Typen und Batch-Anzahl:")
    for typ in sorted(found_types):
        batch_count = len(batch_groups.get(typ, [])) or "1 (Einzeldatei)"
        print(f"  - {typ}: {batch_count}")
    if ldview_files:
        print(f"  - ldview_*: {len(ldview_files)} Dateien")

    # Ergebnis zusaetzlich als Dict zurueckgeben, falls die Funktion nicht per
    # Kommandozeile, sondern aus anderem Python-Code heraus aufgerufen wird.
    return {
        "overall_pass": overall_pass,
        "found_types": sorted(found_types),
        "batch_counts": {typ: len(nums) for typ, nums in batch_groups.items()},
        "ldview_files": sorted(ldview_files),
        "structure_errors": structure_errors + naming_errors,
        "missing_confirmed_empty": sorted(missing_confirmed_empty),
        "missing_unexplained": sorted(missing_unexplained),
        "unexpected_types": sorted(unexpected_types),
    }


# Dieser Block laeuft nur, wenn die Datei direkt per
# "python tests/helper_scripts/check_gzip_output.py" gestartet wird (nicht, wenn sie aus einem anderen Skript importiert wird).
if __name__ == "__main__":
    command_line_args = sys.argv[
        1:
    ]  # sys.argv[0] ist der Skriptname selbst, daher ab Index 1

    deep_mode = "--deep" in command_line_args
    verbose_mode = "--verbose" in command_line_args

    # Alles, was kein "--deep"/"--verbose"-Flag ist, wird als Ordnerpfad behandelt.
    # Falls kein solches Argument uebergeben wurde, den Standardordner verwenden.
    path_arguments = [a for a in command_line_args if a not in ("--deep", "--verbose")]
    target_folder = path_arguments[0] if path_arguments else DEFAULT_FOLDER

    check_gzip_output(
        target_folder,
        expected_types=EXPECTED_TYPES,
        known_empty_types=KNOWN_EMPTY_TYPES,
        deep=deep_mode,
        verbose=verbose_mode,
    )
