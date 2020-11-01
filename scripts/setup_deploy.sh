#!/usr/bin/env bash
set -euxo pipefail

docker run --rm \
  -p 443:443 -p 80:80 --name letsencrypt \
  -v "/etc/letsencrypt:/etc/letsencrypt" \
  -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
  certbot/certbot certonly -n \
  -m "president@ubclaunchpad.com" \
  -d rocket2.ubclaunchpad.com \
  --standalone --agree-tos

mkdir -p /etc/nginx
cp nginx.conf /etc/nginx/nginx.conf
