# REPRODUCE.md - ResearchForge

## Prerequisites

- **Python**: 3.10+
- **OS**: Linux / macOS / Windows
- **GPU**: Not required

## Install

```bash
cd ResearchForge
pip install -r requirements.txt
```

Dependencies: fastapi, uvicorn, pydantic, loguru, numpy, langchain, langchain-core, crewai, httpx, python-dotenv

## Run Server

```bash
cd backend
python main.py  # (entry point not at root)
```

## Expected Outputs

- Closed-loop research automation: read literature -> hypothesis -> experiment design -> simulation -> iteration
- Multi-agent system (CrewAI-based)
- Ablation study and benchmark suite in `backend/experiments/`

## Known Issues

- No test suite at root level
- crewai has complex dependency chain
- Experiment scripts contain hardcoded paths
- Requires LLM API access (langchain-based)
- python-dotenv suggests .env file needed for API keys
