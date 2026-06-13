from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient: 


    def __init__(self, command: list[str]):
        """
        Initializes the MCP client for the given command
        """
        self.command = command
        self.session = None 
        self._exit_stack = None

    
    async def connect(self):
        """
        Connects to the MCP server
        """
        self._exit_stack = AsyncExitStack()
        
        server_params = StdioServerParameters(
            command=self.command[0],
            args=self.command[1:]
        )
        
        # Enter stdio client context
        read, write = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        
        # Enter client session context
        self.session = await self._exit_stack.enter_async_context(
            ClientSession(read, write)
        )
        
        await self.session.initialize()

    
    async def list_tools(self):
        """
        Lists all available tools from the MCP server
        """
        if not self.session:
            raise Exception("Client is not connected")
        return await self.session.list_tools()


    async def call_tools(self, name: str, arguments: dict):
        """
        Invokes a tool on the MCP server
        """
        if not self.session:
            raise Exception("Client is not connected")
        return await self.session.call_tool(name=name, arguments=arguments)

    
    async def disconnect(self):
        """
        Closes the session and disconnects from the server
        """
        if self._exit_stack:
            await self._exit_stack.aclose()
            self._exit_stack = None
            self.session = None