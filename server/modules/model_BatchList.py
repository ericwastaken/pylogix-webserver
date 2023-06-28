import json
from dataclasses import dataclass
from typing import List


@dataclass
class BatchConfig:
    """A class to represent a Batch configuration.
    Matches the JSON:
    {
      "id": "some-batch-id",   // Must be unique, identifies the batch
      "plc_id": "some-plc-id", // Some plc_id matching from the plc_list
      "tag_list": ["TAG3"],    // List of tags to read for this batch
    }
    """
    id: str
    plc_id: str
    tag_list: List[str]

    def __getitem__(self, key):
        return getattr(self, key)


class BatchList:
    def __init__(self, batch_config_json):
        self.batch_configs = []
        self.load_batch_configs(batch_config_json)

    def load_batch_configs(self, batch_config_json):
        for batch in batch_config_json:
            batch_config = BatchConfig(**batch)
            self.batch_configs.append(batch_config)

    def __iter__(self):
        return iter(self.batch_configs)

