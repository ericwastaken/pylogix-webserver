# Python Dependencies
import falcon

# Import our own dependencies
import utils
from controller_get_tag_value import *

# Default logging to DEBUG
import modules.logger as logger
from middleware_auth import AuthMiddleware

shared_logger = logger.CustomLogger()


class GetTagValueHandler:
    """Class that handles the /get_tag_value endpoint"""
    plc_list = None
    tag_lists = None

    def __init__(self, plc_list, tag_lists):
        self.plc_list = plc_list
        self.tag_lists = tag_lists

    def on_post(self, req, resp):
        """Handler for /get_tag_value post endpoint"""
        shared_logger.log.info("GetTagValueHandler | on_post")

        # If middleware has already set a bad status, return immediately
        if AuthMiddleware.is_bad_http_status(resp.status):
            return  # Return response immediately if status is other than in the 200s

        try:

            # get_media and resp.media below are the no-plc_list recommended way to form JSON API's
            obj = req.get_media()
            plc_id = obj.get('plc_id')
            tag_name = obj.get('tag_name')
            tag_list = obj.get('tag_list')

            # throw errors if missing required fields
            if not plc_id and not (tag_name or tag_list):
                raise falcon.HTTPBadRequest(
                    title='Malformed body',
                    description='Missing required fields: plc_id and one of tag_name or tag_list',
                )

            # find a match for this plc_id in the plc_list
            plc_config = utils.get_plc_config_for_plc_id(self.plc_list, plc_id)

            # if plc_config is empty, respond with http 404 and error message
            if plc_config is None:
                raise falcon.HTTPNotFound(
                    title='PLC not found',
                    description=f"plc_id='{plc_id}' not found in the plc_list! Check your value and try again.",
                )

            # If we received tag_name, that is what we respond for
            if tag_name:
                # Go get the tag value (note the singular "value" in the method name)
                tag_value_list, tag_value_timestamp = TagValue.get_tag_value(plc_config, tag_name)

            else:
                # Go get the tag list values (note the plural "values" in the method name)
                tag_value_list, tag_value_timestamp = TagValue.get_tag_values(plc_config, tag_list)

            # Did we get a tag value list response?
            if tag_value_list is None:
                raise Exception(f"tag_value_list not available for plc_id='{plc_id}'!")

            # tag_value_list is a list of dictionaries, so we match type on each item in the list
            # tag_value will be a REFERENCE to each item in the list, so we can modify each item!
            for tag_value in tag_value_list:
                # Join with the tag list to get the tag type
                tag_type = self.tag_lists.get_tag_type(plc_config, tag_value['tag_name'])
                # Set the tag type on the tag value
                tag_value['tag_type'] = tag_type

            # Respond with the tag value list. Note the tag_value_list is coerced to the proper type in the
            # get_tag_value method (so it could be ANY valid python type).
            resp.media = {
                'tag_values': tag_value_list,
                'plc_time': tag_value_timestamp.timestamp()  # convert to unix timestamp
            }
            resp.status = falcon.HTTP_200

        except Exception as e:
            shared_logger.log.error(f'GetTagValueHandler | on_post | {e}')
            # if e is type falcon.HTTPError, it means we raised it above, so just re-raise it
            if isinstance(e, falcon.HTTPError):
                raise e
            # otherwise, we have an internal error, so raise a 500
            raise falcon.HTTPInternalServerError(
                title='Internal server error',
                description=f'An internal error occurred. Details: {e}',
            )
