"""MCP Test Server — 65 deterministic tools for MCP protocol testing."""

import argparse
import asyncio

import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_test_server.api import create_api_routes
from mcp_test_server.tools import register_all

mcp = FastMCP(
    name="mcp-testkit",
    instructions="A test server with 65 deterministic tools across 8 groups for MCP protocol testing.",
)

register_all(mcp)


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """ASGI middleware that requires a Bearer token on every request."""

    def __init__(self, app, auth_key: str):
        super().__init__(app)
        self.auth_key = auth_key

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("authorization", "")
        if not auth_header.startswith("Bearer ") or auth_header[7:] != self.auth_key:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        return await call_next(request)


def _build_http_app(auth_key=None):
    """Build Streamable HTTP Starlette app with REST API routes and optional auth."""
    app = mcp.streamable_http_app()

    # Add REST API routes
    api_routes = create_api_routes(mcp)
    for route in api_routes:
        app.routes.append(route)

    if auth_key:
        app.add_middleware(BearerAuthMiddleware, auth_key=auth_key)

    return app


def main():
    parser = argparse.ArgumentParser(description="MCP Test Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument("--host", default="127.0.0.1", help="HTTP host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=3001, help="HTTP port (default: 3001)")
    parser.add_argument("--auth", default=None, help="Bearer auth key (enables authentication for HTTP)")
    args = parser.parse_args()

    if args.transport == "http":
        mcp.settings.host = args.host
        mcp.settings.port = args.port

        app = _build_http_app(auth_key=args.auth)
        config = uvicorn.Config(
            app,
            host=args.host,
            port=args.port,
            log_level="info",
        )
        server = uvicorn.Server(config)
        asyncio.run(server.serve())
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
