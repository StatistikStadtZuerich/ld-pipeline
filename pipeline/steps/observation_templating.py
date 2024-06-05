from typing import Dict
import math
from .templating import Templating


class ObservationTemplating(Templating):
    def _preprocess(self, row: Dict) -> Dict:
        try:
            value = int(row.get("value"))
        except ValueError:
            value = math.nan
        row["value_is_nan"] = value != value
        return row
