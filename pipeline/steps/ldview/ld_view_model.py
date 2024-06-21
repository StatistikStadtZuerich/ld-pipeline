from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, TypedDict


class FilterOperation(Enum):
    EQ = "Eq"


@dataclass
class Source:
    name: str
    cube_id: str

    def to_bnode(self):
        return f"_:C{self.cube_id}"

    def __hash__(self):
        return hash(self.cube_id)

    def __eq__(self, other):
        return self.cube_id == other.cube_id


@dataclass
class Attribute:
    name: str
    alternate_name: str
    description: str
    position = 0


# abstract base class
@dataclass
class Dimension:
    identifier: str
    name: Optional[str]
    path: List[str]
    column: Optional[Attribute]

    def to_bnode(self):
        return f"_:{self.identifier}"

    def get_type(self):
        return type(self).__name__


@dataclass
class BasicDimension(Dimension):
    sources: List[Source]

    def list_source_bnodes(self):
        return [source.to_bnode() for source in self.sources]


@dataclass
class LookupDimension(Dimension):
    join: BasicDimension


@dataclass
class Filter:
    name: str
    argument: str
    dimension: Dimension
    operation: FilterOperation


class ViewMetadata(TypedDict):
    author: str
    legal_foundation: str
    data_type: str
    version: str
    description: str
    name: str
    alt_name: str
    metadata_creator: str
    start_date: str
    end_date: str
    accrual_periodicity: str
    issued: str
    modified: str
    publisher: str
    theme: str
    keyword: str
    license: str
    usage_notes: str


class View:
    id: str
    metadata: ViewMetadata
    include_datenstatus: bool

    dimensions: List[Dimension] = []  # https://cube.link/view/dimension
    filters: List[Filter] = []

    def __init__(self, id: str, include_datenstatus=False):
        self.id = id
        self.include_datenstatus = include_datenstatus

    def get_sources(self):
        sources = {}
        for dimension in self.dimensions:
            if dimension.get_type() == "BasicDimension":
                for source in dimension.__dict__["sources"]:
                    sources[source.cube_id] = source
        return list(sources.values())
