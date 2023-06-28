# Marketing Snippets

## Social Media Posts

**Post 1**

The Open Source Project pylogix-webserver is an open source project that provides a web server front-end with a REST HTTP API for interacting with Logix PLCs using the PyLogix Library. This web server allows for controlled access to a limited set of PLC data, including retrieving tag lists, tag values, and PLC time. It is useful in scenarios where authentication and authorization are required between client applications and PLCs, as it provides a middle layer for authentication and authorization using tokens. The web server can be configured to restrict access to specific tag names or patterns, allowing for controlled and secure data retrieval. It also supports network isolation, ensuring that client applications can only connect to the web server and not directly to the PLC protocols. The project is not officially sanctioned by Pylogix or Allen Bradley/Rockwell Automation, and PLC configuration is minimal, requiring the declaration of PLCs and their accessible tags in a configuration file. The web server implements basic authentication, where client applications must provide a token in the Authorization header. The project includes detailed instructions for starting the web server, deploying it with Docker and Nginx, and testing it with compatible HTTP client requests.

Learn more about it at https://github.com/ericwastaken/pylogix-webserver.

#PylogixWebServer #PLC #RESTAPI #PyLogixLibrary #Authentication #Authorization #WebServer #DataAccess #ControlledAccess #PLCIntegration #NetworkIsolation #Security #Automation #IndustrialControlSystems #OpenSource #Technology