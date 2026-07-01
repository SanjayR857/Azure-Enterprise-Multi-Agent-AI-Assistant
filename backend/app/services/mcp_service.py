import asyncio
from app.mcp.client import MCPClient
import logging

logger = logging.getLogger(__name__)


class MCPService:

    def __init__(self):
        self.clients = {}
        self._loop = None  # Reference to the event loop where MCP sessions live

    
    def register_server(self, name: str, command: list [str]):
        """
        Register MCP server process
        """
        logger.info("Registering MCP server", extra={"server_name": name, "command": command})
        self.clients[name] = MCPClient(command)

    
    async def connect_all(self):
        """
        Connect to all registered MCP servers.
        Stores the current event loop so tools in worker threads can schedule calls on it.
        """
        logger.info("Connecting to MCP servers", extra={"server_count": len(self.clients)})
        self._loop = asyncio.get_running_loop()
        for name, client in self.clients.items():
            try:
                await client.connect()
                logger.info("Successfully connected to MCP server", extra={"server_name": name})
            except Exception as e:
                logger.error("Failed to connect to MCP server", extra={"server_name": name, "error": str(e)})
    

    async def list_all_tools(self):
        """
        Aggregate tools from all servers
        """

        all_tools = {}

        for name, client in self.clients.items():
            tools = await client.list_tools()
            all_tools[name] = tools
        
        return all_tools

    
    async def exeute_tools(self,server_name: str, tool_name:str, arguments:dict):
        """
        Execute a tool on a specific server
        """
        logger.info("Executing tool on server", extra={"tool_name": tool_name, "server_name": server_name, "arguments": arguments})
        client = self.clients.get(server_name)

        if not client:
            logger.error("Server not found when executing tool", extra={"tool_name": tool_name, "server_name": server_name})
            raise Exception(f"Server {server_name} not found")

        try:
            result = await client.call_tools(tool_name, arguments)
            logger.info("Successfully executed tool", extra={"tool_name": tool_name, "server_name": server_name})
            return result
        except Exception as e:
            logger.error("Failed to execute tool", extra={"tool_name": tool_name, "server_name": server_name, "error": str(e)})
            raise e

mcp_service = MCPService()

    
