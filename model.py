import csv
import json
import os
from datetime import datetime
import numpy as np

# For .xlsx support
try:
    from openpyxl import Workbook
except ImportError:
    Workbook = None

class Model:
    def __init__(self):
        self.seed = None
        self.characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"  # Alphanumeric characters (base-62)
        self.base = len(self.characters)
        self.rng = None

    def set_seed(self, seed):
        self.seed = seed
        if seed:
            try:
                seed_value = int(seed) if str(seed).isdigit() else hash(seed)
                self.rng = np.random.default_rng(seed_value)
            except (ValueError, TypeError):
                self.rng = np.random.default_rng(hash(seed))
        else:
            self.rng = np.random.default_rng()  # No seed = non-deterministic

    def _index_to_char(self, index):
        return self.characters[index % self.base]

    def generate_ids(self, count, start_counter=0):
        if self.rng is None:
            self.set_seed(self.seed)

        ids = []
        for _ in range(count):
            id_chars = [
                self._index_to_char(self.rng.integers(0, self.base))
                for _ in range(9)
            ]
            ids.append(''.join(id_chars))
        return ids

    def generate_one_id(self, existing_ids):
        raise NotImplementedError("generate_one_id is deprecated. Use generate_ids instead.")

    def save_ids(self, ids, dest_path, file_type):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_ids_{timestamp}{file_type}"
        output_path = os.path.join(dest_path, filename)

        try:
            if file_type == ".csv":
                with open(output_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["ehealth_id"])
                    for id in ids:
                        writer.writerow([id])
            elif file_type == ".txt":
                with open(output_path, 'w') as f:
                    f.write("\n".join(ids))
            elif file_type == ".json":
                with open(output_path, 'w') as f:
                    json.dump({"ids": ids}, f, indent=4)
            elif file_type == ".xlsx":
                if Workbook is None:
                    raise ImportError("The 'openpyxl' library is required to save as .xlsx.")
                wb = Workbook()
                ws = wb.active
                ws.title = "Generated IDs"
                ws.append(["ID"])
                for id in ids:
                    ws.append([id])
                wb.save(output_path)
            return output_path
        except Exception as e:
            raise Exception(f"Error saving IDs: {str(e)}")
