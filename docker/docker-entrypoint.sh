#!/bin/sh

set -o errexit
set -o nounset

echo "Docker entrypoint script running..."

check_db() {
python << END
import os
import sys
import psycopg

try:
    conn = psycopg.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', 5432),
    )
except psycopg.OperationalError as e:
    print(f"PostgreSQL connection failed: {e}")
    sys.exit(-1)

print("Postgres is up - continuing...")
sys.exit(0)
END
}

# Waiting for a DB
echo "Checking PostgreSQL readiness..."
until check_db; do
    echo "PostgreSQL is unavailable - waiting..."
    sleep 1
done

# Migrations running
echo "Running migrations…"
alembic upgrade head

# Пропускаем проверку Kafka - закомментировано
# echo "Checking Kafka readiness..."
# until check_kafka; do
#   echo "Kafka is unavailable - waiting..."
#   sleep 1
# done

echo "Skipping Kafka check for development..."

# Application startup
echo "Starting application…"
if [ "${DEBUG:-0}" = "1" ]; then
    echo "Running in DEBUG mode with auto-reload"
    watchfiles "python -m src.core.entrypoint" --sigint
else
    python -m src.core.entrypoint
fi