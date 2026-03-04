from typing import List, Tuple, Optional

from pipeline.base import Environment, Base
from pipeline.steps.ldview import (
    View,
    BasicDimension,
    Source,
    LookupDimension,
    Attribute,
    ViewMetadata,
    Filter,
    FilterOperation,
)


class LdViewBuilder(Base):
    def __init__(self, environment: Environment):
        super().__init__()
        self._environment = environment
        self._env = environment.name
        self._cache = {}

    def build_all(self) -> List[View]:
        views = []
        for view_dict in self._list_views():
            view = self._create_view_from_dict(view_dict)

            source_dict_list = self._list_sources_by_view_id(view.id)
            sources = [
                self._create_source_from_dict(source_dict)
                for source_dict in source_dict_list
            ]

            basic_dimension_plus_dzeit_and_draum = self._get_static_dimensions(
                view, sources
            )
            view.dimensions.extend(basic_dimension_plus_dzeit_and_draum[0])
            dimension_raum = basic_dimension_plus_dzeit_and_draum[2]

            dimension_dict_list = self._list_dimensions_by_view_id(view.id)
            for dimension_dict in dimension_dict_list:
                view.dimensions.extend(
                    self._create_dimensions_from_dimension_dict(dimension_dict, sources)
                )

            filter_dict_list = self._list_filters_by_view_id(view.id)
            for filter_dict in filter_dict_list:
                _filter, dimension = self._create_filter_from_dict(
                    filter_dict, view.dimensions
                )

                if _filter is not None:
                    view.filters.append(_filter)

                if dimension is not None:
                    view.dimensions.append(dimension)

            measurement_dict_list = self._list_measurements_by_view_id(view.id)
            for measurement_dict in measurement_dict_list:
                view.dimensions.append(
                    self._create_measurement_from_dimension_dict(
                        measurement_dict, sources
                    )
                )

            hierarchy_dict_list = self._list_hierarchies_by_view_id(view.id)
            for hierarchy_dict in hierarchy_dict_list:
                view.dimensions.extend(
                    self._create_dimensions_from_hierarchy_dict(
                        hierarchy_dict, dimension_raum
                    )
                )
            view.sort_and_numerate_dimensions()

            # view.sort_and_numerate_dimensions()
            views.append(view)

        return views

    ###### STATIC ########
    def _get_static_dimensions(self, view, sources):
        dz = BasicDimension(
            "ZEIT",
            "Key Zeit",
            ["https://ld.stadt-zuerich.ch/statistics/property/ZEIT"],
            None,
            sources,
        )
        dr = BasicDimension(
            "RAUM",
            "Key Raum",
            ["https://ld.stadt-zuerich.ch/statistics/property/RAUM"],
            None,
            sources,
        )

        azl = Attribute(
            "Zeit (lang)",
            "ZEIT_LANG",
            "Name des Zeitpunkts / der Periode, auf den sich der Datenpunkt bezieht.",
        )
        azc = Attribute(
            "Zeit (code)",
            "ZEIT_CODE",
            "Code des Zeitpunkts / der Periode, auf den sich der Datenpunkt bezieht.",
        )
        arl = Attribute(
            "Raum (lang)",
            "RAUM_LANG",
            "Name der administrativen räumlichen Einheit, auf die sich der Datenpunkt bezieht",
        )
        arc = Attribute(
            "Raum (code)",
            "RAUM_CODE",
            "Code der administrativen räumlichen Einheit, auf die sich der Datenpunkt bezieht",
        )
        ars = Attribute(
            "Raum (sort)",
            "RAUM_SORT",
            "Hilfswert zur Sortierung nach der administrativen räumlichen Einheit, auf die sich der Datenpunkt bezieht",
        )

        dzl = LookupDimension("ZEIT_LANG", None, ["https://schema.org/name"], azl, dz)
        dzc = LookupDimension(
            "ZEIT_CODE", None, ["https://schema.org/termCode"], azc, dz
        )
        drl = LookupDimension("RAUM_LANG", None, ["https://schema.org/name"], arl, dr)
        drc = LookupDimension(
            "RAUM_CODE", None, ["https://schema.org/termCode"], arc, dr
        )
        drs = LookupDimension(
            "RAUM_SORT", None, ["https://schema.org/position"], ars, dr
        )

        dimensions = [dz, dr, dzl, dzc, drl, drc, drs]

        if view.include_datenstatus:
            ads = Attribute(
                "Datenstatus (lang)", "DATENSTATUS", "Datenstatus des Datenpunktes"
            )
            dds = BasicDimension(
                "DATENSTATUS",
                "Datenstatus",
                [
                    "https://ld.stadt-zuerich.ch/statistics/property/STATUS",
                    "https://schema.org/name",
                ],
                ads,
                sources,
            )
            dimensions.append(dds)

        return dimensions, dz, dr

    def _get_view_data(self, view_name, view_id=None):
        cache_ident = view_name + "_" + str(view_id)
        if cache_ident in self._cache:
            return self._cache[cache_ident]
        with self._environment.get_db_connection() as connection:
            _sql_view_name = self._environment.view_name(view_name)
            with connection.cursor() as cursor:
                query = f"SELECT * FROM {_sql_view_name}"
                cursor.execute(query)
                result = cursor.fetchall()
                if view_id is not None:
                    result = [row for row in result if row["view_id"] == view_id]
                self._cache[cache_ident] = result
                return result

    ###### QUERIES #######
    def _list_views(self) -> List:
        # id = viewId
        # name = like all attributes from Datenobjekte table
        # return [{"id":"WIR100OD100A", "name": "Haushaltseinkommen nach ...", "include_datenstatus": True}]
        return self._get_view_data("view_vb_view", None)

    def _list_sources_by_view_id(self, view_id: str) -> List:
        """
        return [
            {"cube_id": "000610", "name": "Haushaltseinkommen 25%"},
            {"cube_id": "000609", "name": "Haushaltseinkommen 50%"}
        ]
        """
        return self._get_view_data("view_vb_source", view_id)

    def _list_filters_by_view_id(self, view_id: str) -> List:
        """
        return [
            {"termset": "KreiseZH", "dimension": "RAUM"},
            {"termset": "Jahr", "dimension": "ZEIT"},
            {"termset": "HYTLevel1", "dimension": "HTY", "view_id": view_id},
        ]
        """
        return self._get_view_data("view_vb_filter", view_id)

    def _list_dimensions_by_view_id(self, view_id) -> List:
        """
        return [
            # HTY|HYTLEVEL1
            {"identifier": "HTY", "name": "Haushaltstyp", "description": "Haushaltstyp nach Haushaltstyp 1"}
        ]
        """
        return self._get_view_data("view_vb_dimension", view_id)

    def _list_measurements_by_view_id(self, view_id) -> List:
        """
        return [
            {"identifier": "HAE", "identifier_full": "HAE_GGH1400_STK1025", "cube_id": "000610", "name": "Haushaltsäquivalenzeinkommen / Steuerpflichtige Bevölkerung / 25%-Perzentil", "description": "Haushaltsäquivalenzeinkommen: Für die Berechnung wird die Haushaltsgrösse über die Äquivalenzskala ..."},
            {"identifier": "HAE", "identifier_full": "HAE_GGH1400_STK1050", "cube_id": "000609", "name": "Haushaltsäquivalenzeinkommen / Steuerpflichtige Bevölkerung / 50%-Perzentil", "description": "Haushaltsäquivalenzeinkommen: Für die Berechnung wird die Haushaltsgrösse über die Äquivalenzskala ..."}
        ]
        """
        return self._get_view_data("view_vb_measure", view_id)

    def _list_hierarchies_by_view_id(self, view_id):
        """
        return [
            {"termset": "KreiseZH", "dimension": "RAUM"},
            {"termset": "QuartiereZH", "dimension": "RAUM"},
        ]
        """
        return self._get_view_data("view_vb_room_hierarchy", view_id)

    ###### LOGIC ##########
    def _create_view_from_dict(self, view_dict) -> View:
        view = View(
            id=view_dict["id"], include_datenstatus=view_dict["include_datenstatus"]
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
            accrual_periodicity=view_dict["accrual_periodicity"],
            spatial=view_dict["spatial"],
            issued=view_dict["issued"],
            publisher=view_dict["publisher"],
            theme=view_dict["theme"],
            keyword=view_dict["keyword"],
            license=view_dict["license"],
            usage_notes=view_dict["usage_notes"],
            dataquality=view_dict["dataquality"],
        )

        view.metadata = metadata
        return view

    def _create_source_from_dict(self, source_dict) -> Source:
        return Source(name=source_dict["name"], cube_id=source_dict["cube_id"])

    def _create_filter_from_dict(
        self, filter_dict: dict, dim_list: List
    ) -> Tuple[Optional[Filter], Optional[LookupDimension]]:
        basic_dimension = next(
            (d for d in dim_list if d.identifier == filter_dict["dimension"].upper()),
            None,
        )

        if basic_dimension is None:
            self.logger.warn(
                f"View contains filter dimension {filter_dict['dimension']}, which is not in the list of dimensions"
            )
            return None, None

        filter_dimension = LookupDimension(
            identifier=f"FILTER_{filter_dict['termset'].upper()}",
            name=None,
            path=["https://schema.org/inDefinedTermSet"],
            column=None,
            join=basic_dimension,
        )
        filter_value = Filter(
            name=f"{filter_dict['termset']} is {filter_dict['dimension']}",
            argument=f"https://ld.stadt-zuerich.ch/statistics/termset/{filter_dict['termset']}",
            dimension=filter_dimension,
            operation=FilterOperation.EQ,
        )
        return filter_value, filter_dimension

    def _create_dimensions_from_dimension_dict(self, dimension_dict, sources) -> List:
        dimension = BasicDimension(
            identifier=dimension_dict["identifier"],
            name=dimension_dict["name"],
            path=[
                f"https://ld.stadt-zuerich.ch/statistics/property/{dimension_dict['identifier']}"
            ],
            column=None,
            sources=sources,
        )

        alang = Attribute(
            name=f"{dimension_dict['name']} (lang)",
            alternate_name=f"{dimension_dict['identifier']}_LANG",
            description=dimension_dict["description"],
        )

        acode = Attribute(
            name=f"{dimension_dict['name']} (code)",
            alternate_name=f"{dimension_dict['identifier']}_CODE",
            description=dimension_dict[
                "description"
            ],  # TODO add maybe more descriptive information
        )

        asort = Attribute(
            name=f"{dimension_dict['name']} (sort)",
            alternate_name=f"{dimension_dict['identifier']}_SORT",
            description=dimension_dict[
                "description"
            ],  # TODO add maybe more descriptive information
        )

        dlang = LookupDimension(
            f"{dimension_dict['identifier']}_LANG",
            None,
            ["https://schema.org/name"],
            alang,
            dimension,
        )
        dcode = LookupDimension(
            f"{dimension_dict['identifier']}_CODE",
            None,
            ["https://schema.org/termCode"],
            acode,
            dimension,
        )
        dsort = LookupDimension(
            f"{dimension_dict['identifier']}_SORT",
            None,
            ["https://schema.org/position"],
            asort,
            dimension,
        )

        return [dimension, dlang, dcode, dsort]

    def _create_measurement_from_dimension_dict(self, measurement_dict, sources):
        source = next((s for s in sources if s.cube_id == measurement_dict["cube_id"]))

        attribute = Attribute(
            name=measurement_dict["name"],
            alternate_name=measurement_dict["identifier_full"],
            description=measurement_dict["description"],
        )

        dimension = BasicDimension(
            identifier=measurement_dict["identifier_full"],
            name=measurement_dict["name"],
            path=[
                f"https://ld.stadt-zuerich.ch/statistics/measure/{measurement_dict['identifier']}"
            ],
            column=attribute,
            sources=[source],
        )

        return dimension

    def _create_dimensions_from_hierarchy_dict(self, hierarchy_dict, raum_dimension):
        alang = Attribute(
            name=f"{hierarchy_dict['termset']} (lang)",
            alternate_name=f"{hierarchy_dict['termset'].upper()}_LANG",
            description=f"Name der Hierarchiestufe '{hierarchy_dict['termset']}', auf den sich der Datenpunkt bezieht.",
        )

        acode = Attribute(
            name=f"{hierarchy_dict['termset']} (code)",
            alternate_name=f"{hierarchy_dict['termset'].upper()}_CODE",
            description=f"Code der Hierarchiestufe '{hierarchy_dict['termset']}', auf den sich der Datenpunkt bezieht.",
        )

        asort = Attribute(
            name=f"{hierarchy_dict['termset']} (sort)",
            alternate_name=f"{hierarchy_dict['termset'].upper()}_SORT",
            description=f"Sortierungshilfe der Hierarchiestufe '{hierarchy_dict['termset']}', auf den sich der Datenpunkt bezieht.",
        )

        if hierarchy_dict["dimension"] != "RAUM":
            self.logger.warn(
                f"View contains hierarchy type {hierarchy_dict['dimension']}, currently only 'RAUM' supported"
            )

        dlang = LookupDimension(
            f"{hierarchy_dict['termset'].upper()}_LANG",
            None,
            [
                f"https://ld.stadt-zuerich.ch/schema/hierarchy/has{hierarchy_dict['termset']}",
                "https://schema.org/name",
            ],
            alang,
            raum_dimension,
        )
        dcode = LookupDimension(
            f"{hierarchy_dict['termset'].upper()}_CODE",
            None,
            [
                f"https://ld.stadt-zuerich.ch/schema/hierarchy/has{hierarchy_dict['termset']}",
                "https://schema.org/termCode",
            ],
            acode,
            raum_dimension,
        )
        dsort = LookupDimension(
            f"{hierarchy_dict['termset'].upper()}_SORT",
            None,
            [
                f"https://ld.stadt-zuerich.ch/schema/hierarchy/has{hierarchy_dict['termset']}",
                "https://schema.org/position",
            ],
            asort,
            raum_dimension,
        )

        return [dlang, dcode, dsort]
