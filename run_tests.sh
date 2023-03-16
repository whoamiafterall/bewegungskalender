#!/bin/sh

set -e

echo starting radicale server..
cd tests/radicale_server
podman-compose up -d > /dev/null
echo running tests..
cd ../..
set +e
pytest
pytest_out=$?
set -e
echo stopping radicale server..
cd tests/radicale_server
podman-compose down > /dev/null
exit $pytest_out
