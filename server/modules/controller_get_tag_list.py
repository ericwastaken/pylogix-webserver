# Python dependencies
import json
import os
from datetime import datetime, timedelta
from typing import List

# Import our own dependencies
import utils
import plc_io
import model_PlcList

# Default logging to DEBUG
import modules.logger as logger
shared_logger = logger.CustomLogger()


class _TagListForPlc:
    """A helper class to store the tag list and its timestamp for a given PLC
    """
    def __init__(self, tag_list, tag_list_updated):
        self.tag_list = tag_list
        self.tag_list_updated = tag_list_updated

    def __getitem__(self, key):
        """Helper method to get a property by name"""
        return getattr(self, key)


class TagList:
    """Class that handles the PLC tag list cache"""

    # declare class properties cache_directory and cache_ttl
    cache_directory = None
    cache_ttl = None
    tag_lists = None

    def __init__(self, cache_directory, cache_ttl):
        """Initialize the TagList class with the cache directory and cache TTL.
        :param cache_directory: the directory to store the tag list cache files
        :param cache_ttl: the time-to-live (in minutes) for the tag list cache files
        """
        self.cache_directory = cache_directory
        self.cache_ttl = cache_ttl
        self.tag_lists = {}

    def get_tag_list(self, plc_config: model_PlcList.PlcConfig):
        """Get tag list from either the CACHE (if exists and within TTL) or the PLC directly.
        :param plc_config: a JSON object that has the properties id, ip, port, and plc_slot
        :return: a tuple of (tag_list, tag_list_timestamp)
        """
        shared_logger.log.debug(f'Getting tag list for plc_config: {plc_config}')

        try:

            plc_ip = plc_config.ip
            plc_slot = plc_config.slot
            plc_id = plc_config.id
            plc_port = plc_config.port

            # Check if we were passed the needed items ip, plc_slot, id, port and return with error if not
            if not plc_ip or not isinstance(plc_slot, int) or not plc_id or not plc_port:
                raise Exception(f'Missing required field(s) in plc_config: {plc_config}')

            # If we have the tag list in memory, return it so long as it's within ttl
            if plc_id in self.tag_lists:
                tag_list_for_plc = self.tag_lists[plc_id]
                # Check if the tag list is for this plc_id within TTL
                if utils.is_timestamp_old(tag_list_for_plc.tag_list_updated, self.cache_ttl):
                    # Return the tag list from memory
                    shared_logger.log.debug(f'Returning in-memory tag list for plc_id: {plc_id}')
                    return tag_list_for_plc.tag_list, tag_list_for_plc.tag_list_updated

            # Calculate the file name for this PLC tag list cache file
            cache_full_path = os.path.join(self.cache_directory, f'{utils.convert_to_safe_filename(plc_id)}.json')
            shared_logger.log.debug(f'Cache file name: {cache_full_path}')

            cache_exists = os.path.exists(cache_full_path)
            # Decide if the cache is old
            if cache_exists:
                is_cache_old, file_timestamp = utils.is_file_old(cache_full_path, self.cache_ttl)
            else:
                is_cache_old, file_timestamp = True, 0

            if cache_exists and not is_cache_old:
                # Read cached data from file
                shared_logger.log.debug(f'Returning cached tag list for plc_id: {plc_id}')
                with open(cache_full_path, "r") as file:
                    tag_list = json.load(file)
                # return the tag list and the timestamp of the cache file
                return tag_list, file_timestamp
            else:
                # Try to pull tag_list from PLC
                tag_list = plc_io.get_tag_list(plc_id, plc_ip, plc_slot, plc_port)
                # If we got a tag_list, save it to cache
                if tag_list is not None:
                    shared_logger.log.debug(f'Saving newly read tag list for plc_id: {plc_id}')
                    with open(cache_full_path, "w") as file:
                        json.dump(tag_list, file)
                    # Get the timestamp of the cache file
                    update_time = os.path.getmtime(cache_full_path)
                    # Also save to memory
                    self.tag_lists[plc_id] = _TagListForPlc(tag_list, update_time)
                    shared_logger.log.debug(f'Returning newly cached tag list for plc_id: {plc_id}')
                    # return the tag list and the timestamp of the cache file
                    return tag_list, update_time
                else:
                    raise Exception(f'Unable to retrieve tag list for plc_id: {plc_id}')

        except Exception as e:
            custom_exception_message = f'{e}'
            shared_logger.log.error(custom_exception_message)
            raise Exception(custom_exception_message) from e

    def get_tag_type(self, plc_config: model_PlcList.PlcConfig, tag_name):
        """Get the tag type for a given tag name.
        :param tag_name: the tag name to get the type for
        :param plc_config: a JSON object that has the properties id, ip, port, and slot_no
        :return: the PLC tag type (as a string)
        """
        try:
            # get the tag list, find tag_name, and return the tag type
            tag_list, _ = self.get_tag_list(plc_config)
            if tag_list is not None:
                return tag_list[tag_name]["type"]
            return ""
        except Exception as e:
            return ""

