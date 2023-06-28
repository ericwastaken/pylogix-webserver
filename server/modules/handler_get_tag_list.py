# Python Dependencies
import falcon

# Import our own dependencies
import utils
from middleware_auth import AuthMiddleware
import model_PlcList

# Default logging to DEBUG
import modules.logger as logger
shared_logger = logger.CustomLogger()


class GetTagListHandler:
    """Class that handles the /get_tag_list endpoint"""
    plc_list = None
    tag_lists = None

    def __init__(self, plc_list: model_PlcList, tag_lists):
        self.plc_list = plc_list
        self.tag_lists = tag_lists

    def on_post(self, req, resp):
        """Handler for /get_tag_list post endpoint"""
        shared_logger.log.info("GetTagListHandler | on_post")

        # If middleware has already set a bad status, return immediately
        if AuthMiddleware.is_bad_http_status(resp.status):
            return  # Return response immediately if status is other than in the 200s

        try:

            # get_media and resp.media below are the no-plc_list recommended way to form JSON API's
            obj = req.get_media()
            plc_id = obj.get('plc_id')

            # throw errors if missing required fields
            if not plc_id:
                raise falcon.HTTPBadRequest(
                    title='Malformed body',
                    description='Missing required field: plc_id',
                )

            # find a match for this plc_id in the plc_list
            plc_config = utils.get_plc_config_for_plc_id(self.plc_list, plc_id)

            # if plc_config is empty, respond with http 404 and error message
            if plc_config is None:
                raise falcon.HTTPNotFound(
                    title='PLC not found',
                    description=f"plc_id='{plc_id}' not found in the config! Check your value and try again.",
                )

            # Otherwise, we have a plc_list, so go get the tag list for it
            tag_list, tag_list_timestamp = self.tag_lists.get_tag_list(plc_config, )

            # Did we get a tag list?
            if tag_list is None:
                raise Exception(f"tag_list not available for plc_id='{plc_id}'!")

            # Otherwise, respond with the tag list
            resp.media = {'plc_id': plc_id, 'tag_list': tag_list, 'plc_time': tag_list_timestamp}
            resp.status = falcon.HTTP_200

        except Exception as e:
            shared_logger.log.error(f'GetTagListHandler | on_post | {e}')
            # if e is type falcon.HTTPError, it means we raised it above, so just re-raise it
            if isinstance(e, falcon.HTTPError):
                raise e
            # otherwise, we have an internal error, so raise a 500
            raise falcon.HTTPInternalServerError(
                title='Internal server error',
                description=f'An internal error occurred. Details: {e}',
            )
