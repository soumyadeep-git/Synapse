from typing import List, Dict, Any
from app.mcp_core.client_manager import mcp_manager
import logging

logger = logging.getLogger(__name__)

class ToolAggregator:
    """
    Composes tools from multiple MCP servers into a single unified toolkit.
    This allows the LLM to use Jira and Slack in the same thought process.
    """

    @staticmethod
    async def get_all_tools() -> List[Dict[str, Any]]:
        """
        Fetches tools from all connected MCP sessions and namespaces them.
        """
        unified_tools = []

        for server_name, session in mcp_manager.sessions.items():
            try:
                # Fetch available tools from the specific MCP server
                response = await session.list_tools()
                
                for tool in response.tools:
                    # Rename tool to include server name (e.g., "jira_create_ticket")
                    # This prevents namespace collisions if two servers have a "search" tool
                    namespaced_name = f"{server_name}_{tool.name}"
                    
                    unified_tools.append({
                        "name": namespaced_name,
                        "description": tool.description,
                        "input_schema": tool.inputSchema,
                        "original_name": tool.name, # Keep original name for execution
                        "server": server_name
                    })
            except Exception as e:
                logger.error(f"Error fetching tools from {server_name}: {str(e)}")

        return unified_tools

    @staticmethod
    async def execute_tool(namespaced_tool_name: str, arguments: dict) -> str:
        """
        Routes the tool execution request to the correct MCP server.
        """
        # Parse the server name and the original tool name
        # Example: "jira_create_ticket" -> server="jira", tool="create_ticket"
        parts = namespaced_tool_name.split("_", 1)
        if len(parts) != 2:
            raise ValueError(f"Invalid tool name format: {namespaced_tool_name}")

        server_name, original_tool_name = parts[0], parts[1]

        # Get the correct session
        session = await mcp_manager.get_session(server_name)

        # Execute the tool on the external server
        logger.info(f"Executing tool {original_tool_name} on {server_name}...")
        result = await session.call_tool(original_tool_name, arguments)

        # MCP returns a list of contents (text, images, etc.)
        # For simplicity, we extract the text.
        output_text = "\n".join([item.text for item in result.content if item.type == "text"])
        return output_text