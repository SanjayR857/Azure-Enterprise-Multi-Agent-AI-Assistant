from langgraph.graph import StateGraph 
from langgraph.graph import START,END

from app.workflows.state import AgentState

from app.workflows.nodes.chatbot_node import chatbot_node
from app.workflows.nodes.rag_node import rag_node
from app.workflows.nodes.tool_node import tool_node
from app.workflows.nodes.router_node import router_node

from app.workflows.nodes.route_decision import route_decision

class GraphBuilder:

    def __init__(self):

        self.graph_builder=StateGraph(AgentState)

    
    def builder(self):

        self.graph_builder.add_node("router", router_node)

        self.graph_builder.add_node("chatbot",chatbot_node)

        self.graph_builder.add_node("tool", tool_node)

        self.graph_builder.add_node("rag", rag_node)

        self.graph_builder.add_edge(START,"router")

        self.graph_builder.add_conditional_edges(
            "router",
            route_decision,
            {
                "chatbot": "chatbot",
                "tool": "tool",
                "rag": "rag"
            }
        )

        self.graph_builder.add_edge("chatbot",END)

        self.graph_builder.add_edge("tool",END)

        self.graph_builder.add_edge("rag",END)
        
        # complier 
        graph = self.graph_builder.compile()

        return graph

graph_builder = GraphBuilder()

graph = graph_builder.builder()


