#!/bin/bash

docker compose -f ./compose.yml -f ./docker/compose.prod.yml -f ./docker/compose.caddy.yml "$@"
