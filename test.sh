#!/bin/bash

# bash file to contain commands to run a scraper locally.

# example usage: ./test.sh techmatched

serverless invoke local --function $1 --debug