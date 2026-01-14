import asyncio
from typing import Dict, Any, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import logging

logger = logging.getLogger(__name__)

class MCPClientManager:
    """
    Manages connections to multiple MCP (Model Context Protocol) servers.
    This demonstrates the "Composition" architectural pattern.
    """
    def __init__(self):
        # Stores active sessions: {"slack": session_obj, "jira": session_obj}
        self.sessions: Dict[str, ClientSession] = {}
        # Stores the background tasks keeping the streams open
        self.exit_stacks: Dict[str, Any] = {}

    async def connect_to_server(self, server_name: str, command: str, args: List[str], env: Dict[str, str] = None):
        """
        Connects to a single MCP server via Stdio (Standard Input/Output).
        In production, this could also use SSE (Server-Sent Events) for remote servers.
        """
        if server_name in self.sessions:
            logger.info(f"Already connected to {server_name}")
            return

        logger.info(f"Connecting to MCP Server: {server_name}...")

        server_params = StdioServerParameters(
            command=command,
            args=args,h
            env=env
        )

        from contextlib import AsyncExitStack
        exit_stack = AsyncExitStack()
        
        try:
            # Open the standard I/O stream to the external MCP server
            stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
            read, writfastapi>=0.110.0
uvicorn[standard]>=0.29.0
python-multipart>=0.0.9      # For handling file uploads/form data
httpx>=0.27.0                # Async HTTP client (needed for internal requests)

# --- Task Queue (Async Workers) ---
celery[redis]>=5.3.6
redis>=5.0.3
watchfiles>=0.21.0           # For hot-reloading Celery during dev

# --- Database & Models ---
sqlalchemy>=2.0.29
asyncpg>=0.29.0              # High-performance Async Postgres driver
alembic>=1.13.1              # Database migrations (CRITICAL for production)
pydantic>=2.7.0
pydantic-settings>=2.2.1     # For strict environment variable validation

# --- AI & Agents (The Brain) ---
langgraph>=0.0.39            # State machine orchestration
langchain>=0.1.16
langchain-core>=0.1.45
langchain-anthropic>=0.1.11  # Or openai if you switch models
mcp>=0.1.0                   # Model Context Protocol SDK

# --- Utilities ---
python-dotenv>=1.0.1         # Loading .env files
tenacity>=8.2.3              # For retry logic (crucial for LLM calls)
composio-client==1.5.0
composio_core==0.7.15
composio_openai==0.7.20e = stdio_transport

            # Create the MCP Session
            session = await exit_stack.enter_async_context(ClientSession(read, write))
            
            # Initialize the protocol handshake
            await session.initialize()

            # Store session and stack for cleanup later
            self.sessions[server_name] = session
            self.exit_stacks[server_name] = exit_stack
            
            logger.info(f"Successfully connected and initialized: {server_name}")

        except Exception as e:
            logger.error(f"Failed to connect to {server_name}: {str(e)}")
            await exit_stack.aclose()
            raise e

    async def get_session(self, server_name: str) -> ClientSession:
        """Retrieve an active session by name."""
        if server_name not in self.sessions:
            raise ValueError(f"MCP Server '{server_name}' is not connected.")
        return self.sessions[server_name]

    async def cleanup(self):
        """Gracefully close all MCP connections."""
        for name, stack in self.exit_stacks.items():
            logger.info(f"Closing connection to {name}...")
            await stack.aclose()
        self.sessions.clear()
        self.exit_stacks.clear()

# Global instance to be used by the Celery Worker
mcp_manager = MCPClientManager()