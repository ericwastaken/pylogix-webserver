import json
from dataclasses import dataclass
from typing import List, Optional


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
      "rate_limit": "1/second"        // Rate limit for this PLC - empty for no rate limit
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
    rate_limit: Optional[str] = ""

    def __getitem__(self, key):
        return getattr(self, key)


class PlcList:
    """
    A class to represent a list of PLC configurations
    Supports a singleton pattern so that only one instance is created!
    """

    _instance = None  # Class-level variable to store the singleton instance

    def __new__(cls, *args, **kwargs):
        """
        Override the __new__ method to implement the singleton pattern

        :param args: arguments
        :param kwargs: keyword arguments
        :return: the singleton instance
        """
        if cls._instance is None:
            cls._instance = super(PlcList, cls).__new__(cls)
        return cls._instance

    def __init__(self, plc_config_json=None):
        """
        Initialize the PlcList class, optionally with the PLC configuration JSON. If no JSON is passed
        the class is initialized with an empty list of PLC configurations which can later be updated
        by calling load_plc_configs(plc_config_json) on the instance.

        :param plc_config_json: a JSON object that has the properties id, ip, port, and plc_slot
        """
        if plc_config_json:
            self.plc_configs = []
            self.load_plc_configs(plc_config_json)

    def load_plc_configs(self, plc_config_json):
        self.plc_configs = []
        for plc in plc_config_json:
            plc_config = PlcConfig(**plc)
            self.plc_configs.append(plc_config)

    def __iter__(self):
        return iter(self.plc_configs)

