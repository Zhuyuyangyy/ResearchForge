"""API Routes for ResearchForge"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.agents.patent_miner import PatentMinerAgent
from app.agents.material_generator import MaterialGenAgent
from app.agents.lab_automation import LabAutomationAgent
from app.services.project_ingestor import ingest_project

router = APIRouter(prefix="/api/v1", tags=["ResearchForge"])


class ProjectIngestRequest(BaseModel):
    project_path: str = Field(..., description="待摄取项目路径")


class HypothesisRequest(BaseModel):
    research_question: str = Field(..., description="研究问题或目标")
    context: Optional[str] = Field(None, description="上下文信息")
    num_hypotheses: int = Field(3, ge=1, le=10)
    modality: str = Field("text")


class PriorArtRequest(BaseModel):
    tech_description: str = Field(..., description="技术描述")
    search_depth: str = Field("standard")


class MaterialGenRequest(BaseModel):
    target_property: str = Field(..., description="目标性能（如 energy_density, thermal_stability）")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="约束条件")


class ExperimentDesignRequest(BaseModel):
    hypothesis_id: str = Field(..., description="假设ID")
    hypothesis_context: Dict[str, Any] = Field(default_factory=dict)


class ResearchResponse(BaseModel):
    status: str; data: Dict[str, Any]; message: str = ""


patent_miner = PatentMinerAgent()
material_gen = MaterialGenAgent()
lab_automation = LabAutomationAgent()



@router.post("/research/ingest_project")
async def ingest_project_endpoint(req: ProjectIngestRequest) -> ResearchResponse:
    result = ingest_project(req.project_path)
    if "error" in result:
        return ResearchResponse(status="error", data={}, message=result["error"])
    return ResearchResponse(
        status="success",
        data=result,
        message=f"项目 {req.project_path} 摄取完成，发现 {len(result.get('detected_modules', []))} 个模块",
    )

@router.post("/research/hypothesis")
async def generate_hypothesis(req: HypothesisRequest) -> ResearchResponse:
    from app.core.hypothesis_engine import HypothesisEngine
    engine = HypothesisEngine()
    hypotheses = engine.generate(
        research_question=req.research_question,
        context=req.context or "",
        num_hypotheses=req.num_hypotheses,
    )
    return ResearchResponse(
        status="success",
        data={"hypotheses": [h.__dict__ for h in hypotheses], "count": len(hypotheses), "research_question": req.research_question},
        message=f"生成了 {len(hypotheses)} 个假设",
    )


@router.post("/research/priorart")
async def search_priorart(req: PriorArtRequest) -> ResearchResponse:
    result = patent_miner.mine(tech_description=req.tech_description, search_depth=req.search_depth)
    return ResearchResponse(status="success", data=result, message=result.get("summary", ""))


@router.post("/research/material/generate")
async def generate_material(req: MaterialGenRequest) -> ResearchResponse:
    result = material_gen.generate(target_property=req.target_property, constraints=req.constraints)
    return ResearchResponse(status="success", data=result, message=f"生成了 {result['count']} 个候选材料配方")


@router.post("/research/material/optimize")
async def optimize_material(base_formula: Dict[str, float], target_improvement: str) -> ResearchResponse:
    result = material_gen.optimize(base_formula=base_formula, target_improvement=target_improvement)
    return ResearchResponse(status="success", data=result, message="配方优化完成")


@router.post("/research/experiment/design")
async def design_experiment(req: ExperimentDesignRequest) -> ResearchResponse:
    result = lab_automation.design_experiment(hypothesis_id=req.hypothesis_id, context=req.hypothesis_context)
    return ResearchResponse(status="success", data=result, message=f"实验设计完成: {result['experiment_id']}")


@router.post("/research/experiment/run")
async def run_experiment(experiment: dict) -> ResearchResponse:
    result = lab_automation.run_simulation(experiment)
    return ResearchResponse(status="success", data=result, message=f"实验模拟完成: {result['status']}")


@router.get("/research/patentable-points")
async def list_patentable_points(domain: Optional[str] = None) -> ResearchResponse:
    points = [
        {"id": "PP-001", "category": "实验闭环", "description": "Complete loop: hypothesis -> experiment -> verification -> refinement", "confidence": 0.85},
        {"id": "PP-002", "category": "因果推理", "description": "反事实推理 + 因果图谱的假设验证", "confidence": 0.82},
        {"id": "PP-003", "category": "KG约束", "description": "KG约束的假设生成 + 一致性检查", "confidence": 0.78},
    ]
    if domain: points = [p for p in points if domain.lower() in p["category"].lower()]
    return ResearchResponse(status="success", data={"points": points, "count": len(points)}, message=f"当前共 {len(points)} 个可专利点")


@router.get("/research/domains")
async def list_domains() -> ResearchResponse:
    domains = [
        {"id": "科1", "name": "自主实验室闭环", "status": "ready", "priority": "high"},
        {"id": "科2", "name": "材料配方生成", "status": "ready", "priority": "high"},
        {"id": "科3", "name": "多目标优化", "status": "planning", "priority": "medium"},
        {"id": "科4", "name": "蛋白质/药物设计", "status": "planning", "priority": "medium"},
        {"id": "科5", "name": "重复性可靠性统计", "status": "planning", "priority": "low"},
    ]
    return ResearchResponse(status="success", data={"domains": domains, "count": len(domains)}, message="5个科研领域，覆盖AI for Science核心方向")


@router.get("/health")
async def health():
    return {"status": "healthy", "service": "ResearchForge", "version": "0.1.1"}