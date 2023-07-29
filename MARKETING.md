# Marketing Snippets

## Social Media Posts

**Post 1**

The Open Source Project pylogix-webserver is an open source project that provides a web server front-end with a REST HTTP API for interacting with Logix PLCs using the PyLogix Library. This web server allows for controlled access to a limited set of PLC data, including retrieving tag lists, tag values, and PLC time. It is useful in scenarios where authentication and authorization are required between client applications and PLCs, as it provides a middle layer for authentication and authorization using tokens. The web server can be configured to restrict access to specific tag names or patterns, allowing for controlled and secure data retrieval. It also supports network isolation, ensuring that client applications can only connect to the web server and not directly to the PLC protocols. The project is not officially sanctioned by Pylogix or Allen Bradley/Rockwell Automation, and PLC configuration is minimal, requiring the declaration of PLCs and their accessible tags in a configuration file. The web server implements basic authentication, where client applications must provide a token in the Authorization header. The project includes detailed instructions for starting the web server, deploying it with Docker and Nginx, and testing it with compatible HTTP client requests.

Learn more about it at https://github.com/ericwastaken/pylogix-webserver.

#PylogixWebServer #PLC #RESTAPI #PyLogixLibrary #Authentication #Authorization #WebServer #DataAccess #ControlledAccess #PLCIntegration #NetworkIsolation #Security #Automation #IndustrialControlSystems #OpenSource #Technology

**Post 2 - Introducing Rate Limits**

🚀 Introducing Pylogix Webserver with New Feature "Rate Limiting" 🚀

I'm excited to reintroduce the Pylogix Webserver project! For those who are new, Pylogix Webserver is a web server front-end (REST HTTP API) designed to interface with Logix PLCs using the PyLogix Library. It provides structured controlled access to a limited set of PLC data, including GetTagList, GetTagValues, and GetPLCTime functionalities.

**Why is PyLogix Webserver useful?**

This web server serves as a crucial mediator between client applications and PLCs, providing authentication and authorization to the PLC data. Since EtherNet/IP protocol lacks built-in authentication, PyLogix Webserver bridges the gap and enforces strict data access controls. It offers the following key features:

1. Authentication & Authorization: Separates client applications from direct access to PLCs, ensuring only authorized clients can access the data through valid tokens defined by the web server administrators.
2. Data Access Control: Allows fine-grained control over the data that can be retrieved from the PLC. You can specify allowed or excluded tag names using regular expressions or explicit tag names.
3. Rate Limiting: The latest addition to the web server's feature set! Now, you can enforce rate limits on the number of reads per second, minute, hour, day, month, or year for each PLC or batch of tags. This helps prevent clients from overwhelming the web server and downstream PLCs with excessive requests.

**How does Rate Limiting work?**

Rate limiting is configurable both at the PLC and batch levels. The rate limits are defined using a rate limit string notation, such as "2 per minute" or "10 per hour." You can also combine multiple rate limits for added flexibility.

To get started, create your own PLC configuration and authentication tokens files, and follow the deployment guidelines provided in the project's documentation. 

You can find the detailed project description and usage guidelines in the repository. Feel free to contribute, report issues, or share your feedback. Let's make PyLogix Webserver an even more robust and valuable tool for the controls engineering community!

Check out the project here: [Pylogix Web Server](https://github.com/ericwastaken/pylogix-webserver)

Please note that this project is not officially sanctioned by the Pylogix library nor Allen Bradley / Rockwell Automation. However, it is a powerful tool that can significantly enhance the security and control of your PLC data.

#PylogixWebServer #PLC #RESTAPI #PyLogixLibrary #Authentication #Authorization #WebServer #DataAccess #ControlledAccess #PLCIntegration #NetworkIsolation #Security #Automation #IndustrialControlSystems #OpenSource #Technology #RateLimiting