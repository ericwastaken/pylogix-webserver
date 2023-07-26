import json
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class BatchConfig:
    """A class to represent a Batch configuration.
    Matches the JSON:
    {
      "id": "some-batch-id",        // Must be unique, identifies the batch
      "plc_id": "some-plc-id",      // Some plc_id matching from the plc_list
      "tag_list": ["TAG3"],         // List of tags to read for this batch
      "rate_limit": "1/second",     // Rate limit for this PLC - empty for no rate limit
    }
    """
    id: str
    plc_id: str
    tag_list: List[str]
    rate_limit: Optional[str] = ""

    def __getitem__(self, key):
        return getattr(self, key)


class BatchList:
    """
    A class to represent a list of Batches
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
            cls._instance = super(BatchList, cls).__new__(cls)
        return cls._instance

    def __init__(self, batch_config_json=None):
        """
        Initialize the BatchList class, optionally with the Batch JSON. If no JSON is passed
        the class is initialized with an empty list of batches which can later be updated
        by calling load_batch_configs(batch_config_json) on the instance.

        :param batch_config_json: optional JSON to initialize the class with
        """
        if batch_config_json:
            self.batch_configs = []
            self.load_batch_configs(batch_config_json)

    def load_batch_configs(self, batch_config_json):
        self.batch_configs = []
        for batch in batch_config_json:
            batch_config = BatchConfig(**batch)
            self.batch_configs.append(batch_config)

    def __iter__(self):
        return iter(self.batch_configs)

