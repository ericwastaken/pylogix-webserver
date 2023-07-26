# Python dependencies
import os
import time
import re
import argparse

# Project dependencies
import model_BatchList
import model_PlcList

# Load the shared logger
import modules.logger as logger
shared_logger = logger.CustomLogger()


def is_file_old(file_path, minutes_threshold):
    """Return True if file is older than minutes_threshold, else False."""
    file_timestamp = os.path.getmtime(file_path)
    current_time = time.time()
    elapsed_minutes = (current_time - file_timestamp) / 60
    if elapsed_minutes > minutes_threshold:
        return True, file_timestamp
    else:
        return False, file_timestamp


def is_timestamp_old(timestamp, minutes_threshold):
    """Return True if timestamp is older than minutes_threshold, else False."""
    current_time = time.time()
    elapsed_minutes = (current_time - timestamp) / 60
    if elapsed_minutes > minutes_threshold:
        return True, timestamp
    else:
        return False, timestamp


def convert_to_safe_filename(string):
    """Convert a string to a safe filename (Linux & Windows)."""
    # Replace reserved characters for both Linux and Windows with underscore
    safe_string = re.sub(r'[<>:"/\\|?*, ]', '_', string)

    # Replace Linux-specific reserved characters with underscore
    safe_string = re.sub(r'[\\\\]', '_', safe_string)

    # Remove leading or trailing space
    safe_string = safe_string.strip()

    # Remove consecutive underscores
    safe_string = re.sub(r'_{2,}', '_', safe_string)

    # Remove dots at the beginning or end of the filename
    safe_string = safe_string.strip('.')

    return safe_string


def is_list_of_strings(list_to_check):
    return isinstance(list_to_check, list) and all(isinstance(item, str) for item in list_to_check)


def get_plc_config_for_plc_id(plc_list: model_PlcList, plc_id):
    """Return the PLC config for the given plc_id, or None if not found.
    :param plc_list: the list of PLC configs
    :param plc_id: the PLC ID to search for
    :return: the PLC config for the given plc_id, or None if not found
    """
    for plc_config in plc_list:
        if plc_config.id == plc_id:
            return plc_config
    return None


def get_plc_batch_config_for_batch_id(batch_list: model_BatchList, batch_id):
    """Return the PLC batch config for the given batch_id, or None if not found.
    :param batch_list: the list of PLC batch configs
    :param batch_id: the batch ID to search for
    :return: the PLC batch config for the given batch_id, or None if not found
    """
    for batch_config in batch_list:
        if batch_config.id == batch_id:
            return batch_config
    return None


# Command line argument validators

def validate_directory(directory):
    """Validate that the given directory exists."""
    if not os.path.isdir(directory):
        raise argparse.ArgumentTypeError(f"{directory} is not a valid directory")
    return directory


def validate_file(filepath):
    """Validate that the given file exists."""
    if not os.path.isfile(filepath):
        raise argparse.ArgumentTypeError(f"{filepath} does not exist")
    return filepath


def validate_hostname(hostname):
    """Validate that the given hostname is valid."""
    if not re.match(r"^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])$", hostname):
        raise argparse.ArgumentTypeError(f"{hostname} is not a valid hostname")
    return hostname


def validate_port(port):
    """Validate that the given port is valid."""
    try:
        port = int(port)
        if not (0 <= port <= 65535):
            raise argparse.ArgumentTypeError(f"{port} is not a valid port number")
    except ValueError:
        raise argparse.ArgumentTypeError(f"{port} is not a valid port number")
    return port


def validate_integer(value):
    """Validate that the given value is an integer."""
    try:
        value = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a valid value")
    return value


def process_allow_disallow_tag_list(tag_list, plc_config: model_PlcList.PlcConfig):
    """
    Process the allow/disallow tag list for a PLC.
    Note that this function modifies the passed tag_list.
    allow_tags/exclude_tags will take precedence over allow_tags_regex/exclude_tags_regex.
    """
    # Save the original tag list
    original_tag_list = tag_list

    shared_logger.log.info(f"Processing allow/disallow tag list for PLC {plc_config}")
    shared_logger.log.debug(f"Original tag list: {original_tag_list}")

    # Decide which path to take based on whether allow_tags or exclude_tags is set
    # allow_tags/exclude_tags will take precedence over allow_tags_regex/exclude_tags_regex
    if plc_config.allow_tags or plc_config.exclude_tags:
        shared_logger.log.debug(f"Using allow_tags/exclude_tags")
        # If plc_config.allow_tags has any tags, remove any tags from the passed tag_list not in the allow_tags list
        if plc_config.allow_tags:
            tag_list = [tag for tag in tag_list if tag in plc_config.allow_tags]
        # If plc_config.exclude_tags has any tags, remove any tags from the passed tag_list that are in the
        # exclude_tags list
        if plc_config.exclude_tags:
            tag_list = [tag for tag in tag_list if tag not in plc_config.exclude_tags]
    elif plc_config.allow_tags_regex or plc_config.exclude_tags_regex:
        shared_logger.log.debug(f"Using allow_tags_regex/exclude_tags_regex")
        # If plc_config.allow_tags_regex has a regex, remove any tags from the passed tag_list not matching the
        # allow_tags_regex
        if plc_config.allow_tags_regex:
            tag_list = [tag for tag in tag_list if re.match(plc_config.allow_tags_regex, tag)]
        # If plc_config.exclude_tags_regex ha a regex, remove any tags from the passed tag_list that match the
        # exclude_tags_regex
        if plc_config.exclude_tags_regex:
            tag_list = [tag for tag in tag_list if not re.match(plc_config.exclude_tags_regex, tag)]

    shared_logger.log.debug(f"Final tag list: {tag_list}")
    return original_tag_list, tag_list


# Utilities related to rate limiting


def get_limit_key(req, resp, resource, params) -> str:
    """
    Function to return the key to use for rate limiting.
    This function is called by the falcon-limiter package.
    The key is the plc_id or the tag_batch_id, which are required fields in the JSON body of the request for
    fetching batches and values.
    """
    obj = req.get_media()
    tag_batch_id = obj.get('tag_batch_id')
    plc_id = obj.get('plc_id')
    return plc_id if plc_id is not None else tag_batch_id


def get_limit_string_for_plc(req, resp, resource, params) -> str:
    """
    Function to return the string for rate limiting
    This function is called by the falcon-limiter package
    """
    # Pull the plc_list from the shared singleton that was initialized at startup
    plc_list = model_PlcList.PlcList()
    # Pull the plc_id from the request body
    obj = req.get_media()
    plc_id = obj.get('plc_id')
    # Fetch and return the rate limit, if any, for the requested plc_id
    for plc in plc_list:
        if plc.id == plc_id:
            return plc.rate_limit
    return ""


def get_limit_string_for_batch(req, resp, resource, params) -> str:
    """
    Function to return the string for rate limiting
    This function is called by the falcon-limiter package
    """
    # Pull the batch_list from the shared singleton that was initialized at startup
    batch_list = model_BatchList.BatchList()
    # Pull the tag_batch_id from the request body
    obj = req.get_media()
    tag_batch_id = obj.get('tag_batch_id')
    # Fetch and return the rate limit, if any, for the requested tag_batch_id
    for batch in batch_list:
        if batch.id == tag_batch_id:
            return batch.rate_limit
    return ""
