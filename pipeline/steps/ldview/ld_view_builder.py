from abc import ABC
from typing import List

from pipeline.base import Environment
from pipeline.steps.ldview import View, BasicDimension, Source, LookupDimension, Attribute, ViewMetadata, Filter, FilterOperation


class LdViewBuilder(ABC):
    def __init__(self, environment: Environment, env):
        self._environment = environment
        self._env = env

    def build_all(self) -> List[View]:
        views = []
        for view_dict in self._list_views():
            view = self._create_view_from_dict(view_dict)

            source_dict_list = self._list_sources_by_view_id(view.id)
            sources = [self._create_source_from_dict(source_dict) for source_dict in source_dict_list]

            basic_dimension_plus_dzeit_and_draum = self._get_static_dimensions(view, sources)
            view.dimensions.extend(basic_dimension_plus_dzeit_and_draum[0])

            dimension_zeit = basic_dimension_plus_dzeit_and_draum[1]
            dimension_raum = basic_dimension_plus_dzeit_and_draum[2]

            filter_dict_list = self._list_filters_by_view_id(view.id)
            for filter_dict in filter_dict_list:
                filter_and_dimension = self._create_filter_from_dict(filter_dict, dimension_zeit, dimension_raum)
                view.filters.append(filter_and_dimension[0])
                view.dimensions.append(filter_and_dimension[1])

            dimension_dict_list = self._list_dimensions_by_view_id(view.id)
            for dimension_dict in dimension_dict_list:
                view.dimensions.extend(self._create_dimensions_from_dimension_dict(dimension_dict, sources))

            measurement_dict_list = self._list_measurements_by_view_id(view.id)
            for measurement_dict in measurement_dict_list:
                view.dimensions.append(self._create_measurement_from_dimension_dict(measurement_dict, sources))

            views.append(view)

        return views

    ###### STATIC ########
    def _get_static_dimensions(self, view, sources):
        dz = BasicDimension("ZEIT", "Zeit Raum", ["https://ld.stadt-zuerich.ch/statistics/property/ZEIT"], None, sources)
        dr = BasicDimension("RAUM", "Key Raum", ["https://ld.stadt-zuerich.ch/statistics/property/RAUM"], None, sources)

        azl = Attribute("Zeit (lang)", "ZEIT_LANG", "Name des Zeitpunkts / der Periode, auf den sich der Datenpunkt bezieht.")
        azc = Attribute("Zeit (code)", "ZEIT_CODE", "Code des Zeitpunkts / der Periode, auf den sich der Datenpunkt bezieht.")
        arl = Attribute("Raum (lang)", "RAUM_LANG", "Name der administrativen räumlichen Einheit, auf die sich der Datenpunkt bezieht")
        arc = Attribute("Raum (code)", "RAUM_CODE", "Code der administrativen räumlichen Einheit, auf die sich der Datenpunkt bezieht")

        dzl = LookupDimension("ZEIT_LANG", None, ["http://schema.org/name"], azl, dz)
        dzc = LookupDimension("ZEIT_CODE", None, ["http://schema.org/termCode"], azc, dz)
        drl = LookupDimension("RAUM_LANG", None, ["http://schema.org/name"], arl, dr)
        drc = LookupDimension("RAUM_CODE", None, ["http://schema.org/termCode"], arc, dr)

        dimensions = [dz, dr, dzl, dzc, drl, drc]

        if view.include_datenstatus:
            ads = Attribute("Datenstatus (lang)", "DATENSTATUS", "Datenstatus des Datenpunktes")
            dds = BasicDimension("DATENSTATUS", "Datenstatus",
                                 ["https://ld.stadt-zuerich.ch/statistics/property/STATUS",
                                  "http://schema.org/name"], ads, sources)
            dimensions.append(dds)

        return dimensions, dz, dr
    
    def _get_view_data(self, viewname):
        with self._environment.get_db_connection() as connection:
            with connection.cursor() as cursor:
                query = f"SELECT * FROM {viewname}"
                cursor.execute(query)
                return cursor.fetchall()

    ###### QUERIES #######
    def _list_views(self) -> List:
        # id = viewId
        # name = like all attributes from Datenobjekte table
        # return [{"id":"WIR100OD100A", "name": "Haushaltseinkommen nach ...", "include_datenstatus": True}]
        return self._get_view_data(f"view_vb_view_{self._env}")

    def _list_sources_by_view_id(self, view_id: str) -> List:
        '''
        return [
            {"cube_id": "000610", "name": "Haushaltseinkommen 25%"},
            {"cube_id": "000609", "name": "Haushaltseinkommen 50%"}
        ]
        '''
        return self._get_view_data(f"view_vb_source_{self._env}")

    def _list_filters_by_view_id(self, view_id: str) -> List:
        '''
        return [
            {"termset": "KreiseZH", "dimension": "RAUM"},
            {"termset": "Jahr", "dimension": "ZEIT"}
        ]
        '''
        return self._get_view_data(f"view_vb_filter_{self._env}")

    def _list_dimensions_by_view_id(self, view_id) -> List:
        '''
        return [
            # HTY|HYTLEVEL1
            {"identifier": "HTY", "name": "Haushaltstyp", "description": "Haushaltstyp nach Haushaltstyp 1"}
        ]
        '''
        return self._get_view_data(f"view_vb_dimension_{self._env}")

    def _list_measurements_by_view_id(self, view_id) -> List:
        '''
        return [
            {"identifier": "HAE", "identifier_full": "HAE_GGH1400_STK1025", "cube_id": "000610", "name": "Haushaltsäquivalenzeinkommen / Steuerpflichtige Bevölkerung / 25%-Perzentil", "description": "Haushaltsäquivalenzeinkommen: Für die Berechnung wird die Haushaltsgrösse über die Äquivalenzskala ..."},
            {"identifier": "HAE", "identifier_full": "HAE_GGH1400_STK1050", "cube_id": "000609", "name": "Haushaltsäquivalenzeinkommen / Steuerpflichtige Bevölkerung / 50%-Perzentil", "description": "Haushaltsäquivalenzeinkommen: Für die Berechnung wird die Haushaltsgrösse über die Äquivalenzskala ..."}
        ]
        '''
        return self._get_view_data(f"view_vb_measure_{self._env}")

    ###### LOGIC ##########
    def _create_view_from_dict(self, view_dict) -> View:
        view = View(
            id=view_dict["id"],
            include_datenstatus=view_dict["include_datenstatus"]
        )

        metadata = ViewMetadata(
            author=view_dict["author"],
            legal_foundation=view_dict["legal_foundation"],
            data_type=view_dict["data_type"],
            version=view_dict["version"],
            description=view_dict["description"],
            name=view_dict["name"],
            alt_name=view_dict["alt_name"],
            metadata_creator=view_dict["metadata_creator"],
            start_date=view_dict["start_date"],
            end_date=view_dict["end_date"],
            accrual_periodicity=view_dict["accrual_periodicity"],
            issued=view_dict["issued"],
            modified=view_dict["modified"],
            publisher=view_dict["publisher"],
            keyword=view_dict["keyword"],
            license=view_dict["license"],
            usage_notes=view_dict["usage_notes"],
        )

        view.metadata = metadata
        return view

    def _create_source_from_dict(self, source_dict) -> Source:
        return Source(
            name=source_dict["name"],
            cube_id=source_dict["cube_id"]
        )

    def _create_filter_from_dict(self, filter_dict, zeit_dim, raum_dim) -> (Filter, LookupDimension):
        filter_dimension = LookupDimension(
            identifier=f"FILTER_{filter_dict["termset"].upper()}",
            name=None,
            path=["http://schema.org/inDefinedTermSet"],
            column=None,
            join=zeit_dim if filter_dict["dimension"] == "ZEIT" else raum_dim
        )
        filter = Filter(
            name=f"{filter_dict["termset"]} is {filter_dict["dimension"]}",
            argument=f"https://ld.stadt-zuerich.ch/statistics/termset/{filter_dict["termset"]}",
            dimension=filter_dimension,
            operation=FilterOperation.EQ
        )
        return filter, filter_dimension

    def _create_dimensions_from_dimension_dict(self, dimension_dict, sources) -> List:
        dimension = BasicDimension(
            identifier=dimension_dict["identifier"],
            name=dimension_dict["name"],
            path=[f"https://ld.stadt-zuerich.ch/statistics/property/{dimension_dict["identifier"]}"],
            column=None,
            sources=sources)

        alang = Attribute(
            name=f"{dimension_dict["name"]} (lang)",
            alternate_name=f"{dimension_dict["identifier"]}_LANG",
            description=dimension_dict["description"]
        )

        acode = Attribute(
            name=f"{dimension_dict["name"]} (code)",
            alternate_name=f"{dimension_dict["identifier"]}_CODE",
            description=dimension_dict["description"]
        )

        dlang = LookupDimension(f"{dimension_dict["identifier"]}_LANG", None, ["http://schema.org/name"], alang, dimension)
        dcode = LookupDimension(f"{dimension_dict["identifier"]}_CODE", None, ["http://schema.org/termCode"], acode, dimension)

        return [dimension, dlang, dcode]

    def _create_measurement_from_dimension_dict(self, measurement_dict, sources):
        source = next((s for s in sources if s.cube_id == measurement_dict["cube_id"]))

        attribute = Attribute(
            name=measurement_dict["name"],
            alternate_name=measurement_dict["identifier_full"],
            description=measurement_dict["description"]
        )

        dimension = BasicDimension(
            identifier=measurement_dict["identifier_full"],
            name=measurement_dict["name"],
            path=[f"https://ld.stadt-zuerich.ch/statistics/measure/{measurement_dict["identifier"]}"],
            column=attribute,
            sources=[source]
        )

        return dimension
