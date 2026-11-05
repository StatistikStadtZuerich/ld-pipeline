import gzip
import os
import shutil
from unittest.mock import MagicMock, Mock

from rdflib import Graph, Namespace
from rdflib.compare import graph_diff, isomorphic, to_isomorphic

from pipeline.base import Env, Environment
from pipeline.steps import TemplatingOptimized
from pipeline.steps.templating import OutputType
from pipeline.steps.templating_optimized import GroupedTemplatingOptimized
from tests.unit.utils import TestUtils


def _create_environment(
    fetch_results: list[list[dict]],
) -> tuple[Environment, MagicMock]:
    env = Environment(Env.test)
    env.config.get = Mock(
        side_effect=lambda name, _return_type=str, fallback=None: {
            "template_output_path": TestUtils.abs_path("tmp"),
            "template_path": TestUtils.abs_path("data"),
        }.get(name, fallback)
    )
    env.get_db_connection = MagicMock()
    cursor = env.get_db_connection().__enter__().cursor().__enter__()
    cursor.fetchall.side_effect = fetch_results
    return env, cursor


def _read_graph(filepath: str) -> Graph:
    with gzip.open(filepath, "rt", encoding="utf-8") as generated:
        return Graph().parse(data=generated.read(), format="turtle")


def _local_name(uri) -> str:
    return str(uri).rsplit("/", 1)[-1]


SCHEMA = Namespace("https://schema.org/")


def test_templating_optimized_writes_complete_and_valid_gzip():
    tmp_dir = TestUtils.abs_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    env, _ = _create_environment(
        [
            [
                {"property_code": "ÜBG", "title": "Arbeitslosengrad   "},
                {"property_code": "ABT", "title": "Abteilung"},
            ],
            [],
        ]
    )

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

        assert os.listdir(output_dir) == ["test_output_batch001.ttl.gz"]

        output_filepath = os.path.join(output_dir, "test_output_batch001.ttl.gz")
        actual_graph = _read_graph(output_filepath)
        expected_graph = Graph().parse(
            TestUtils.abs_path("data/expected_content.ttl"),
            format="turtle",
            encoding="utf-8",
        )
        _, only_expected, only_actual = graph_diff(
            to_isomorphic(expected_graph), to_isomorphic(actual_graph)
        )
        assert isomorphic(expected_graph, actual_graph), (
            f"Fehlende Triples:\n{only_expected.serialize(format='nt')}\n"
            f"Unerwartete Triples:\n{only_actual.serialize(format='nt')}"
        )

    finally:
        shutil.rmtree(tmp_dir)


def test_templating_optimized_splits_batches_correctly():
    tmp_dir = TestUtils.abs_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    env, _ = _create_environment(
        [
            [
                {"property_code": "P1", "title": "Titel 1"},
                {"property_code": "P2", "title": "Titel 2"},
            ],
            [
                {"property_code": "P3", "title": "Titel 3"},
                {"property_code": "P4", "title": "Titel 4"},
            ],
            [
                {"property_code": "P5", "title": "Titel 5"},
            ],
            [],
        ]
    )

    sql_filepath = TestUtils.abs_path("data/sample.sql")
    template_filename = "template.ttl.jinja"
    output_filename = "test_output.ttl"
    output_dir = os.path.join(tmp_dir, OutputType.SHARED)

    def read_property_codes(filename: str) -> list[str]:
        graph = _read_graph(os.path.join(output_dir, filename))
        return sorted(str(code) for code in graph.objects(None, SCHEMA.identifier))

    try:
        TemplatingOptimized(
            template_filename,
            output_filename,
            "view_property",
            OutputType.SHARED,
            sql_filepath=sql_filepath,
            options={"db_batch_size": 2, "write_batch_size": 2},
        ).run(env)

        assert sorted(os.listdir(output_dir)) == [
            "test_output_batch001.ttl.gz",
            "test_output_batch002.ttl.gz",
            "test_output_batch003.ttl.gz",
        ]

        assert read_property_codes("test_output_batch001.ttl.gz") == ["P1", "P2"]
        assert read_property_codes("test_output_batch002.ttl.gz") == ["P3", "P4"]
        assert read_property_codes("test_output_batch003.ttl.gz") == ["P5"]

    finally:
        shutil.rmtree(tmp_dir)


