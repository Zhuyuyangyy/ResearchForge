"""API Routes for ResearchForge"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from app.agents.patent_miner import PatentMinerAgent

router = APIRouter(prefix="/api/v1", tags=["ResearchForge"])

# ============ Request/Response Models ============

class HypothesisRequest(BaseModel):
    """假设生成请求"""
    research_question: str = Field(..., description="研究问题或目标")
    context: Optional[str] = Field(None, description="背景上下文")
    num_hypotheses: int = Field(3, ge=1, le=10, description="生成假设数量")
    modality: str = Field("text", description="输入模态: text/image/data")


class PriorArtRequest(BaseModel):
    """Prior-art 检索请求"""
    tech_description: str = Field(..., description="技术描述")
    search_depth: str = Field("standard", description="检索深度: standard/deep")


class ResearchResponse(BaseModel):
    """通用响应"""
    status: str
    data: Dict[str, Any]
    message: str = ""


# ============ Agents ============

patent_miner = PatentMinerAgent()


# ============ Routes ============

@router.post("/research/hypothesis")
async def generate_hypothesis(req: HypothesisRequest) -> ResearchResponse:
    """
    生成科研假设
    输入研究问题 → 输出结构化假设列表 + 验证路径
    """
    from app.core.hypothesis_engine import HypothesisEngine

    engine = HypothesisEngine()
    hypotheses = engine.generate(
        research_question=req.research_question,
        context=req.context or "",
        num_hypotheses=req.num_hypotheses,
    )

    return ResearchResponse(
        status="success",
        data={
            "hypotheses": [h.__dict__ for h in hypotheses],
            "count": len(hypotheses),
            "research_question": req.research_question,
        },
        message=f"生成了 {len(hypotheses)} 个假设",
    )


@router.post("/research/priorart")
async def search_priorart(req: PriorArtRequest) -> ResearchResponse:
    """
    Prior-art 分析
    输入技术描述 → 输出专利/论文/产品三元组分析 + 可专利点
    """
    result = patent_miner.mine(
        tech_description=req.tech_description,
        search_depth=req.search_depth,
    )

    return ResearchResponse(
        status="success",
        data=result,
        message=result.get("summary", ""),
    )


@router.get("/research/patentable-points")
async def list_patentable_points(domain: Optional[str] = None) -> ResearchResponse:
    """
    列出已识别的可专利点
    可按领域过滤
    """
    # 示例数据
    points = [
        {
            "id": "PP-001",
            "category": "实验闭环",
            "description": "First to implement complete loop: hypothesis -> experiment -> verification -> refinement",
            "confidence": 0.85,
        },
        {
            "id": "PP-002",
            "category": "因果推理",
            "description": "反事实推理 + 因果图约束的假设验证",
            "confidence": 0.82,
        },
        {
            "id": "PP-003",
            "category": "KG约束",
            "description": "KG 约束的假设生成 + 一致性检查",
            "confidence": 0.78,
        },
    ]

    if domain:
        points = [p for p in points if domain.lower() in p["category"].lower()]

    return ResearchResponse(
        status="success",
        data={"points": points, "count": len(points)},
        message=f"当前共 {len(points)} 个可专利点",
    )


@router.get("/research/domains")
async def list_domains() -> ResearchResponse:
    """
    列出支持的科研领域
    """
    domains = [
        {"id": "科1", "name": "自主实验室闭环", "status": "ready", "priority": "high"},
        {"id": "科2", "name": "材料配方生成", "status": "planning", "priority": "high"},
        {"id": "科3", "name": "多模态显微谱图", "status": "planning", "priority": "medium"},
        {"id": "科4", "name": "蛋白/药物设计", "status": "planning", "priority": "medium"},
        {"id": "科5", "name": "重复性审计", "status": "planning", "priority": "low"},
    ]
    return ResearchResponse(
        status="success",
        data={"domains": domains, "count": len(domains)},
        message="5个科研领域，覆盖AI for Science核心方向",
    )
