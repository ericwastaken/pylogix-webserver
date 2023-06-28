# Python Dependencies
import falcon

# Import our own dependencies
import utils
from controller_get_tag_value import *
import model_PlcList
import model_BatchList

# Default logging to DEBUG
import modules.logger as logger
from middleware_auth import AuthMiddleware

shared_logger = logger.CustomLogger()


class GetTagBatchHandler:
    """Class that handles the /get_tag_batch endpoint"""
    plc_list = None
    tag_lists = None
    batch_list = None

    def __init__(self, plc_list: model_PlcList, tag_lists, batch_list: model_BatchList):
        self.plc_list = plc_list
        self.tag_lists = tag_lists
        self.batch_list = batch_list

    def on_post(self, req, resp):
        """Handler for /get_tag_batch post endpoint"""
        shared_logger.log.info("GetTagBatchHandler | on_post")

        # If middleware has already set a bad status, return immediately
        if AuthMiddleware.is_bad_http_status(resp.status):
            return  # Return response immediately if status is other than in the 200s

        try:

            # get_media and resp.media below are the no-config recommended way to form JSON API's
            obj = req.get_media()
            tag_batch_id = obj.get('tag_batch_id')

            # throw errors if missing required fields
            if not tag_batch_id:
                raise falcon.HTTPBadRequest(
                    title='Malformed body',
                    description='Missing required fields: tag_batch_id',
                )

            # find a match for this tag_batch_id in the plc_list
            plc_batch_config: model_BatchList.BatchConfig = \
                utils.get_plc_batch_config_for_batch_id(self.batch_list, tag_batch_id)
            # If we don't find a plc_batch_config or the tag_batch_id, we have to throw a Falcon HTTPNotFound error
            if plc_batch_config is None:
                raise falcon.HTTPNotFound(
                    title='tag_batch_id not found',
                    description=f"tag_batch_id='{tag_batch_id}' "
                                f"not found in the config! Check your value and try again.",
                )

            # Otherwise, we found the batch plc_list, so we can continue
            # set the plc_id for this batch
            plc_id = plc_batch_config.plc_id
            tag_list = plc_batch_config.tag_list

            # find a match for this batch's PLC in the plc_list
            plc_config = utils.get_plc_config_for_plc_id(self.plc_list, plc_id)

            # if plc_config is empty, respond with http 404 and error message
            if plc_config is None:
                raise falcon.HTTPNotFound(
                    title='PLC not found',
                    description=f"PLC Config for tag_batch_id='{tag_batch_id}' not found in the config! "
                                f"Check your value and try again.",
                )

            # Now we treat this as a normal tag list request

            # Go get the tag list values (note the plural "values" in the method name)
            tag_value_list, tag_value_timestamp = TagValue.get_tag_values(plc_config, tag_list)

            # Did we get a tag value list response?
            if tag_value_list is None:
                raise Exception(f"tag_value_list not available for tag_batch_id='{tag_batch_id}'!")

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
