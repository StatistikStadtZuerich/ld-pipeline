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

- Python 3.6 or higher
- Access to a Microsoft SQL Server Database (HDB)
- An installed and configured RDF database

### Installation

Follow these steps to set up your development environment:

1) Clone the repository:

    git clone https://github.com/StatistikStadtZuerich/ld-pipeline-2024.git
    cd ld-pipeline-2024

2) Install the required Python dependencies:

    pip install -r requirements.txt

3) Configure the access credentials for both the Harmonized Database and the RDF
database within the configuration files.

4) Execute the pipeline:

    python main.py
