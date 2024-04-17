from ..base import Step, Environment
import csv


class Templating(Step):
    def __init__(self):
        super().__init__()

    def run(self, environment: Environment):
        with environment.get_template_engine(
            "ttl_template.txt", "my_output.ttl"
        ) as templating_engine:
            templating_engine.open()
            with open("./HDB_DIMENSIONEN.csv", newline="") as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    templating_engine.template(
                        {
                            "Dimension": row["Dimension"],
                            "Dimensionname": row["Dimensionname"],
                        }
                    )
            templating_engine.close()
