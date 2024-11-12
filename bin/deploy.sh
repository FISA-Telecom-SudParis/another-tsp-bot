#!/bin/sh

# git pull origin master
./bin/compose-prod.sh pull
./bin/compose-prod.sh down
./bin/compose-prod.sh up -d
