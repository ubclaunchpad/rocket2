#!/usr/bin/env bash
set -euxo pipefail

docker run --rm --name letsencrypt \
    -v "/etc/letsencrypt:/etc/letsencrypt" \
    -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
    -v "/usr/share/nginx/html:/usr/share/nginx/html" \
    certbot/certbot:latest \
    renew --quiet