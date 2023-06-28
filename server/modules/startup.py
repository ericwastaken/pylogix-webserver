# Python Dependencies
import os
import json
import sys

# Bring in own dependencies
from controller_get_tag_list import TagList
import model_PlcList
from model_PlcList import PlcList
import model_BatchList
from model_BatchList import BatchList

# Load the shared logger
import modules.logger as logger
shared_logger = logger.CustomLogger()


class Startup:
    """Start Up Pre-Requisites
    This class handles the pre-requisites for starting the server.
    """

    @classmethod
    def start(cls, config_file_path, cache_directory, cache_ttl):
        """Prepare dependencies for the server.
        :param config_file_path: the path to the config file
        :param cache_directory: the directory to store the tag list cache files
        :param cache_ttl: the time-to-live (in minutes) for the tag list cache files
        :return: a tuple of (plc_list, tag_list_instance)
        """

        shared_logger.log.info("Starting...")
        plc_list: model_PlcList = []
        batch_list: model_BatchList = []
        tag_list_instance = None

        # each PLC will cache its tag list in a file in this cache_directory
        # so on startup, if the cache_directory exists, remove all files. otherwise, create it
        if os.path.exists(cache_directory):
            werefiles = 0
            for filename in os.listdir(cache_directory):
                file_path = os.path.join(cache_directory, filename)
                # Check if the current path is a file
                if os.path.isfile(file_path):
                    # Delete the file
                    os.remove(file_path)
                    werefiles = werefiles + 1
            if werefiles > 0:
                shared_logger.log.info("plc_tag_cache was cleared")
        else:
            os.mkdir(cache_directory)

        # load the config for PLC identification
        if os.path.exists(config_file_path):
            # Read cached data from file
            with open(config_file_path, "r") as file:
                config = json.load(file)
            shared_logger.log.info("loaded " + config_file_path)
            # Deserialize the PLC list
            plc_list = PlcList(config["plc_list"])
            batch_list = BatchList(config["batch_list"])
        else:
            shared_logger.log.fatal(f'Unable to read config: {config_file_path}.')
            sys.exit(-1)

        try:
            # Create an instance of the Tag List
            tag_list_instance = TagList(cache_directory, cache_ttl)

            # for each PLC, retrieve and cache tags
            # this might fail for some, not others, so we try/catch individually
            for plc_config in plc_list:
                try:
                    shared_logger.log.debug(f'Getting tag list for {plc_config}')
                    # In this case, this gets called for the side effect on the instance
                    # i.e. loads the tag list cache for each PLC.
                    tag_list_instance.get_tag_list(plc_config)
                except Exception as e:
                    shared_logger.log.error(f'On Startup, error getting tag list: {e}')

            # Log and return the useful objects
            shared_logger.log.info("Startup finished")
            return plc_list, tag_list_instance, batch_list

        except Exception as e:
            shared_logger.log.error(f'Startup error: {e}')
            return plc_list, tag_list_instance, batch_list