def test_templating_optimized_empty_result_writes_no_file():
    tmp_dir = TestUtils.abs_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    env, cursor = _create_environment([[]])

    sql_filepath = TestUtils.abs_path("data/sample.sql")
    template_filename = "template.ttl.jinja"
    output_filename = "test_output.ttl"

    try:
        TemplatingOptimized(
            template_filename,
            output_filename,
            "view_property",
            OutputType.SHARED,
            sql_filepath=sql_filepath,
        ).run(env)

        assert cursor.fetchall.call_count == 1

        output_files = [
            filename for _, _, filenames in os.walk(tmp_dir) for filename in filenames
        ]
        assert output_files == []

    finally:
        shutil.rmtree(tmp_dir)


def test_grouped_templating_optimized_keeps_group_across_fetch_boundary():
    tmp_dir = TestUtils.abs_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    env, _ = _create_environment(
        [
            [
                {"termset_code": "T1", "code": "A"},
                {"termset_code": "T1", "code": "B"},
                {"termset_code": "T2", "code": "C"},
            ],
            [
                {"termset_code": "T2", "code": "D"},
                {"termset_code": "T2", "code": "E"},
                {"termset_code": "T3", "code": "F"},
            ],
            [],
        ]
    )

    sql_filepath = TestUtils.abs_path("data/sample.sql")
    template_filename = "grouped_template.ttl.jinja"
    output_filename = "test_output.ttl"
    output_dir = os.path.join(tmp_dir, OutputType.SHARED)

    def read_groups(filename: str) -> dict[str, list[str]]:
        graph = _read_graph(os.path.join(output_dir, filename))
        return {
            _local_name(termset): sorted(
                _local_name(code) for code in graph.objects(termset, SCHEMA.hasPart)
            )
            for termset in set(graph.subjects(SCHEMA.hasPart, None))
        }

    try:
        GroupedTemplatingOptimized(
            template_filename,
            output_filename,
            "view_time_termset",
            OutputType.SHARED,
            sql_filepath=sql_filepath,
            options={
                "group_by": "termset_code",
                "db_batch_size": 3,
                "write_batch_size": 1,
            },
        ).run(env)

        assert sorted(os.listdir(output_dir)) == [
            "test_output_batch001.ttl.gz",
            "test_output_batch002.ttl.gz",
            "test_output_batch003.ttl.gz",
        ]

        assert read_groups("test_output_batch001.ttl.gz") == {"T1": ["A", "B"]}
        assert read_groups("test_output_batch002.ttl.gz") == {"T2": ["C", "D", "E"]}
        assert read_groups("test_output_batch003.ttl.gz") == {"T3": ["F"]}

    finally:
        shutil.rmtree(tmp_dir)


def test_templating_optimized_leaves_no_leftover_files_on_success():
    tmp_dir = TestUtils.abs_path("tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    env, _ = _create_environment(
        [
            [
                {"property_code": "P1", "title": "Titel 1"},
                {"property_code": "P2", "title": "Titel 2"},
            ],
            [
                {"property_code": "P3", "title": "Titel 3"},
            ],
            [],
        ]
    )

    sql_filepath = TestUtils.abs_path("data/sample.sql")
    template_filename = "template.ttl.jinja"
    output_filename = "test_output.ttl"

    try:
        TemplatingOptimized(
            template_filename,
            output_filename,
            "view_property",
            OutputType.SHARED,
            sql_filepath=sql_filepath,
            options={"db_batch_size": 2, "write_batch_size": 2},
        ).run(env)

        output_entries = sorted(
            os.path.relpath(os.path.join(dirpath, name), tmp_dir).replace("\\", "/")
            for dirpath, dirnames, filenames in os.walk(tmp_dir)
            for name in dirnames + filenames
        )
        assert output_entries == [
            "shared",
            "shared/test_output_batch001.ttl.gz",
            "shared/test_output_batch002.ttl.gz",
        ]

    finally:
        shutil.rmtree(tmp_dir)
