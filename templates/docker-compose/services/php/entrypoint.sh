#! /bin/sh

set -e

# start cron
cron -f &

exec docker-php-entrypoint "$${@}"
