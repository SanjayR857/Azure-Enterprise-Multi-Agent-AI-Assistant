from app.prompts.agent_prompts import SUPERVISOR_PROMPT

from app.services.agent_service import agent_service

def report_agent_node(state):

    research = state.get(
        "research_result",
        ""
    )

    sql_data = state.get(
        "sql_result",
        ""
    )

    prompt = f"""
Create a professional report.

Research Data:
{research}

SQL Data:
{sql_data}

Provide:
1. Summary
2. Insights
3. Recommendations
"""

    report = agent_service.run_chat(prompt)

    return {
        "final_response": report
    }