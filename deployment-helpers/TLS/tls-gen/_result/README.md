Placeholder to set up a `TLS GEN _result (with secrets)` folder for the repository.

Expected in this directory:
* ca_certificate.pem (not in source control) - the CA cert that signed the generated server_certificate.
* ca_key.pem (not in source control) - the CA key that signed the generated ca_certificate.
* client_certificate.pem (not in source control) - the client certificate that can be used to access the server_certificate.
* client_key.pem/p12 (not in source control) - the client key that can be used with the client_certificate.
* server_certificate.pem (not in source control) - the server certificate generated and signed with the ca_certificate.
* server_key.pem/p12 (not in source control) - the server key that can be used with the server_certificate.
