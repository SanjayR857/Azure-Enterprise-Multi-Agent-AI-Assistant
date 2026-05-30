from langgraph.graph import StateGraph 
from langgraph.graph import START,END

from app.workflows.state import AgentState

from app.workflows.nodes.rag_agent_node import rag_agent_node
from app.workflows.nodes.supervisor_node import supervisor_node
from app.workflows.nodes.supervisor_router import supervisor_router
from app.workflows.nodes.chatbot_agent_node import chatbot_agent_node
from app.workflows.nodes.research_agent_node import research_agent_node
from app.workflows.nodes.sql_agent_node import sql_agent_node

from app.memory.conversation_memory import memory

class GraphBuilder:

    def __init__(self):

        self.graph_builder=StateGraph(AgentState)

    
    def builder(self):

        self.graph_builder.add_node("supervisor", supervisor_node)
        
        self.graph_builder.add_node("chatbot_agent",chatbot_agent_node)

        self.graph_builder.add_node("research_agent", research_agent_node)

        self.graph_builder.add_node("sql_agent", sql_agent_node)

        self.graph_builder.add_node("rag_agent", rag_agent_node)


        self.graph_builder.add_edge(START,"supervisor")

        self.graph_builder.add_conditional_edges(
            "supervisor",
            supervisor_router,
            {
                "chatbot_agent": "chatbot_agent",
                "research_agent": "research_agent",
                "sql_agent": "sql_agent",
                "rag_agent": "rag_agent"
            }
        )

        self.graph_builder.add_edge("chatbot_agent",END)

        self.graph_builder.add_edge("research_agent",END)

        self.graph_builder.add_edge("sql_agent",END)
        
        self.graph_builder.add_edge("rag_agent",END)
        
        # complier 
        graph = self.graph_builder.compile(
            checkpointer=memory
        )

        return graph

graph_builder = GraphBuilder()

graph = graph_builder.builder()


