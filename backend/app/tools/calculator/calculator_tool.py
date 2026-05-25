from langchain.tools import tool 


@tool
def calculator(expression: str) -> str:
    """
    Evaluate a mathematical expression.
    Use this tool whenever the user asks a question involving mathematical calculations, arithmetic,
    or needs to compute numerical equations (e.g. addition, subtraction, multiplication, division, powers).
    
    Args:
        expression (str): A valid Python mathematical expression to evaluate (e.g. "342 * 94 + 102").
        
    Returns:
        str: The numeric result as a string, or an error message if the expression is invalid.
    """

    try:
        result = eval(expression)
        
        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"