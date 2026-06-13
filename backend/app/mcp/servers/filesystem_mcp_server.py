import sys
import os
# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from mcp.server.fastmcp import FastMCP
from app.mcp.servers.filesystem_server import FilesystemServer

mcp = FastMCP("filesystem")
fs_server = FilesystemServer()

@mcp.tool()
def list_files(directory: str) -> list[str]:
    """
    List all files and directories located within the specified directory.
    """
    return fs_server.list_files(directory)

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Read the content of a file located within the specified directory.
    """
    return fs_server.read_text(file_path) if hasattr(fs_server, "read_text") else fs_server.read_file(file_path)

@mcp.tool()
def search_files(root_directory: str, keyword: str) -> list[str]:
    """
    Search for files containing the specified keyword within the specified directory.
    """
    return fs_server.search_files(root_directory, keyword)

if __name__ == "__main__":
    mcp.run()
