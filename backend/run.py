"""
Custom Flask server runner that suppresses the Server header.

This overrides Werkzeug's default request handler to prevent version information
leakage via the Server HTTP response header (OWASP ZAP finding).
"""

import os
from werkzeug.serving import run_simple, WSGIRequestHandler
from app import create_app


class CustomRequestHandler(WSGIRequestHandler):
    """Request handler that suppresses Server header."""

    def version_string(self):
        """Return empty string to suppress Server header."""
        return ""

    server_version = ""
    sys_version = ""


if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("BACKEND_PORT", 8000))

    # Make reloader/debugger configurable for Docker compatibility
    # Set FLASK_DEBUG=false in production to disable
    debug_mode = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    print(
        f"Starting Flask server on 0.0.0.0:{port} (Server header suppressed, debug={debug_mode})"
    )

    run_simple(
        "0.0.0.0",
        port,
        app,
        request_handler=CustomRequestHandler,
        use_reloader=debug_mode,
        use_debugger=debug_mode,
    )
