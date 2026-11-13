import csv
class CSVExporter:
    @staticmethod
    def write_csv(filename, data, fieldnames=None):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            if not data:
                return
            if isinstance(data[0], dict):
                fieldnames = fieldnames or list(data[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(f)
                writer.writerows(data)