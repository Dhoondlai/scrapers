#!/bin/bash

# bash file to start dynamodb docker container with table and dynamodb-admin (local gui)
# usage: ./setup-env.sh
# start dynamodb container

docker-compose up -d
# start dynamodb-admin
dynamodb-admin &
# check if table exists
table_exists=$(aws dynamodb list-tables --endpoint-url http://localhost:8000 | grep -c "products")
# if table does not exist, create table
if [ $table_exists -eq 0 ]; then
    aws dynamodb create-table --table-name products \
    --attribute-definitions AttributeName=name,AttributeType=S AttributeName=vendor,AttributeType=S \
    --key-schema AttributeName=name,KeyType=HASH AttributeName=vendor,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url http://localhost:8000
fi
