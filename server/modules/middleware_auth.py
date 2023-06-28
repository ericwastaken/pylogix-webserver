# Python Dependencies
import falcon
import json

# Default logging to DEBUG
import modules.logger as logger
shared_logger = logger.CustomLogger()

class AuthMiddleware:
    def __init__(self, tokens_file_path):
        self.tokens = self.load_tokens(tokens_file_path)

    def process_request(self, req, resp):
        auth_header = req.get_header('Authorization')
        if auth_header:
            auth_type, auth_string = auth_header.split(' ')
            if auth_type.lower() == 'basic':
                # Compare the passed in auth_string to the tokens loaded from the tokens file
                if auth_string in self.tokens:
                    shared_logger.log.debug(f"AuthMiddleware | process_request | Auth is ok!")
                    return
        shared_logger.log.debug(f"AuthMiddleware | process_request | Auth fails!")
        resp.status = falcon.HTTP_401
        resp.media = {'message': 'Authentication failed. Please check your AUTH TOKEN and try again.'}

    @classmethod
    def load_tokens(cls, tokens_file):
        try:
            with open(tokens_file) as f:
                tokens = json.load(f)
            return tokens
        except (IOError, json.JSONDecodeError) as e:
            raise falcon.HTTPInternalServerError(f'Error loading tokens from path="{tokens_file}". {str(e)}')

    @classmethod
    def is_bad_http_status(cls, http_status):
        """Returns True if the http_status is not in the 200s
        :param http_status: The http status code as a string 999 Some String (e.g. "200 OK")
        :return: True if the http_status is not in the 200s
        """
        status_parts = http_status.split(' ')
        status_code = int(status_parts[0])
        return not (200 <= status_code < 300)
