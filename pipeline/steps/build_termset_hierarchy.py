from .templating import Templating


class BuildTermsetHierarchy(Templating):
    def pre_process(self, row):
        rows = []
        for x in range(1, 4):
            if not row.get(f"r{x}"):
                break
            for y in range(x):
                value = row.get(f"f{y}")
                if not value:
                    break
                for relation in value.split(";"):
                    rows.append(
                        {
                            "child_code": row[f"r{x}"],
                            "relation_filter": relation.strip(),
                            "parent_code": row[f"r{y}"],
                        }
                    )
        return rows
