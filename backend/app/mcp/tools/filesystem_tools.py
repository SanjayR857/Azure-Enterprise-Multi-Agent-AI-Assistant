import asyncio
from langchain.tools import tool
from app.services.mcp_service import mcp_service


def run_async(coro):
    """
    Run an async coroutine from a synchronous context (e.g. LangGraph ToolNode thread pool).
    
    Uses asyncio.run_coroutine_threadsafe() to schedule the coroutine on the MAIN
    event loop where the MCP session background tasks live, then blocks the current
    thread waiting for the result. This avoids the deadlock caused by creating a new
    event loop in the worker thread.
    """
    # The MCP session lives on the main event loop stored in mcp_service._loop.
    # Schedule the coroutine there and block this thread until it completes.
    loop = mcp_service._loop
    if loop is None:
        raise RuntimeError(
            "MCP service event loop not initialized. "
            "Ensure mcp_service.connect_all() was called during app startup."
        )
    
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=30)  # 30s timeout to prevent infinite hangs


@tool
def list_project_files(directory: str) -> str:
    """
    List all files and directories located within the specified directory.
    """
    result = run_async(
        mcp_service.exeute_tools("filesystem", "list_files", {"directory": directory})
    )
    if hasattr(result, "content"):
        return "\n".join([item.text for item in result.content if hasattr(item, "text")])
    return str(result)


@tool
def read_project_file(file_path: str) -> str:
    """
    Read the content of a file located within the specified directory.
    """
    result = run_async(
        mcp_service.exeute_tools("filesystem", "read_file", {"file_path": file_path})
    )
    if hasattr(result, "content"):
        return "\n".join([item.text for item in result.content if hasattr(item, "text")])
    return str(result)


@tool
def search_project_files(root_directory: str, keyword: str) -> str:
    """
    Search for files containing the specified keyword within the specified directory.
    """
    result = run_async(
        mcp_service.exeute_tools("filesystem", "search_files", {"root_directory": root_directory, "keyword": keyword})
    )
    if hasattr(result, "content"):
        return "\n".join([item.text for item in result.content if hasattr(item, "text")])
    return str(result)
