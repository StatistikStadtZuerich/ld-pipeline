import os
import shutil
import unittest
from unittest.mock import Mock, MagicMock

from pipeline.base import Environment, Env
from pipeline.steps.ldview import LdViewBuilder, LdViewSerializer
from tests.unit.utils import TestUtils


class TestLdViews(unittest.TestCase):
    def _mock_view_props(self, view_id=None):
        return {
            "id": view_id,
            "name": "Haushaltseinkommen nach ...",
            "include_datenstatus": True,
            "author": None,
            "legal_foundation": None,
            "data_type": None,
            "version": None,
            "description": None,
            "alt_name": None,
            "metadata_creator": None,
            "start_date": None,
            "end_date": None,
            "accrual_periodicity": None,
            "spatial": None,
            "issued": None,
            "modified": None,
            "publisher": None,
            "theme": None,
            "keyword": None,
            "license": None,
            "usage_notes": None,
            "dataquality": None,
        }

    def _mock_database_query(self, query_name, view_id):
        if query_name == "view_vb_view_test":
            return [
                self._mock_view_props("WIR100OD100A"),
                self._mock_view_props("WIR100OD100B"),
            ]
        elif query_name == "view_vb_source_test":
            return [
                {
                    "cube_id": "000610",
                    "name": "Haushaltseinkommen 25%",
                    "view_id": view_id,
                },
                {
                    "cube_id": "000609",
                    "name": "Haushaltseinkommen 50%",
                    "view_id": view_id,
                },
            ]
        elif query_name == "view_vb_filter_test":
            return [
                {"termset": "KreiseZH", "dimension": "RAUM", "view_id": view_id},
                {"termset": "Jahr", "dimension": "ZEIT", "view_id": view_id},
            ]
        elif query_name == "view_vb_dimension_test":
            return [
                {
                    "identifier": "HTY",
                    "name": "Haushaltstyp",
                    "description": "Haushaltstyp nach Haushaltstyp 1",
                    "view_id": view_id,
                }
            ]
        elif query_name == "view_vb_measure_test":
            return [
                {
                    "identifier": "HAE",
                    "identifier_full": "HAE_GGH1400_STK1025",
                    "cube_id": "000610",
                    "name": "Haushaltsäquivalenzeinkommen / Steuerpflichtige Bevölkerung / 25%-Perzentil",
                    "description": "Haushaltsäquivalenzeinkommen: Für die Berechnung wird die Haushaltsgrösse über die Äquivalenzskala ...",
                    "view_id": view_id,
                },
                {
                    "identifier": "HAE",
                    "identifier_full": "HAE_GGH1400_STK1050",
                    "cube_id": "000609",
                    "name": "Haushaltsäquivalenzeinkommen / Steuerpflichtige Bevölkerung / 50%-Perzentil",
                    "description": "Haushaltsäquivalenzeinkommen: Für die Berechnung wird die Haushaltsgrösse über die Äquivalenzskala ...",
                    "view_id": view_id,
                },
            ]
        elif query_name == "view_vb_room_hierarchy_test":
            return [
                {"termset": "KreiseZH", "dimension": "RAUM", "view_id": view_id},
                {"termset": "QuartiereZH", "dimension": "RAUM", "view_id": view_id},
            ]
        else:
            raise Exception(f"query {query_name} not properly mocked for test")

    def test_view_building(self):
        tmp_dir = TestUtils.abs_path("tmp")
        os.makedirs(tmp_dir, exist_ok=True)

        env = Environment(Env.test)
        env.config.get = Mock(
            side_effect=lambda arg: {
                "template_output_path": TestUtils.abs_path("tmp"),
                "template_path": TestUtils.abs_path("../../pipeline/templates"),
            }[arg]
        )

        try:
            view_builder = LdViewBuilder(env, "test")
            view_builder._get_view_data = MagicMock(
                side_effect=self._mock_database_query
            )

            views = view_builder.build_all()
            self.assertEqual(2, len(views))

            serializer = LdViewSerializer(env)
            serializer.serialize(views[0])
            serializer.serialize(views[1])

            content = open(
                os.path.join(TestUtils.abs_path("tmp"), "ldviews/view.WIR100OD100A.ttl")
            ).read()
            content2 = open(
                os.path.join(TestUtils.abs_path("tmp"), "ldviews/view.WIR100OD100B.ttl")
            ).read()

            expected_content = open(
                TestUtils.abs_path("data/expected_view.WIR100OD100A.ttl")
            ).read()
            expected_content2 = expected_content.replace("WIR100OD100A", "WIR100OD100B")

            self.assertEqual(content, expected_content)
            self.assertEqual(content2, expected_content2)

        finally:
            shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    unittest.main()
