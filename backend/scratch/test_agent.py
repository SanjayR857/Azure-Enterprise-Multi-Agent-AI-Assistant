import os
import sys
from dotenv import load_dotenv

# Resolve paths
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)
load_dotenv(os.path.join(backend_dir, ".env"))

from langchain_ollama import ChatOllama
from app.prompts.system_prompts import AGENT_SYSTEM_PROMPT
from app.tools.calculator.calculator_tool import calculator
from app.tools.web_search.tavily_search import web_search
from langchain.agents import create_agent

def test_model_with_agent(model_name: str):
    print(f"\n=================== TESTING MODEL: {model_name} ===================")
    try:
        model = ChatOllama(model=model_name, temperature=0)
        tools = [calculator, web_search]
        
        agent = create_agent(
            tools=tools,
            model=model,
            system_prompt=AGENT_SYSTEM_PROMPT
        )
        
        # Test case designed to force a math tool invocation
        prompt = "What is 342 * 94 plus 102? Please use the calculator tool."
        print(f"Prompt: {prompt}")
        print("Invoking agent...")
        
        response = agent.invoke({"messages": [{"role": "user", "content": prompt}]})
        
        print("\nMessages in execution history:")
        for idx, msg in enumerate(response.get("messages", [])):
            role = "AI" if msg.__class__.__name__ == "AIMessage" else "User" if msg.__class__.__name__ == "HumanMessage" else msg.__class__.__name__
            content_preview = msg.content if len(msg.content) < 150 else msg.content[:150] + "..."
            print(f"  {idx}. [{role}] -> {content_preview}")
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"      [TOOL CALLS DETECTED] -> {msg.tool_calls}")
                
    except Exception as e:
        print(f"Error testing model {model_name}: {str(e)}")

if __name__ == "__main__":
    # Test current configuration model
    current_model = os.getenv("OLLAMA_MODEL", "gemma4:31b-cloud")
    test_model_with_agent(current_model)
    
    # Test a model known to have native tool calling support in standard Ollama
    test_model_with_agent("mistral:latest")
