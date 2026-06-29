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
        logger.info(f"Registering MCP server: {name} with command: {command}")
        self.clients[name] = MCPClient(command)

    
    async def connect_all(self):
        """
        Connect to all registered MCP servers.
        Stores the current event loop so tools in worker threads can schedule calls on it.
        """
        logger.info(f"Connecting to all {len(self.clients)} MCP servers")
        self._loop = asyncio.get_running_loop()
        for name, client in self.clients.items():
            try:
                await client.connect()
                logger.info(f"Successfully connected to MCP server: {name}")
            except Exception as e:
                logger.error(f"Failed to connect to MCP server {name}: {e}")
    

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
        logger.info(f"Executing tool {tool_name} on server {server_name} with args: {arguments}")
        client = self.clients.get(server_name)

        if not client:
            logger.error(f"Server {server_name} not found when executing tool {tool_name}")
            raise Exception(f"Server {server_name} not found")

        try:
            result = await client.call_tools(tool_name, arguments)
            logger.info(f"Successfully executed tool {tool_name} on {server_name}")
            return result
        except Exception as e:
            logger.error(f"Failed to execute tool {tool_name} on {server_name}: {e}")
            raise e

mcp_service = MCPService()

    
