import shutil
import unittest
from unittest.mock import Mock

from pipeline.base import Environment, Env
from pipeline.steps.ldview import View, Filter, BasicDimension, LookupDimension, Source, Attribute, FilterOperation, LdViewSerializer
from tests.unit.utils import TestUtils


class TestLdView(unittest.TestCase):

    def test_model(self):
        tmp_dir = TestUtils.abs_path("tmp")

        env = Environment(Env.test)
        env.config.get = Mock(
            side_effect=lambda arg: {
                "template_output_path": tmp_dir,
                "template_path": "../../pipeline/templates/",
            }[arg]
        )

        view = View('VIEW123', 'Test View')

        source = Source("Haushaltsäquivalenzeinkommen", "000610")

        attribute1 = Attribute("Raum (lang)", "RAUM_LANG", "Name der administrativen ...")
        attribute1.position = 1
        attribute2 = Attribute("Raum (code)", "RAUM_CODE", "Code der administrativen ...")
        attribute2.position = 2

        dimension1 = BasicDimension("RAUM", "Key Raum", ["https://ld.stadt-zuerich.ch/statistics/property/RAUM"], None, [source])
        dimension2 = LookupDimension("RAUM_CODE", None, ["http://schema.org/code"], attribute2, dimension1)
        dimension3 = LookupDimension("RAUM_FILTER_1", None, ["http://schema.org/inDefinedTermSet"], None, dimension1)
        dimension4 = LookupDimension("RAUM_LANG", None, ["http://schema.org/name"], attribute1, dimension1)
        view.dimensions.append(dimension1)
        view.dimensions.append(dimension2)
        view.dimensions.append(dimension3)
        view.dimensions.append(dimension4)

        filter1 = Filter("Raum is QuartiereZH", "https://ld.stadt-zuerich.ch/statistics/termset/QuartiereZH", dimension3, FilterOperation.EQ.value)
        view.filters.append(filter1)

        serializer = LdViewSerializer(env)

        try:
            serializer.serialize(view)
        finally:
            shutil.rmtree(tmp_dir)




