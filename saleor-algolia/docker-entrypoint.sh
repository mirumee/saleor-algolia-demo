#!/bin/bash

set -e

if [ -n "$CHAMBER_SECRET_GROUP" ]; then
    # Use secrets from Chamber
    echo "Fetching secrets from chamber"
    CMD_PREFIX="chamber exec $CHAMBER_SECRET_GROUP --"
else
    # No chamber
    echo "No chamber parameters found"
    CMD_PREFIX=""
fi

echo "Upgrade migrations"
$CMD_PREFIX alembic upgrade heads

exec env $CMD_PREFIX "$@"
