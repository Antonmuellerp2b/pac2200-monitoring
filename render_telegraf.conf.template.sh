#!/bin/bash
# build_conf.sh
# creates telegraf.conf from telegraf.conf.template using environment variables from .env file

# export all variables from .env
set -a
source .env
set +a

# template and target files
TEMPLATE="telegraf/telegraf.conf.template"
TARGET="telegraf/telegraf.conf"

# replace placeholders in template with environment variables
envsubst < "$TEMPLATE" > "$TARGET"