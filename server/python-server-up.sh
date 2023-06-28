#!/bin/bash

# Note, the ENV VARS are to be set by the docker-compose.yml file or docker command line or .env file!

# In the command below:
# -u: force the stdout and stderr streams to be unbuffered. This was required in order to see python app logs in docker instantly (w/out waiting for buffer to fill)
python -u "${PY_SCRIPT}" \
  --host "${HOST}" \
  --port "${PORT}" \
  --cache-directory "${PLC_CACHE_DIRECTORY}" \
  --config-file-path "${PLC_CONFIG_FILE_PATH}" \
  --auth-token-file-path "${AUTH_TOKENS_FILE_PATH}" \
  --cache-ttl "${CACHE_TTL}"
