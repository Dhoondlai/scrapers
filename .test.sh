#!/bin/bash

# bash file to contain commands to run a scraper locally.

# example usage: ./test.sh techmatched

serverless invoke local -e LOCAL=true --function $1 