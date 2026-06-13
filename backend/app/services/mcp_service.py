import asyncio
from app.mcp.client import MCPClient


class MCPService:

    def __init__(self):
        self.clients = {}
        self._loop = None  # Reference to the event loop where MCP sessions live

    
    def register_server(self, name: str, command: list [str]):
        """
        Register MCP server process
        """
        self.clients[name] = MCPClient(command)

    
    async def connect_all(self):
        """
        Connect to all registered MCP servers.
        Stores the current event loop so tools in worker threads can schedule calls on it.
        """
        self._loop = asyncio.get_running_loop()
        for client in self.clients.values():
            await client.connect()
    

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
        client = self.clients.get(server_name)

        if not client:
            raise Exception(f"Server {server_name} not found")

        return await client.call_tools(tool_name, arguments)

mcp_service = MCPService()

    
