from langgraph.graph import StateGraph
from langgraph.graph import START, END

from app.workflows.state import AgentState

from app.workflows.nodes.supervisor.supervisor_node import supervisor_node
from app.workflows.nodes.supervisor.supervisor_router import supervisor_router

from app.workflows.nodes.chatbot.chatbot_agent_node import chatbot_agent_node
from app.workflows.nodes.research.research_agent_node import research_agent_node
from app.workflows.nodes.sql.sql_agent_node import sql_agent_node
from app.workflows.nodes.rag.rag_agent_node import rag_agent_node

from app.workflows.nodes.report_agent_node import report_agent_node
from app.workflows.nodes.final_response_node import final_response_node
from app.workflows.nodes.analytics.analytics_agent_node import analytics_agent_node

from app.memory.conversation_memory import memory


class GraphBuilder:
    def __init__(self):
        self.graph_builder = StateGraph(AgentState)

    def builder(self):
        # Supervisor
        self.graph_builder.add_node(
            "supervisor",
            supervisor_node
        )

        # Existing Agents
        self.graph_builder.add_node(
            "chatbot_agent",
            chatbot_agent_node
        )

        self.graph_builder.add_node(
            "research_agent",
            research_agent_node
        )

        self.graph_builder.add_node(
            "sql_agent",
            sql_agent_node
        )

        self.graph_builder.add_node(
            "rag_agent",
            rag_agent_node
        )
        
        self.graph_builder.add_node(
            "analytics_agent",
            analytics_agent_node
        )

        self.graph_builder.add_node(
            "report_agent",
            report_agent_node
        )

        self.graph_builder.add_node(
            "final_response",
            final_response_node
        )   

        self.graph_builder.add_edge(
            START,
            "supervisor"
        )

        self.graph_builder.add_conditional_edges(
            "supervisor",
            supervisor_router,
            {
                "chatbot_agent": "chatbot_agent",
                "research_agent": "research_agent",
                "sql_agent": "sql_agent",
                "rag_agent": "rag_agent",
                "analytics_agent": "analytics_agent"
            }
        )

        # Standalone Chat
        self.graph_builder.add_edge(
            "chatbot_agent",
            END
        )

        # RAG Flow
        self.graph_builder.add_edge(
            "rag_agent",
            END
        )

        # SQL Direct Flow
        self.graph_builder.add_edge(
            "sql_agent",
            END
        )

      

        # Multi-Agent Flow

        self.graph_builder.add_edge(
            "analytics_agent",
            "report_agent"
        )

        self.graph_builder.add_edge(
            "research_agent",
            "sql_agent"
        )

        self.graph_builder.add_edge(
            "sql_agent",
            "report_agent"
        )

        self.graph_builder.add_edge(
            "report_agent",
            "final_response"
        )

        self.graph_builder.add_edge(
            "final_response",
            END
        )

        graph = self.graph_builder.compile()
        return graph

graph_builder = GraphBuilder()
graph = graph_builder.builder()