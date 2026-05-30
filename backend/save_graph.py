# save_graph.py
import sys
import os

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.workflows.graph_builder import graph

def save_mermaid():
    try:
        # Get the mermaid representation
        mermaid_code = graph.get_graph().draw_mermaid()
        print("Mermaid graph generated successfully!")
        
        # Save mermaid code to file
        output_path = os.path.join(os.path.dirname(__file__), "workflow_graph.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# LangGraph Workflow Architecture\n\n")
            f.write("Below is the visual graph structure of the Enterprise Multi-Agent AI Assistant:\n\n")
            f.write("```mermaid\n")
            f.write(mermaid_code)
            f.write("\n```\n")
        print(f"Graph saved as markdown with Mermaid rendering to: {output_path}")
        
    except Exception as e:
        print(f"Error generating graph representation: {e}")

if __name__ == "__main__":
    save_mermaid()
