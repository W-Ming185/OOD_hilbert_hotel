import csv


class CSVExporter:
    @staticmethod
    def write_csv(filename, data, fieldnames=None):
        rows = list(data)
        with open(filename, "w", newline="", encoding="utf-8") as file:
            if not rows:
                if fieldnames:
                    csv.writer(file).writerow(fieldnames)
                return
            if isinstance(rows[0], dict):
                names = fieldnames or list(rows[0].keys())
                writer = csv.DictWriter(file, fieldnames=names)
                writer.writeheader()
                writer.writerows(rows)
            else:
                csv.writer(file).writerows(rows)
