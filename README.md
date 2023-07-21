# Pylogix Web Server

## Summary

This project is a web server front-end (rest http api) to interface with Logix PLCs using the [PyLogix Library](https://github.com/dmroeder/pylogix). The web server provides structured controlled access to a limited set of PLC data. At present, only GetTagList, GetTagValues and GetPLCTime are supported.

Why is this useful? 

This web server is useful to allow a separation between a client application that needs values from a PLC and the PLC itself. Since the [EtherNet/IP](https://literature.rockwellautomation.com/idc/groups/literature/documents/wp/enet-wp001_-en-p.pdf) protocol offers no authentication, this web server can be installed in the middle between a client application and a PLC to provide authentication and authorization to the PLC data. Also, since this webserver can be strict in the data it will access from the PLC, it can be configured at build / deploy time with certain limits that the client application can't exceed. For instance the web server can:

- allow reads of only specific tag names or tag names matching an allow regex.
- explicitly exclude specific tag names or tag names matching an exclude regex.

Furthermore, this web server can be network-isolated in such a way that client applications can't access the EtnerNet/IP protocols directly. Only the web server can access the PLC protocols and network, while client applications only connect to the web server (and are required to hold a valid token defined by the web server administrators.) 

Finally, this webserver can be deployed by the controls engineering team (or an IT team) that can gatekeep the data being accessed. Client applications by other teams can then access the data in a controlled fashion!

## Not Official nor Sanctioned

This project is not related nor sanctioned by either the Pylogix library nor Allen Bradley / Rockwell Automation. Please see the LICENSE file for usage guidelines. 

## PlC Support & Configuration

This web server can access PLCs that can be accessed by the Pylogix library. The web server is configured with a list of PLCs.

PLC configuration is minimal. Expose some tags to be accessible externally and that's it! You can now access them through this web server (with authentication and authorization!)

## Web Server Config File

The **plc-config.json** file in the **conf** directory is where you want to declare a list of PLCs and their tags. It is used by the webserver to know how to access PLCs and if tou use batch_lists, which tags to access.

You can see an example in this repo under **./server/conf/plc-config.template.json5**. Note the example is JSON5 which allows comments, but when you use this to create your own file, you'll have to remove the comments!

* Supports as many PLCs as you want. Just add more entries in `plc_list`.
* Inside each PLC entry, you can choose to provide allow_tags, exclude_tags, allow_tags_regex, and exclude_tags_regex. This allows you to limit the tags that the web server will allow to be retrieved from a PLC. Note that allow/exclude tags takes priority over allow/exclude tags regex, so you want to use one or the other but not both.
* Supports as many batch_lists as you want. Just add more entries in `batch_list`.
  * Note that though having many batch_lists won't affect performance, reading too many tags in a single batch might actually cause a read failure due to limitations in packet size from single reads.
  * Each batch will retrieve values from a single PLC.

## Web Server Authentication

This web server implements basic authentication, which is header based. Client applications must pass an "Authorization" header with "basic \[TOKEN-HERE\]". The passed token is then verified against a list of tokens held by the server.

The file **./conf/auth-tokens.json** should contain one or more tokens that clients can use.

## Web Server Details

### Starting

Before starting:
1. Create your own **./conf/plc-config.json** file based on the template file **./conf/plc-config.template.json5**. See the section above for more details.
2. Create your own **./conf/auth-tokens.json** file based on the template file **./conf/auth-tokens.template.json**. See the section above for more details.

After you have these two files, you can start the web server by changing into the **./server** directory and running:

```bash
$ python -u server.py \
  --host "${HOST}" \
  --port "${PORT}" \
  --cache-directory "${PLC_CACHE_DIRECTORY}" \
  --config-file-path "${PLC_CONFIG_FILE_PATH}" \
  --auth-token-file-path "${AUTH_TOKENS_FILE_PATH}" \
  --cache-ttl "${CACHE_TTL}"
```
- **host** is ip address or hostname to bind to. For testing local "localhost" is suitable. See TLS for more information deploying to servers connected to the internet.
- **port** is the port to bind to. Any port is possible, the examples here use 8000.
- **cache-directory** is the directory where the web server will store cached tag lists data. This is used to speed up subsequent type matching.
- **config-file-path** is the path to the PLC config file discussed above.
- **auth-token-file-path** is the path to the auth token file discussed above.
- **cache-ttl** is the time to live for cached tag lists data. This is used to speed up subsequent type matching. The value is in minutes. 24 hours (1440 minutes) is suitable for environments where the PLC tag list doesn't change often.

Note that the repo includes a convenience script `./python-server-up.sh` that will start the server with the exact command above and pulling from environment variables. Be sure to set those environment variables before running the script or make a copy with static values.

In a PRODUCTION environment, you'll want to front this web server with something more suitable like Nginx as a proxy (and you'll definitely want to set up TLS. See the TLS section below for more information.) A detailed discussion of setting up Nginx as a proxy is outside the scope of this project, but you can see the Docker deployment included as an example.

### Endpoints

The following are the endpoints implemented by the web server. Note all endpoints require an Authentication header. See the Authentication section above for more information.

- get tag list (PyLogix GetTagList): gets the list of tags from a PLC that the web server can access.
  - Example Request:
    ```bash
    curl -X POST --location "http://localhost:8000/get_tag_list" \
        -H "Content-Type: application/json" \
        -H "Authorization: basic your-token-here" \
        -d "{\"plc_id\":\"some-plc-id-from-your-config\"}"
    ```
  - Responds with a JSON object in the form:
    ```json5
    {
      "plc_id": "the ID of the PLC",
      "tag_list": {
        // A key for each TAG in the PLC with the corresponding TYPE.
        "BOOL_Rx": {
          "type": "BOOL"
        }
        // Repeats for as many tags as the PLC has...
      },
      // The PLC time at the time of the tag list fetch
      "plc_time": 1687904399.6868227
    }
    ```


- get tag values (PyLogix GetTagValue): Gets the value of a single tag or a tag list from a PLC that the web server can access.
  - Example Request (pass a single tag):
    ```bash
    curl -X POST --location "http://localhost:8000/get_tag_value" \
      -H "Content-Type: application/json" \
      -H "Authorization: basic your-token-here" \
      -d "{\"plc_id\":\"some-plc-id-from-your-config\", \"tag_name\":\"DINT_Rx\"}"
    ```
  - Example Request (pass a tag list, an array of tag names strings):
    ```bash
    curl -X POST --location "http://localhost:8000/get_tag_value" \
      -H "Content-Type: application/json" \
      -H "Authorization: basic your-token-here" \
      -d "{\"plc_id\":\"some-plc-id-from-your-config\", \"tag_list\":[\"STRING_Rx\",\"DINT_Rx\"]}"
    ```
  - Responds with a JSON object in the form:
    ```json5
    {
    "tag_values": [
      {
        "tag_name": "DINT_Rx",
        "value": 55,
        // Important: If PyLogix can't read the value, success will be false and status will be set to the error message from the library.
        "success": true,
        "status": "",
        // PLC Type is added to the response for convenience - it is not part of the PyLogix response each time, but rather a cached value from the tag list fetch on server startup and updated to match the CACHE TTL in your config.
        "tag_type": "DINT"
      }
      // Repeats for as many tags as were requested...
    ],
    // The PLC time at the time of the tag value fetch
    "plc_time": 884244931.519458
    }
    ```
    - **tag_values** is an array of as many tags as were requested, excluding any tags that were limited or excluded by allow_tags, allow_tag_regex, etc. in your config. Even passing a single tag name will still yield an array of 1 tag value.
    - **plc_time** is the PLC time at the time of the tag value fetch.


- get tag batches (PyLogix GetTagValue with a list of tag names): Gets the value of a tag list, configured via the config file, from a PLC that the web server can access.
  - Example Request:
    ```bash
    $ curl -X POST --location "http://localhost:8000/get_tag_batch" \
      -H "Content-Type: application/json" \
      -H "Authorization: basic your-token-here" \
      -d "{\"tag_batch_id\":\"some-batch-id-from-your-config\"}"
    ```
  - Responds with a JSON object in the form: (identical to get tag value)
    ```json5
    {
    "tag_values": [
      {
        "tag_name": "DINT_Rx",
        "value": 55,
        // Important: If PyLogix can't read the value, success will be false and status will be set to the error message from the library.
        "success": true,
        "status": "",
        // PLC Type is added to the response for convenience - it is not part of the PyLogix response each time, but rather a cached value from the tag list fetch on server startup and updated to match the CACHE TTL in your config.
        "tag_type": "DINT"
      }
      // Repeats for as many tags as were requested...
    ],
    // The PLC time at the time of the tag value fetch
    "plc_time": 884244931.519458
    }
    ```
    - **tag_values** is an array of as many tags as were requested, excluding any tags that were limited or excluded by allow_tags, allow_tag_regex, etc. in your config. Even passing a single tag name will still yield an array of 1 tag value.
    - **plc_time** is the PLC time at the time of the tag value fetch.

## Deploying

This web server must always be deployed behind TLS (the best practice).
It is not safe to deploy this web server without TLS, even in testing setups.
Please see the README.md in the **./deployment-helpers/TLS/** directory for help
creating a self-signed certificate suitable for testing.
In production, you should use a certificate from a trusted CA!

### Docker + Nginx

In this scenario, Docker stands up an NGINX container which receives the HTTPS requests and forwards them to the python backend. This is the recommended deployment method for PROD environments. It's the easiest to set up and maintain plus it supports TLS.

#### Getting Started with the Docker + Nginx Deployment

1. Configure the Pylogix-Webserver per the above instructions.
2. Place your TLS server_certificate.pem and server_key.pem in the **./nginx/secrets/** directory. 
3. From the root of this repository, build the Docker Compose stack with `docker-compose build`.
4. Start the stack with `docker-compose up -d`.

You should now be able to access the POST to the web server at https://localhost/get_tag_list on your docker host. (Replace with whatever hostname is configured for your host, matching the TLS certificate to avoid browser warnings!)

Please see the README.md in the **./deployment-helpers/TLS/** directory for help
creating a self-signed certificate suitable for testing.

### Nginx Native

In this scenario, your own NGINX server receives the HTTPS requests and forwards them to the python backend.

You can use the same configuration as the Docker + Nginx setup, but you'll have to install and configure Nginx yourself.

See the configuration in **./nginx/** for details.

## Testing

> **Note:** Testing this library requires access to an Allen-Bradley/Rockwell Automation PLC that supports EtherNet/IP. I've not found an emulator or other "easy way". I realize this is a costly requirement! Please create an ISSUE in this repo if you know of other ways this library can be tested without access to a real PLC.

The **\*.http** files in the **test** directory are HTTP Client requests with tests supported by either [PyCharm's built-in HTTP Client](https://www.jetbrains.com/help/pycharm/http-client-in-product-code-editor.html) or the [JetBrains standalone HTTP Client CLI](https://www.jetbrains.com/help/pycharm/http-client-cli.html). 

The **test** directory contains an **http-client.env.json** with some values to match a test **plc-config.example.json**.

The directory will not contain **http-client.private.env.json** so you have to provide that file with content like this:

```json
{
  "dev": {
    "request_token": "some-token-here"
  }
}
```

In your **./conf** directory, you'll want compatible **auth-tokens.json** and **plc-config.json** files that look like this:

```json
[
"some-token-here"
]
```

```json
{
  "plc_list": [
    {
      "id": "test 1, slot 0, should not work",
      "ip": "192.168.1.211",
      "port": 44818,
      "slot": 0
    },
    {
      "id": "test 2, slot 0, should work",
      "ip": "192.168.1.210",
      "port": 44818,
      "slot": 0
    }
  ],
  "batch_list": [
    {
      "id": "batch10",
      "plc_id": "test 1, slot 0, should not work",
      "tag_list": ["TAG1", "TAG2"]
    },
    {
      "id": "batch20",
      "plc_id": "crap plc_id",
      "tag_list": ["TAG1", "TAG2"]
    },
    {
      "id": "batch30",
      "plc_id": "test 2, slot 0, should work",
      "tag_list": [
        "BOOL_Rx",
        "DINT_Rx",
        "INT_Rx",
        "REAL_Rx",
        "STRING_Rx",
        "DINT_TIMERA",
        "DINT_TIMERB",
        "DINT_BIT_Rx"
      ]
    }
  ]
}
```

## Python Nuances

Tested with Python 3.11.4 on macOS. Should work with any Python 3.6+.

You must provide Python in your environment. Ways of doing this:

**Native Setup**

Checkout this repo on a workstation that has Python3 natively. You can then create a virtual environment with Python 3.11.4 and install the requirements.txt.

**PyCharm Setup**

If using PyCharm, make sure you have Python 3.11.4 and then create a new virtual environment to match. This is not tested in Windows, but should work fine if you have Python 3.11.4 installed and create a virtual environment to match.

On PyCharm on macOS, it's best to install Python with Homebrew `brew install python3` then set your System Interpreter within PyCharm to the Homebrew version (typically **/usr/local/bin/python3** or **/opt/homebrew/bin/python3**). After that, create a new virtual environment with the same Homebrew version as base. The venv is not part of the repository, so you must create it if you want to run the server locally.

