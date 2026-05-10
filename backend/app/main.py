"""ResearchForge - 科研自动化多智能体系统主入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from app.api.routes import router
from app.core.research_agent import ResearchAgent
from app.core.hypothesis_engine import HypothesisEngine
from app.core.tool_orchestrator import ToolChainOrchestrator

logger.remove()
logger.add(sys.stderr, format="<level>{time:HH:mm:ss}</level> | <level>{level}</level> | <level>{message}</level>", level="INFO")

app = FastAPI(
    title="ResearchForge",
    description="科研自动化多智能体系统 — 假设生成 + 实验设计 + 专利验证 + 流程优化",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

hypothesis_engine = HypothesisEngine()
tool_orchestrator = ToolChainOrchestrator()
research_agent = ResearchAgent(hypothesis_engine=hypothesis_engine, tool_orchestrator=tool_orchestrator)

app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "ResearchForge",
        "framework": "OpenClaw + ASF-BGT + CrewAI + AgentShield V3",
        "version": "0.1.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012, log_level="info")