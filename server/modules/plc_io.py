# Python dependencies
from pylogix import PLC

# Project dependencies
import utils

# Default logging to DEBUG
import modules.logger as logger
shared_logger = logger.CustomLogger()


def get_tag_list(plc_id, ip, slot_no=0, port=44818):
    """Gets a tag_list from a PLC.
    :param plc_id: The ID of the PLC
    :param slot_no: The slot number of the PLC
    :param ip: The IP address of the PLC
    :param port: The port number of the PLC
    :return: A dictionary of tag names and data types

    If the tag list can't be retrieved, returns None.
    """

    # Raise exception if plc_id, ip are missing
    if not plc_id or not ip:
        raise Exception(f'Missing required plc_id or ip call.')

    with PLC() as comm:
        comm.IPAddress = ip
        comm.Port = port
        if slot_no > 0:
            comm.ProcessorSlot = int(slot_no)
        shared_logger.log.debug(f'plc_id="{plc_id}" comm = {str(comm)}')

        try:
            tag_list_object = {}
            tag_list = process_plc_generic_response_item(comm.GetTagList())
            # Tag list could still be empty
            if tag_list is not None:
                # We have a tag list, so process into a dictionary
                for t in tag_list:
                    # Skip "Program:MainProgram" tag
                    if t.TagName == "Program:MainProgram":
                        continue
                    tag_list_object[t.TagName] = {"type": t.DataType}
            else:
                # We have no tag list, so raise an error
                raise Exception(f'No tag list retrieved for {plc_id}.')

            # Otherwise, we're good, so return the new dictionary
            return tag_list_object

        except Exception as e:
            custom_exception_message = f'plc_id="{plc_id}" {e}'
            shared_logger.log.error(custom_exception_message)
            raise Exception(custom_exception_message) from e


def get_tag_value(plc_id, ip, slot_no=0, port=44818, tag_name=""):
    """Gets a tag value from a PLC.
    :param plc_id: The ID of the PLC
    :param slot_no: The slot number of the PLC
    :param ip: The IP address of the PLC
    :param port: The port number of the PLC
    :param tag_name: The name of the tag to read
    :return: A tuple with a single item list of value of the tag (inside a dictionary), and the PLC time.

    If the tag value can't be retrieved, returns None for its value.

    Note the tag_value returned could be of ANY type, coerced by the Pylogix library
    into the proper Python type!
    """

    # Raise exception if plc_id, ip are missing
    if not plc_id or not ip:
        raise Exception(f'Missing required plc_id or ip call.')

    # Raise exception if tag_name is missing
    if not tag_name:
        raise Exception(f'Missing tag_name in call to plc_id="{plc_id}"')

    # Call get_tag_values with a single tag and return in a list of 1
    return get_tag_values(plc_id, ip, slot_no, port, [tag_name])


def get_tag_values(plc_id, ip, slot_no=0, port=44818, tag_list=[""]):
    """Gets a list of tag values from a PLC.

    :param plc_id: The ID of the PLC
    :param slot_no: The slot number of the PLC
    :param ip: The IP address of the PLC
    :param port: The port number of the PLC
    :param tag_list: The list of tag names to read (list of strings)
    :return: A tuple with the list of values of the tags (inside a dictionary each), and the PLC time.

    If any of the tags can't be retrieved, returns None for that tag's value.

    The dictionary has the following structure:
    {
        "tag_name": "NAME-HERE",
        "value": "value" | 999 | None (Note data type can be any type depending on the underlying
                                        response),
        "success": True | False,
        "status": "status" (if success is False, this will contain the error message from PyLogix)
    }

    Note the tag_value returned could be of ANY type, coerced by the Pylogix library
    into the proper Python type!

    NOTE: From PyLogix examples: Packets have a ~500 byte limit, so you have
    to be cautions about not exceeding that or the read will fail. It's a little
    difficult to predict how many bytes your reads will take up because
    the packet will depend on the length of the tag name and the
    reply will depend on the data type. Strings are a lot longer than
    DINT's for example.
    """

    # Raise exception if plc_id, ip are missing
    if not plc_id or not ip:
        raise Exception(f'Missing required plc_id or ip call.')

    # Raise exception if tag_list is invalid
    if not utils.is_list_of_strings(tag_list):
        raise Exception(f"tag_list must be an array of strings. Received: {tag_list}.")

    with PLC() as comm:
        comm.IPAddress = ip
        comm.Port = port
        if slot_no > 0:
            comm.ProcessorSlot = int(slot_no)
        shared_logger.log.debug(f'plc_id="{plc_id}" comm = {str(comm)}')

        try:
            # read PLC TIME and set to variable
            plc_time = process_plc_generic_response_item(comm.GetPLCTime())
        except Exception as e:
            custom_exception_message = f'Could not read PLCTime for plc_id="{plc_id}" {e}'
            shared_logger.log.error(custom_exception_message)

        try:
            # read tag list
            tag_list_values = process_plc_tag_response(comm.Read(tag_list))
            # return the values of the tags, including status, which should be checked by the caller
            return tag_list_values, plc_time

        except Exception as e:
            custom_exception_message = f'plc_id="{plc_id}" {e}'
            shared_logger.log.error(custom_exception_message)
            raise Exception(custom_exception_message) from e


def process_plc_tag_response(response):
    """
    Processes a pylogix GetTag response into a dictionary we define. If reading a single tag, the response is a single
    item list dictionary. If reading multiple tags, the response is a multi-item list of dictionaries.

    Use process_plc_generic_response_item for other PLC calls!

    :param response:
    :return: a custom dictionary with: tag_name, value (whatever type is returned from the PLC),
        success (bool - whether the read was successful or not), and status message from PyLogix
        if success != true.
    """
    # response might be an individual response, or a list. If it's a list, we need to process each item
    if isinstance(response, list):
        # Create a new list to hold the processed responses
        processed_responses = []
        # Loop through each item in the list
        for item in response:
            # Process the item and add it to the new list
            processed_responses.append(process_plc_tag_response_item(item))
        # Return the new list
        return processed_responses
    else:
        # Process the item and return it
        return [process_plc_tag_response_item(response)]


def process_plc_tag_response_item(response_item):
    """
    Processes a pylogix GetTag response item into a dictionary we define.
    Use process_plc_generic_response_item for other PLC calls!

    :param response_item:
    :return: a custom dictionary with: tag_name, value (whatever type is returned from the PLC),
        success (bool - whether the read was successful or not), and status message from PyLogix
        if success != true.
    """
    # if response.Status is not "Success" then throw an exception
    success = True
    if 'Success' not in str(response_item.Status):
        success = False
    # Else no error, so get the response_item_normalized we're aiming for
    # TODO: Use a defined class here instead of hard coding the dictionary
    response_item_normalized = {
        "tag_name": response_item.TagName,
        "value": response_item.Value if success else None,
        "success": success,
        "status": f"{response_item.Status if not success else ''}"
    }
    # return the response_item_normalized
    return response_item_normalized


def process_plc_generic_response_item(response_item):
    """
    Processes a pylogix response item into a response value. Not suitable for lists of responses!
    Works best with GetPLCTime, GetTagList or other calls that return a single response.

    :param response_item:
    :return: a value from the response or None if value is not available (due to error or otherwise.)
    """
    # if response.Status is not "Success" then throw an exception
    if 'Success' in str(response_item.Status):
        # No error, so get the response value
        return response_item.Value
    else:
        return None
