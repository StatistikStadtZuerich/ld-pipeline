from typing import Dict
import math
from .templating import Templating


class ObservationTemplating(Templating):
    def _preprocess(self, row: Dict) -> Dict:
        # row["CUBE_IDS"] = list(
        #     map(lambda cid: cid.replace("CID_", ""), row.get("CUBEID").split(" "))
        # )
        # row["DATENSTATUS"] = row.get("DATENSTATUS").split(";")[0].strip().lower()

        try:
            wert = int(row.get("wert"))
        except ValueError:
            wert = math.nan
        row["is_wert_nan"] = wert != wert
        return row
