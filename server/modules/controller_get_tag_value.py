# Python dependencies
import json

# Import our own dependencies
import plc_io
import utils
import model_PlcList

# Default logging to DEBUG
import modules.logger as logger

shared_logger = logger.CustomLogger()


class TagValue:

    @classmethod
    def get_tag_value(cls, plc_config: model_PlcList.PlcConfig, tag_name):
        """Get a tag value and coerce it to the proper TYPE.
        :param plc_config: a JSON object that has the properties id, ip, port, and plc_slot
        :param tag_name: the name of the tag to get the value for
        :return: A tuple with a single item list of value of the tag (inside a dictionary), and the PLC time.

        If the tag value can't be retrieved, returns None for its value.

        Note the tag_value returned could be of ANY type, coerced by the Pylogix library
        into the proper Python type!
        """
        shared_logger.log.debug(f'Getting tag value for plc_config: {plc_config}')

        plc_ip = plc_config.ip
        plc_slot = plc_config.slot
        plc_id = plc_config.id
        plc_port = plc_config.port

        # Check if we were passed the needed items ip, plc_slot, id, port and return with error if not
        if not plc_ip or not isinstance(plc_slot, int) or not plc_id or not plc_port:
            raise Exception(f'Missing required field(s) in plc_config: {plc_config}')

        return TagValue.get_tag_values(plc_config, [tag_name])

    @classmethod
    def get_tag_values(cls, plc_config: model_PlcList.PlcConfig, tag_list):
        """Get a list of tag values from a tag list (each coerced to the proper TYPE).
        :param plc_config: a JSON object that has the properties id, ip, port, and plc_slot
        :param tag_list: a list of tag names to get the values for (List of strings)
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

        Note the tag_values returned could be of ANY type, coerced by the Pylogix library
        into the proper Python type!
        """
        shared_logger.log.debug(f'Getting tag values for plc_config: {plc_config}')

        # if tag_list is not a List of strings, raise exception
        if not utils.is_list_of_strings(tag_list):
            raise Exception(f"tag_list must be an array of strings. Received: {tag_list}.")

        plc_ip = plc_config.ip
        plc_slot = plc_config.slot
        plc_id = plc_config.id
        plc_port = plc_config.port

        # Check if we were passed the needed items ip, plc_slot, id, port and return with error if not
        if not plc_ip or not isinstance(plc_slot, int) or not plc_id or not plc_port:
            raise Exception(f'Missing required field(s) in plc_config: {plc_config}')

        try:
            # Process allow/disallow list (may remove some items from the tag list)
            tag_list, tag_list_filtered = utils.process_allow_disallow_tag_list(tag_list, plc_config)

            # Get the tag values from the PLC (note we use the filtered tag list)
            tag_values, tag_value_timestamp = plc_io.get_tag_values(plc_id, plc_ip, plc_slot, plc_port,
                                                                    tag_list_filtered)

            # Did we get a tag values?
            if tag_values is None:
                raise Exception(f"tag_values not available for plc_id='{plc_id}' and tag_list='{tag_list}'!")

            # Otherwise, respond with the tag value
            return tag_values, tag_value_timestamp

        except Exception as e:
            shared_logger.log.error(f'GetTagValueHandler | on_post | {e}')
            return None, None
