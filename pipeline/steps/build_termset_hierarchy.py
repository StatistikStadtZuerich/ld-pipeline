from .templating import Templating


class BuildTermsetHierarchy(Templating):

    def pre_process(self, row):
        rows = []
        for x in range(1, 4):
            for y in range(0, x):
                for relation in row[f"f{y}"].split(";"):
                    rows.append({
                        'child_code': row[f"r{x}"],
                        'relation_filter': relation.strip(),
                        'parent_code': row[f"r{y}"]
                    })
        return rows

