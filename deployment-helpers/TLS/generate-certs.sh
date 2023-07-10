#!/bin/bash

# This script uses the TLS-GEN library to generate self-signed
# TLS certs suitable to use for RMQ. The certificates will be
# copied to the RMQ Secrets directory after creation!
#
# You can change the domain to suit your needs!
#
# Learn more about TLS-GEN at https://github.com/rabbitmq/tls-gen
#
# DEPENDENCIES:
# The TLS-GEN library requires Python 3.6 or later and openssl.
# Install those prior to running this tool.

# Change into the tool directory. Basis is fine for our use.
# The more advanced options are not included in this repo, but are part of the original.
cd tls-gen/basic/ || exit

# Generate the certs for our desired hostname

# Wildcard for the domain expiring in 100 years
# UPDATE LOCALHOST BELOW TO YOUR OWN DOMAIN AND DESIRED VALIDITY
make CN=localhost DAYS_OF_VALIDITY=36500

# Cleanup
rm -rf server client testca
# Remove any old results
rm -rf ../_result
# Move the results back up
mv result ../_result