**Docker Setup**

As an alternative, you can use the Docker version of the server, which will run in a container with Python 3.11.4 installed inside the container. See the **Docker + Nginx** section above for more details.

## NodeJS

NodeJS is only used for formatting JSON files with prettier. It's not used for the server itself.

## Roadmap

- Perform more testing of all the calls with an unresponsive PLC
  - "description": "An internal error occurred. Details: 'NoneType' object has no attribute 'timestamp'"
- Enforce rate limits defined per PLC, per client, etc.

## Future

- (maybe) Support more features from the underlying PyLogix (other than tag write or other operations that change PLC data)?
- (maybe, unlikely we want this unless much more security is added) Writing tags (or other PLC data changes) with granular permissions (could be limited to certain tokens, or even certain tags explicitly configured.)
- (maybe) Stricter adherence to REST specifications?
- (if needed) other authentication methods? (LDAP/RADIUS, etc.)

## Known limitations

- In plc_io
  - Sometimes get "'utf-8' codec can't decode byte 0xfb in position 4: invalid start byte" when reading some timers ("TON_A", "TON_B" from a test rig, of type TIMER). Other timers read fine. This is an issue with my test rig, and I'm not sure if it's necessary to look into further.
  - Inside a read-tag-list, a failure causes the whole call to bail. Since this one call to pylogix fails, this means that a single bad tag inside a tag list causes the whole call to fail.
