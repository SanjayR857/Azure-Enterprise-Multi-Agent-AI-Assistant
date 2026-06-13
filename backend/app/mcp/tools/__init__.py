from app.mcp.tools.calculator_tool import calculator
from app.mcp.tools.tavily_search import web_search

from app.mcp.tools.filesystem_tools import (
    list_project_files,
    read_project_file,
    search_project_files
)

ALL_TOOLS = [
    calculator,
    web_search,
    list_project_files, 
    read_project_file,
    search_project_files
]