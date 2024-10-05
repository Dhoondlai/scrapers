#!/bin/bash

# bash file to start mongodb docker container with table and mongodb client (local gui)
# usage: ./setup-env.sh

# add mongodb compass here

cd scripts && docker-compose up -d
echo "Opening MongoDB Compass..."
start "" "C:\Users\Khanh\AppData\Local\MongoDBCompass\MongoDBCompass.exe"
