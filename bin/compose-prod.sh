#!/bin/sh

docker compose -f ./compose.yml -f ./docker/compose.prod.yml "$@"
