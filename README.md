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

PLCs that can be access by the Pylogix library can be accessed by this web server. The web server is configured with a list of PLCs.

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

TODO: Discuss how to start the webserver with the shell script and the env/command line variables.

### Endpoints

- get tag list (TODO: explain types and how they're merged back into results)
- get tag values (TODO: explain the results, including the type key that is added.)
- get tag batches (TODO: explain batch_list, including the type key that is added.)

## Deploying

This web server must always be deployed behind TLS (a best practice). It is not safe to deploy this web server without TLS, even in testing setups. Please see the README.md in the **./deployment-helpers/TLS/** directory for help creating a self-signed certificate suitable for testing. In production, you should use a certificate from a trusted CA!

### Docker + Nginx

TODO: Write Docker+Nginx instructions.

### Nginx Native

You can use the same configuration as the Docker + Nginx setup, but you'll have to install and configure Nginx yourself.

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

Tested with Python 3.11.4 on macOs. Should work with any Python 3.6+.

You must provide Python in your environment. Ways of doing this:

**Native Setup**

Checkout this repo on a workstation that has Python3 natively.

**PyCharm Setup**

If using PyCharm, make sure you have Python 3.11.4 and then create a new virtual environment to match. This is not tested in Windows, but should work fine if you have Python 3.11.4 installed and create a virtual environment to match.

On PyCharm on macOS, it's best to install Python with Homebrew `brew install python3` then set your System Interpreter within PyCharm to the Homebrew version (typically **/usr/local/bin/python3** or **/opt/homebrew/bin/python3**). After that, create a new virtual environment with the same Homebrew version as base. The venv is not part of the repository, so you must create it if you want to run the server locally.

**Docker Setup**

As an alternative, you can use the Docker version of the server, which will run in a container with Python 3.11.4 installed inside the container. See the **Docker + Nginx** section above for more details.

## NodeJS

NodeJS is only used for formatting JSON files with prettier. It's not used for the server itself.

## Roadmap TODOs
- README todo items
- Crete a Docker compose deployment.
  - copies the code, python 3.11.4, install requirements, bind conf, data in a volume
  - fix PyCharm's run-config for the docker-compose deployment
- Document Nginx native (after Docker container, so I have the nginx conf)
- Test all the calls with unresponsive PLC
  - "description": "An internal error occurred. Details: 'NoneType' object has no attribute 'timestamp'"

## Future TODOs
- (maybe) Support more features from the underlying PyLogix (other than tag write or other operations that change PLC data)?
- (maybe, unlikely we want this unless much more security is added) Writing tags (or other PLC data changes) with granular permissions (could be limited to certain tokens, or even certain tags explicitly configured.)
- (maybe) Stricter adherence to REST specifications?
- (if needed) other authentication methods? (LDAP/RADIUS, etc.)

## Known limitations
- In plc_io
  - Sometimes get "'utf-8' codec can't decode byte 0xfb in position 4: invalid start byte" when reading some timers ("TON_A", "TON_B" from a test rig, of type TIMER). Other timers read fine. This is an issue with my test rig, and I'm not sure if it's necessary to look into further.
  - Inside a read-tag-list, a failure causes the whole call to bail. Since this one call to pylogix fails, this means that a single bad tag inside a tag list causes the whole call to fail.
