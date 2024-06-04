from typing import Dict
import math
from .templating import Templating


class ObservationTemplating(Templating):
    def _preprocess(self, row: Dict) -> Dict:
        try:
            wert = int(row.get("wert"))
        except ValueError:
            wert = math.nan
        row["wert_is_nan"] = wert != wert
        return row
