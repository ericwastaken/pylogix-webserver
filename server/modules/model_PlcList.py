import json
from dataclasses import dataclass
from typing import List


@dataclass
class PlcConfig:
    """A class to represent a PLC configuration.
    Matches the JSON:
    {
      "id": "some-plc-id",            // Must be unique, identifies the PLC
      "ip": "xxx.xxx.xxx.xxx",        // Some IP
      "port": 44818,
      "slot": 0,
      "allow_tags": ["TAG1", "TAG2"], // Explicit tag names to allow
      "exclude_tags": ["TAG3"],       // Explicit tag names to exclude
      "allow_tags_regex": ".*",       // Explicit tag name regex to allow
      "exclude_tags_regex": ""        // Explicit tag name regex to exclude
    }
    """
    id: str
    ip: str
    port: int
    slot: int
    allow_tags: List[str]
    exclude_tags: List[str]
    allow_tags_regex: str
    exclude_tags_regex: str

    def __getitem__(self, key):
        return getattr(self, key)


class PlcList:
    def __init__(self, plc_config_json):
        self.plc_configs = []
        self.load_plc_configs(plc_config_json)

    def load_plc_configs(self, plc_config_json):
        for plc in plc_config_json:
            plc_config = PlcConfig(**plc)
            self.plc_configs.append(plc_config)

    def __iter__(self):
        return iter(self.plc_configs)

