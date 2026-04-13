from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, SystemMessage

from src.agent.agent import agent

class ChatRequest(BaseModel):
    message: str
    thread_id: str = "default"

class ChatResponse(BaseModel):
    response: str

app = FastAPI(
        title="Power BI Agent API",
        description="AI-powered agent for managing Power BI dashboards (recommendation, migration, deletion, comparison)",
        version="1.0.0"
)

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    
    system_prompt = """
    You are a helpful assistant specialized in Power BI operations.
    """

    thread = {"configurable": {"thread_id": req.thread_id}}

    result = agent.invoke(
        {
            "messages": [
                SystemMessage(content=system_prompt),
                HumanMessage(content=req.message)
            ]
        },
        config=thread
    )

    return {
        "response": result["messages"][-1].content
    }

