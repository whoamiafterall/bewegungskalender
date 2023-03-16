#!/bin/sh

set -e

echo starting radicale server..
cd radicale_server
podman-compose up -d > /dev/null
echo running scripts..
cd ../../src
set +e
for f in ../tests/configs/*.yml; do
  python3 -m post_caldav_events.main --config "$f" > "$f.out"
  rc=$?
  if [ "$rc" != "0" ]; then
    break;
  fi
done
set -e
echo stopping radicale server..
cd ../tests/radicale_server
podman-compose down > /dev/null
exit $rc
