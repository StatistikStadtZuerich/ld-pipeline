import gzip
import os
import shutil
from unittest.mock import MagicMock, Mock

from pipeline.base import Env, Environment
from pipeline.steps import TemplatingOptimized
from pipeline.steps.templating import OutputType
from tests.unit.utils import TestUtils


def test_templating_optimized_writes_complete_and_valid_gzip():
    tmp_dir = TestUtils.abs_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    env = Environment(Env.test)
    env.config.get = Mock(
        side_effect=lambda name, _return_type=str, fallback=None: {
            "template_output_path": TestUtils.abs_path("tmp"),
            "template_path": TestUtils.abs_path("data"),
        }.get(name, fallback)
    )
    env.get_db_connection = MagicMock()
    cursor = env.get_db_connection().__enter__().cursor().__enter__()
    # 1. Fetch liefert die Daten, 2. Fetch ist leer -> Ende der Daten
    cursor.fetchall.side_effect = [
        [
            {"property_code": "ÜBG", "title": "Arbeitslosengrad   "},
            {"property_code": "ABT", "title": "Abteilung"},
        ],
        [],
    ]

    sql_filepath = TestUtils.abs_path("data/sample.sql")
    template_filename = "template.ttl.jinja"
    output_filename = "test_output.ttl"
    output_dir = os.path.join(tmp_dir, OutputType.SHARED)

    try:
        TemplatingOptimized(
            template_filename,
            output_filename,
            "view_property",
            OutputType.SHARED,
            sql_filepath=sql_filepath,
        ).run(env)

        # Genau eine Batch-Datei mit korrektem Namen, keine weiteren Dateien
        assert os.listdir(output_dir) == ["test_output_batch001.ttl.gz"]

        # Valide Gzip-Struktur: Gzip-Header vorhanden
        output_filepath = os.path.join(output_dir, "test_output_batch001.ttl.gz")
        with open(output_filepath, "rb") as f:
            assert f.read(2) == b"\x1f\x8b"

        # Vollstaendigkeit: Datei laesst sich komplett entpacken und enthaelt
        # die Triples aller Zeilen (Turtle ist UTF-8)
        with gzip.open(output_filepath, "rt", encoding="utf-8") as generated:
            content = generated.read()
        expected_content = TestUtils.read_file(
            TestUtils.abs_path("data/expected_content.ttl"), encoding="utf-8"
        )
        TestUtils.assert_text_equals(expected_content, content)

    finally:
        shutil.rmtree(tmp_dir)
