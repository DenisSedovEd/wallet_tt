#!/bin/sh

set -e

echo "Apply alembic migrations"

alembic upgrade head

echo "Successfully alembic migrations"

exec "$@"