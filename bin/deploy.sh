#!/bin/sh

# git pull origin master
./bin/compose-prod.sh --profile webhook pull
./bin/compose-prod.sh down
./bin/compose-prod.sh --profile webhook up -d
