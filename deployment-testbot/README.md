# Prefect - TestBot Deployment

TestBot-compatible deployment scripts for Prefect workflow orchestration platform.

## Files

- **setup.sh** - Starts Prefect server and registers sample flows
- **get-token.sh** - No auth required (outputs empty string)
- **docker-compose.yml** - Service configuration (includes PostgreSQL)

## TestBot Configuration

```yaml
- uses: skyramp/testbot@v1
  with:
    skyramp_license_file: ${{ secrets.SKYRAMP_LICENSE }}
    cursor_api_key: ${{ secrets.CURSOR_API_KEY }}
    target_setup_command: './deployment-testbot/prefect/setup.sh'
    target_ready_check_command: 'curl -f http://localhost:4200/api/health'
    target_teardown_command: 'docker-compose -f deployment-testbot/prefect/docker-compose.yml down'
    # No auth_token_command needed - Prefect has no auth in dev mode
```

## Application Details

- **Port:** 4200
- **API Base:** http://localhost:4200/api
- **Web UI:** http://localhost:4200
- **Health Endpoint:** /api/health
- **Auth Type:** None (open access)

## API Endpoints

- `GET /api/flows` - List flows
- `POST /api/flows` - Create flow
- `GET /api/flows/{id}` - Get flow
- `GET /api/flow_runs` - List flow runs
- `POST /api/flow_runs` - Create flow run
- `GET /api/deployments` - List deployments

## Manual Testing

```bash
# Start services
./setup.sh

# Test API (no auth required)
curl http://localhost:4200/api/flows

# Stop services
docker-compose down
```

## Test Data

Setup script creates 2 sample flows:
- TestBot Sample Flow (math operations)
- Hello World Flow (simple greeting)
