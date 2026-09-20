#!/bin/bash
cd ~/garud_core
C="docker compose -f docker-compose.yml -f docker-compose.ci.yml"
trap 'crontab -l | sed "s|^#\(\*/2.*watchdog.sh.*\)|\1|" | crontab -; crontab -l | tail -1' EXIT
crontab -l | sed 's|^\(\*/2.*watchdog.sh.*\)|#\1|' | crontab -
$C build || { echo "BUILD FAILED"; exit 1; }
docker rm -f garud-perimeter garud-shield
$C up -d
sleep 8
docker ps --format '{{.Names}} {{.Status}}'
curl -s -o /dev/null -w "home %{http_code}\n" http://127.0.0.1/
curl -s -o /dev/null -w "garud %{http_code}\n" http://127.0.0.1/garud
