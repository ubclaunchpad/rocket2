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

echo "19 0,12 * * * ${PWD}/scripts/certbot_updateall.sh" >> crontab.txt

crontab crontab.txt
rm crontab.txt

mkdir -p /etc/nginx
cp nginx.conf /etc/nginx/nginx.conf
