# pyfarm-api

API gateway for the pyfarm ecosystem.

Single inbound HTTP gateway for:
- Control status & history
- Event streaming
- Actuator overrides (with permission checks)
- Integration with pyfarm-auth for multi-user access
- WebSocket for real-time updates

## Quick Start

```python
from pyfarm.api import create_app

app = create_app()
# Run with: uvicorn pyfarm.api.app:app --port 8002
```

Environment variables:
- `CONTROL_URL` — pyfarm-control service (default: http://localhost:8000)
- `AUTH_URL` — pyfarm-auth service (default: http://localhost:8001)

## Architecture

```
pyfarm-api (8002)
  ├─ /health — service status
  ├─ /api/v1/status — current control state
  ├─ /api/v1/history — historical readings
  ├─ /api/v1/events — event log
  └─ /api/v1/override — actuator overrides (operator+)
  
  Dependencies:
  ├─ pyfarm-control (8000) — core engine
  └─ pyfarm-auth (8001) — token validation
```

## Endpoints

All endpoints except `/health` require `Authorization: Bearer <token>` header.

### Control

**GET /api/v1/status** — Current control context
**GET /api/v1/history** — Historical sensor readings
- Query params: sensor_id, metric, limit
**GET /api/v1/events** — Event log
- Query params: limit
**POST /api/v1/override** — Override actuator (operator+)
- Query params: actuator_id, state

### Health

**GET /health** — Service health (no auth required)

## Testing

```bash
pytest tests/
```

## Deployment

### Single-server
```bash
uvicorn pyfarm.api.app:app --host 0.0.0.0 --port 8002
```

### Docker
```dockerfile
FROM python:3.10
RUN pip install pyfarm-api
CMD ["uvicorn", "pyfarm.api.app:app", "--host", "0.0.0.0", "--port", "8002"]
```

### Kubernetes
```yaml
apiVersion: v1
kind: Service
metadata:
  name: pyfarm-api
spec:
  ports:
  - port: 8002
    targetPort: 8002
  selector:
    app: pyfarm-api
```
