#!/bin/bash
set -e

# TestBot Setup Script for Prefect
# This script starts Prefect server and registers sample flows

cd "$(dirname "$0")"

echo "Starting Prefect service..."
docker compose up -d

echo "Waiting for service to be ready..."
sleep 15

echo "Initializing database tables for new features..."
docker compose exec -T prefect-server python3 /opt/prefect/init-db.py || echo "Warning: DB init failed, tables may already exist"

echo "Creating sample flows..."
# Create Python script for sample flows
docker compose exec -T prefect-server bash << 'EOF'
export PREFECT_API_URL=http://localhost:4200/api
pip install -q httpx 2>/dev/null || true

python3 << 'PYEOF'
from prefect import flow, task

@task
def add_numbers(x: int, y: int):
    return x + y

@flow(name="TestBot Sample Flow")
def sample_flow(x: int = 10, y: int = 5):
    result = add_numbers(x, y)
    return result

@flow(name="Hello World Flow")
def hello_flow(name: str = "TestBot"):
    return f"Hello {name}!"

if __name__ == "__main__":
    try:
        sample_flow()
        hello_flow()
        print("Flows registered successfully")
    except Exception as e:
        print(f"Warning: {e}")
PYEOF
EOF

echo "✓ Prefect setup complete"
