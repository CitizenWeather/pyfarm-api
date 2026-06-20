"""pyfarm-api: API gateway for pyfarm ecosystem.

Exposes:
- Control status and history
- Event streams
- Actuator overrides
- User/role management (delegated to pyfarm-auth)
- Multi-user access with JWT authentication
"""

from pyfarm.api.app import create_app
from pyfarm.api.client import ControlClient, get_control_client

__version__ = "0.1.0"

__all__ = [
    "create_app",
    "ControlClient",
    "get_control_client",
]
