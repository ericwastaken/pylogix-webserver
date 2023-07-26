# Python Dependencies
import argparse
import signal
import sys
import falcon
from falcon_limiter import Limiter
import logging

# Let's get this party started!
from wsgiref.simple_server import make_server

# Bring in own dependencies
import modules.utils as utils
from modules.startup import Startup
from modules.handler_get_tag_list import GetTagListHandler
from modules.handler_get_tag_value import GetTagValueHandler
from modules.handler_get_tag_batch import GetTagBatchHandler
from modules.middleware_auth import AuthMiddleware

# Default logging to DEBUG
import modules.logger as logger
shared_logger = logger.CustomLogger(logging.DEBUG)


# Define a function to handle the SIGINT signal
def handle_sigint(signal, frame):
    shared_logger.log.info("SIGINT received. Stopping server...")
    # Perform cleanup actions here
    shared_logger.log.info("Server stopped.")
    sys.exit(0)


# Register the SIGINT handler
signal.signal(signal.SIGINT, handle_sigint)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Example script with command line arguments")
    parser.add_argument("-d", "--cache-directory", type=utils.validate_directory, help="Existing cache directory")
    parser.add_argument("-c", "--config-file-path", type=utils.validate_file, help="Existing configuration file path")
    parser.add_argument("-s", "--host", type=utils.validate_hostname, help="Valid hostname")
    parser.add_argument("-p", "--port", type=utils.validate_port, help="Valid TCP port number")
    parser.add_argument("-t", "--cache-ttl", type=utils.validate_integer, help="Valid integer")
    parser.add_argument("-a", "--auth-token-file-path", type=utils.validate_file, help="Existing auth tokens file path")
    # Parse the command line arguments. Note, they will be available as args.<argument_name> using the long
    # argument name as the attribute name without the initial "--" and any "-" characters replaced with "_".
    args = parser.parse_args()

    # Set up the server pre-requisites
    plc_list, tag_lists, batch_list = Startup.start(args.config_file_path, args.cache_directory, args.cache_ttl)

    # Set up an empty rate limiter. This will be populated in the handler classes.
    limiter = Limiter()

    # Instantiate the server and hook up the middleware packages for auth and rate limiting
    app = falcon.App(middleware=[AuthMiddleware(args.auth_token_file_path), limiter.middleware])
    # define Server Endpoint Routes and Handlers
    app.add_route('/get_tag_list', GetTagListHandler(plc_list, tag_lists))
    app.add_route('/get_tag_value', GetTagValueHandler(plc_list, tag_lists))
    app.add_route('/get_tag_batch', GetTagBatchHandler(plc_list, tag_lists, batch_list))

    # Below "" means localhost - but you can't use that value directly. (localhost or 127.0.0.1)
    # https://docs.python.org/3/library/wsgiref.html#module-wsgiref.simple_server
    target_host = ""
    if args.host == "localhost" or args.host == "127.0.0.1":
        target_host = ""
    else:
        target_host = args.host
    with make_server(target_host, args.port, app) as httpd:
        shared_logger.log.info('Serving on ' + args.host + ':' + str(args.port) + ' ...')
        # Serve until process is killed
        httpd.serve_forever()
