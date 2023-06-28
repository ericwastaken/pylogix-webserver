# Certificates

## Attribution

The version of tls-gen used in this project is an abbreviated simple version of the full library available at https://github.com/rabbitmq/tls-gen.

## Generate Certificates

Note, you only need to GENERATE certs if you are creating a new environment. If you are using an existing environment, you should skip this and instead download the generated certs from the project's secrets storage.

To generate certs:
1. Edit the file `./generate-certs.sh` and change the `make` CN argument to the hostname of the environment you are generating certs for. You should generate a WILDCARD for all hosts in your environment or a specific host, depending on your needs.
2. Once you've edited the file, from your terminal, run `./generate-certs.sh`.
3. Self-signed certs for the domain you specified will be generated in the `./tls-gen/_result/` directory.

## Distributing Certs

Copy the generated certs from the `./tls-gen/_result/` directory as needed.