#!/usr/bin/env bash
set -euxo pipefail
docker run --rm -it -p 0.0.0.0:5000:5000 $@ rocket2-dev-img
