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

5) Execute the pipeline:

   * Get help: `python main.py --help`
   * Run pipeline: `python main.py run`
   * Run pipeline in env:test: `python main.py run --env test`
   * Run single step in env:test: `python main.py step --env test --name copy` 
