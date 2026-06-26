import json


class MappingLoader:
    def __init__(self, mapping_path):
        self.mapping_path = mapping_path

    def load(self) -> dict:
        """Return only the field mapping rules (excludes the 'config' key)."""
        raw = self._load_raw()
        return {k: v for k, v in raw.items() if k != "config"}

    def load_config(self) -> dict:
        """Return the 'config' block, or an empty dict if absent."""
        return self._load_raw().get("config", {})

    def _load_raw(self) -> dict:
        with open(self.mapping_path, "r", encoding="utf-8") as f:
            return json.load(f)