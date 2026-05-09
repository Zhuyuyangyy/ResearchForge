"""
PatentMiner Agent — 专利挖掘智能体
从专利/论文/产品三元组中挖掘 prior-art + 识别可专利点
"""

import json
from typing import Any
from dataclasses import dataclass, field


@dataclass
class PriorArtItem:
    """Prior-art 条目"""
    type: str  # patent | paper | product
    title: str
    source: str
    date: str
    key_claims: list[str] = field(default_factory=list)
    relevance_score: float = 0.0
    gap_description: str = ""


@dataclass
class PatentablePoint:
    """可专利点"""
    id: str
    description: str
    novelty: str
    inventive_step: str
    technical_effect: str
    confidence: float = 0.0
    claim_direction: list[str] = field(default_factory=list)


class PatentMinerAgent:
    """
    专利挖掘 Agent：
    1. 接收技术描述
    2. 检索 patent/paper/product prior-art
    3. 识别技术空白点
    4. 输出可专利点 + 权利要求方向
    """

    def __init__(self, llm=None):
        self.llm = llm
        self.prior_art_db = self._load_prior_art_db()

    def _load_prior_art_db(self) -> dict:
        """加载本地 prior-art 知识库（示例数据）"""
        return {
            "patent_families": [
                {
                    "id": "CN202410001",
                    "title": "一种基于知识图谱的实验假设生成方法",
                    "date": "2024-01",
                    "applicant": "某高校",
                    "claims": ["知识图谱约束", "假设生成", "可验证性检验"],
                }
            ],
            "papers": [
                {
                    "id": "paper_ai_science_2024",
                    "title": "AI for Science: opportunities and challenges",
                    "venue": "Nature Machine Intelligence",
                    "date": "2024",
                    "key_findings": ["自主实验闭环", "主动学习", "失败模式追踪"],
                }
            ],
            "products": [
                {
                    "id": "product_gpt_science",
                    "name": "GPT-4 Science Mode",
                    "capabilities": ["文献总结", "假设建议"],
                    "limitations": ["无实验闭环", "无仿真验证"],
                }
            ],
        }

    def mine(self, tech_description: str, search_depth: str = "standard") -> dict:
        """
        执行专利挖掘

        Args:
            tech_description: 技术描述文本
            search_depth: standard | deep

        Returns:
            {
                "prior_art": [...],
                "gaps": [...],
                "patentable_points": [...],
                "claim_directions": [...]
            }
        """
        # Step 1: 构建查询
        query_terms = self._extract_terms(tech_description)

        # Step 2: prior-art 检索
        patent_results = self._search_patents(query_terms)
        paper_results = self._search_papers(query_terms)
        product_results = self._search_products(query_terms)

        # Step 3: 技术空白点分析
        gaps = self._analyze_gaps(tech_description, patent_results, paper_results, product_results)

        # Step 4: 可专利点识别
        patentable_points = self._identify_patentable_points(gaps, tech_description)

        return {
            "tech_description": tech_description,
            "prior_art": {
                "patents": patent_results,
                "papers": paper_results,
                "products": product_results,
            },
            "gaps": gaps,
            "patentable_points": patentable_points,
            "summary": self._generate_summary(patentable_points, gaps),
        }

    def _extract_terms(self, text: str) -> list[str]:
        """提取关键技术术语"""
        # 简单演示：实际用 NLP/Embedding 做
        keywords = [
            "hypothesis generation", "knowledge graph", "experiment automation",
            "active learning", "counterfactual", "multi-agent",
            "digital twin", "causal inference", "autonomous lab",
        ]
        found = [k for k in keywords if k.lower() in text.lower()]
        return found if found else ["hypothesis generation", "experiment automation"]

    def _search_patents(self, terms: list[str]) -> list[dict]:
        """检索专利"""
        results = []
        for fam in self.prior_art_db["patent_families"]:
            if any(t.lower() in fam["title"].lower() for t in terms):
                results.append(fam)
        return results

    def _search_papers(self, terms: list[str]) -> list[dict]:
        """检索论文"""
        results = []
        for paper in self.prior_art_db["papers"]:
            if any(t.lower() in paper["title"].lower() or t.lower() in " ".join(paper["key_findings"]).lower()
                    for t in terms):
                results.append(paper)
        return results

    def _search_products(self, terms: list[str]) -> list[dict]:
        """检索产品"""
        results = []
        for prod in self.prior_art_db["products"]:
            if any(t.lower() in prod["name"].lower() or t.lower() in " ".join(prod["capabilities"]).lower()
                    for t in terms):
                results.append(prod)
        return results

    def _analyze_gaps(self, tech_desc: str, patents: list, papers: list, products: list) -> list[dict]:
        """分析技术空白点"""
        gaps = []

        # 检测是否有实验闭环
        if "experiment" in tech_desc.lower() and "闭环" in tech_desc:
            has_closed_loop = any("闭环" in str(p) for p in patents + papers)
            if not has_closed_loop:
                gaps.append({
                    "gap_id": "GAP-001",
                    "category": "实验闭环",
                    "description": "Existing tech does not implement complete loop: hypothesis->experiment->verification->refinement",
                    "opportunity": "自主实验闭环 + 失败模式追踪",
                })

        # 检测是否有因果推理
        if "因果" in tech_desc or "causal" in tech_desc.lower():
            has_causal = any("causal" in str(p).lower() for p in patents + papers)
            if not has_causal:
                gaps.append({
                    "gap_id": "GAP-002",
                    "category": "因果推理",
                    "description": "现有系统缺乏因果约束的假设验证机制",
                    "opportunity": "反事实推理 + 因果图约束",
                })

        # 检测知识图谱增强
        if "知识图谱" in tech_desc or "knowledge graph" in tech_desc.lower():
            has_kg_constraint = any("知识图谱约束" in str(p) for p in patents)
            if not has_kg_constraint:
                gaps.append({
                    "gap_id": "GAP-003",
                    "category": "KG约束",
                    "description": "KG 仅用于检索，未用于假设约束过滤",
                    "opportunity": "KG 约束的假设生成 + 一致性检查",
                })

        # 检测多智能体协作
        if "多智能体" in tech_desc or "multi-agent" in tech_desc.lower():
            gaps.append({
                "gap_id": "GAP-004",
                "category": "多智能体协作",
                "description": "科研场景下多 Agent 协作的分工与治理机制尚未系统化",
                "opportunity": "科研多智能体分工 + V3 行为审计",
            })

        return gaps

    def _identify_patentable_points(self, gaps: list, tech_desc: str) -> list[PatentablePoint]:
        """识别可专利点"""
        points = []
        for i, gap in enumerate(gaps):
            pt = PatentablePoint(
                id=f"PP-{i+1:03d}",
                description=gap["description"],
                novelty=f"在科研假设生成领域，首次将{gap['category']}与{gap['opportunity']}结合",
                inventive_step=f"通过{gap['opportunity']}实现假设的{gap['category']}增强",
                technical_effect=f"提升假设可验证性和科研效率",
                confidence=0.85 if gap["category"] else 0.70,
                claim_direction=[
                    f"一种基于{gap['opportunity']}的科研假设生成方法",
                    f"一种集成{gap['category']}约束的多智能体科研系统",
                ],
            )
            points.append(pt)
        return points

    def _generate_summary(self, patentable_points: list, gaps: list) -> str:
        """生成摘要"""
        if not patentable_points:
            return "未发现明显技术空白点，建议进行更深入的 prior-art 检索"
        return (
            f"发现 {len(gaps)} 个技术空白点，"
            f"识别 {len(patentable_points)} 个可专利点，"
            f"Found {len(gaps)} tech gaps, identified {len(patentable_points)} patentable points, main innovation: {gaps[0]['category'] if gaps else 'N/A'}"
        )
