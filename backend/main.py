from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent_core import agent_executor
from datetime import datetime
#creat fastapi instance

app= FastAPI(
    title="智能问答研究助手",
    description="An AI search assistant powered by fastapi and langchain"
)

# config with middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

# Define request model
class QueryRequest(BaseModel):
    topic:str

# Define Endpoint

@app.post("/api/research")
async def research_agent(request:QueryRequest):
    try:
        response=await agent_executor.ainvoke({
            "input":request.topic,
            "current_time":datetime.now().strftime("%Y年%m月%d日")
        })
        return {"result":response['output']}
    except Exception as e:
        return {f"Error: Agent Execution {e}"}
    
@app.get("/")
def read_root():
    return {"message":"欢迎使用智能研究助手！"}