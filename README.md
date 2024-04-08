# LD Pipeline 2024

"LD Pipeline 2024" is a redevelopment of the existing pipeline, focusing on
improving flexibility, efficiency and scalability. This project involves
extracting data from the Harmonized Database (HDB), converting it into triples,
and then transferring it into an RDF database.

## Getting Started

These instructions will help you get a copy of the project up and running on your
local machine for development and testing purposes.

### Prerequisites

Before you begin, ensure you have the following installed and configured:

- Python 3.6 or higher, development is done with python 3.10

### Installation

Follow these steps to set up your development environment:

1) Clone the repository:

   1) `git clone https://github.com/StatistikStadtZuerich/ld-pipeline-2024.git`
   2) `cd ld-pipeline-2024`

2) It is recommended to use a virtual environment.

   1) `python -m venv .venv`
   2) `source .venv/bin/activate`

3) Install the required Python dependencies:

   * `pip install -r requirements.txt`

4) Execute the pipeline:

   * Get help: `python main.py --help`
   * Run pipeline: `python main.py run`
   * Run pipeline in env:test: `python main.py run --env test`
   * List all supported step names: `python main.py list-step-names `
   * Run single step in env:test: `python main.py step --env test --name copyStatic`

## Pipeline Steps
### Copy Step
Copies file from

## Run with docker

1) Build docker image: `docker build -t ssz/ld-pipeline .`
2) Run dockerized application (e.g. help command): `docker run ssz/ld-pipeline --help`
3) Mount an output directory, e.g.: `docker run --mount type=bind,source="$(pwd)"/tmp,target=/out ssz/ld-pipeline step --env local --name copyStatic`.

*HINT*: be sure to use only _local_, _int_ or _prod_ as environment within docker.

## Development

1) Unit Tests
   * Unit tests can be found under tests/unit
   * Run: `python -m pytest tests/unit`
2) Integration Tests
   * Integration tests can be found under tests/integration
   * The tests create the environment using docker (test/integration/docker-compose.yaml)
   * Be sure docker is up and running
   * Run: `python -m pytest --container-scope=session tests/integration`
3) Local Pipeline execution
   * Install act from https://nektosact.com/
   * Execute pipeline: `act --container-architecture linux/amd64`
