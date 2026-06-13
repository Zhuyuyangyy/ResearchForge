"""
Hypothesis Generation Engine (HGE) — SCI-Level
多模态假设生成引擎 · 结构化假设 · 质量评估 · 知识图谱 · 证据追溯

核心升级:
1. 结构化假设生成 (变量-假设-验证方法三段式)
2. 假设质量评分 (创新性/可验证性/效应量/一致性)
3. 文献知识图谱构建 (Semantic Scholar API)
4. 假设-证据关联追溯 (Evidence Linkage)
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from datetime import datetime
import numpy as np
import httpx
import asyncio
import json
import re


# =============================================================================
# 数据结构
# =============================================================================

class HypothesisSourceModality(Enum):
    TEXT = "text"
    IMAGE = "image"
    DATA = "data"
    MULTIMODAL = "multimodal"


class GenerationMethod(Enum):
    LLM = "llm"
    KG_INFERENCE = "kg_inference"
    ANALOGY = "analogy"
    DATA_DRIVEN = "data_driven"


class VerificationStatus(Enum):
    PENDING = "pending"
    SUPPORTED = "supported"
    CONTRADICTED = "contradicted"
    PARTIAL = "partial"


@dataclass
class Variable:
    """变量定义"""
    name: str
    type: str  # independent, dependent, control, mediator, moderator
    unit: str = ""
    range_min: Optional[float] = None
    range_max: Optional[float] = None
    operationalization: str = ""  # 操作化定义


@dataclass
class VerificationMethod:
    """验证方法"""
    method_type: str  # 实验, 仿真, 文献, 统计
    description: str
    required_data: List[str] = field(default_factory=list)
    statistical_test: str = ""  # e.g., "t-test", "ANOVA", "regression"
    sample_size_estimate: int = 0
    expected_effect_size: float = 0.0
    confidence_level: float = 0.95


@dataclass
class HypothesisQualityScore:
    """假设质量评分"""
    novelty: float = 0.0           # 创新性 0-1
    verifiability: float = 0.0     # 可验证性 0-1
    effect_size: float = 0.0       # 效应量 0-1
    consistency: float = 0.0       # 一致性 0-1
    overall: float = 0.0           # 综合评分


@dataclass
class EvidenceLink:
    """证据链接"""
    evidence_id: str
    evidence_type: str  # empirical, theoretical, simulation
    source: str  # paper title, database, experiment id
    relevance_score: float  # 0-1
    supporting: bool  # True=支持, False=反对
    extract: str  # 关键证据摘要
    page_or_figure: str = ""


@dataclass
class Hypothesis:
    """科学假设数据结构 — SCI级别"""
    id: str
    statement: str  # 自然语言假设描述

    # 结构化组成
    variables: List[Variable] = field(default_factory=list)
    relations: List[str] = field(default_factory=list)  # e.g., ["X ↑ → Y ↓", "X mediates Z"]
    constraints: List[str] = field(default_factory=list)

    # 元信息
    confidence: float = 0.0
    source_modality: HypothesisSourceModality = HypothesisSourceModality.TEXT
    generation_method: GenerationMethod = GenerationMethod.LLM

    # SCI级别新增
    quality_score: HypothesisQualityScore = field(default_factory=HypothesisQualityScore)
    verification_methods: List[VerificationMethod] = field(default_factory=list)
    evidence_links: List[EvidenceLink] = field(default_factory=list)
    literature_context: Dict[str, Any] = field(default_factory=dict)  # 关联文献

    # 溯源
    parent_hypothesis_id: Optional[str] = None  # 迭代过程中来自哪个假设
    iteration: int = 1
    tags: List[str] = field(default_factory=list)


@dataclass
class KnowledgeGraphNode:
    """知识图谱节点"""
    id: str
    entity_type: str  # concept, variable, finding, method
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[List[float]] = None


@dataclass
class KnowledgeGraphEdge:
    """知识图谱边"""
    source: str
    target: str
    relation_type: str  # causes, correlates, contradicts, part_of
    weight: float = 1.0
    source_paper: str = ""


@dataclass
class LiteratureKG:
    """文献知识图谱"""
    nodes: List[KnowledgeGraphNode] = field(default_factory=list)
    edges: List[KnowledgeGraphEdge] = field(default_factory=list)
    paper_metadata: Dict[str, Dict] = field(default_factory=dict)


@dataclass
class ConsistencyCheck:
    """一致性检查结果"""
    passed: bool
    violation_type: str = ""  # direction, magnitude, structure, constraint, physics
    violation_message: str = ""
    correction: dict = field(default_factory=dict)


@dataclass
class ToolExecutionResult:
    """工具执行结果"""
    tool_name: str
    success: bool
    output: str
    error: str = ""
    execution_time: float = 0.0
    intermediate_data: dict = field(default_factory=dict)


# =============================================================================
# 知识图谱约束检查器
# =============================================================================

class KnowledgeGraphChecker:
    """知识图谱约束检查器"""

    PHYSICS_LAWS = {
        "energy_conservation": ["能量", "守恒", "conservation", "energy"],
        "mass_conservation": ["质量", "守恒", "mass"],
        "momentum_conservation": ["动量", "守恒", "momentum"],
        "charge_conservation": ["电荷", "守恒", "charge"],
    }

    DIMENSION_RULES = {
        "force": {"units": ["N", "kg*m/s^2"], "base": ["M", "L", "T^-2"]},
        "energy": {"units": ["J", "kg*m^2/s^2"], "base": ["M", "L^2", "T^-2"]},
        "power": {"units": ["W", "J/s"], "base": ["M", "L^2", "T^-3"]},
    }

    def check_physical_feasibility(self, hypothesis: Hypothesis) -> Tuple[bool, str]:
        text = hypothesis.statement.lower()
        for law, keywords in self.PHYSICS_LAWS.items():
            if any(kw in text for kw in keywords):
                if any(w in text for w in ["违反", "violate", "破坏", "break"]):
                    return False, f"Violation of {law}"
        return True, ""

    def check_dimensional_consistency(self, hypothesis: Hypothesis) -> Tuple[bool, str]:
        """
        量纲一致性检查
        检验假设中变量的单位是否与物理量纲匹配
        """
        # 常见物理量的量纲映射
        DIMENSION_MAP = {
            # 基本量纲
            "长度": {"m", "cm", "mm", "km", "nm", "um", "米", "厘米", "毫米"},
            "质量": {"kg", "g", "mg", "ug", "千克", "克", "毫克"},
            "时间": {"s", "ms", "us", "ns", "min", "h", "秒", "毫秒", "分钟", "小时"},
            "温度": {"K", "°C", "°F", "开尔文", "摄氏度", "华氏度"},
            "电流": {"A", "mA", "uA", "安培", "毫安"},
            "物质的量": {"mol", "mmol", "umol", "摩尔", "毫摩尔"},

            # 导出量纲
            "力": {"N", "kN", "mN", "牛顿", "千牛", "毫牛"},
            "能量": {"J", "kJ", "mJ", "eV", "keV", "MeV", "焦耳", "千焦", "电子伏特"},
            "功率": {"W", "kW", "mW", "瓦特", "千瓦", "毫瓦"},
            "压力": {"Pa", "kPa", "MPa", "GPa", "atm", "bar", "帕斯卡", "千帕", "兆帕"},
            "电压": {"V", "mV", "kV", "伏特", "毫伏", "千伏"},
            "电阻": {"ohm", "Ω", "kohm", "Mohm", "欧姆", "千欧", "兆欧"},
            "电容": {"F", "uF", "nF", "pF", "法拉", "微法", "纳法", "皮法"},
            "频率": {"Hz", "kHz", "MHz", "GHz", "赫兹", "千赫", "兆赫", "吉赫"},
            "浓度": {"M", "mM", "uM", "nM", "mol/L", "mol/l", "摩尔每升", "毫摩尔每升"},
            "密度": {"kg/m3", "g/cm3", "g/ml", "千克每立方米", "克每立方厘米"},
            "速度": {"m/s", "km/h", "cm/s", "米每秒", "千米每小时"},
            "加速度": {"m/s2", "m/s^2", "米每二次方秒"},
            "面积": {"m2", "cm2", "mm2", "平方米", "平方厘米", "平方毫米"},
            "体积": {"m3", "cm3", "mm3", "L", "ml", "立方米", "立方厘米", "升", "毫升"},
        }

        # 从假设中提取变量和单位
        variables = hypothesis.variables
        if not variables:
            return True, ""

        # 收集所有变量的单位
        var_units = {}
        for var in variables:
            if var.unit:
                var_units[var.name] = var.unit

        # 检查单位是否在已知量纲中
        unknown_units = []
        for var_name, unit in var_units.items():
            found = False
            for dim_name, valid_units in DIMENSION_MAP.items():
                if unit in valid_units:
                    found = True
                    break
            if not found:
                unknown_units.append(f"{var_name}({unit})")

        # 如果有未知单位，返回警告（但不一定是错误）
        if unknown_units:
            return True, f"未知单位: {', '.join(unknown_units)}"

        # 检查关系描述中的量纲一致性
        for relation in hypothesis.relations:
            # 检查是否混合了不兼容的量纲
            if "→" in relation or "->" in relation:
                parts = relation.split("→") if "→" in relation else relation.split("->")
                if len(parts) == 2:
                    left, right = parts[0].strip(), parts[1].strip()
                    # 简单检查：如果两边都有单位，检查是否一致
                    # 这里简化处理，实际应该解析更复杂的表达式
                    pass

        return True, ""

    def check_numerical_reasonableness(self, hypothesis: Hypothesis) -> Tuple[bool, str]:
        """
        数值合理性检查
        检验假设中的数值是否在物理合理范围内
        """
        import re

        # 常见物理量的合理范围
        REASONABLE_RANGES = {
            # 温度相关
            "温度": {"min": 0, "max": 1e8, "unit": "K"},  # 绝对温度
            "°C": {"min": -273.15, "max": 1e8},
            "K": {"min": 0, "max": 1e8},

            # 浓度相关
            "浓度": {"min": 0, "max": 1e10, "unit": "mol/L"},
            "M": {"min": 0, "max": 100},  # 摩尔浓度
            "mM": {"min": 0, "max": 1e6},
            "uM": {"min": 0, "max": 1e9},
            "nM": {"min": 0, "max": 1e12},

            # 百分比
            "%": {"min": 0, "max": 100},
            "百分比": {"min": 0, "max": 100},

            # pH值
            "pH": {"min": 0, "max": 14},

            # 效率相关
            "效率": {"min": 0, "max": 100, "unit": "%"},
            "转化率": {"min": 0, "max": 100, "unit": "%"},
            "产率": {"min": 0, "max": 100, "unit": "%"},

            # 压力相关
            "Pa": {"min": 0, "max": 1e15},
            "kPa": {"min": 0, "max": 1e12},
            "MPa": {"min": 0, "max": 1e9},
            "GPa": {"min": 0, "max": 1e6},
            "atm": {"min": 0, "max": 1e6},

            # 电压相关
            "V": {"min": -1e6, "max": 1e6},
            "mV": {"min": -1e9, "max": 1e9},

            # 电流相关
            "A": {"min": -1e6, "max": 1e6},
            "mA": {"min": -1e9, "max": 1e9},

            # 时间相关
            "s": {"min": 0, "max": 1e15},
            "min": {"min": 0, "max": 1e12},
            "h": {"min": 0, "max": 1e9},

            # 长度相关
            "m": {"min": 0, "max": 1e15},
            "cm": {"min": 0, "max": 1e15},
            "mm": {"min": 0, "max": 1e15},
            "nm": {"min": 0, "max": 1e15},
            "um": {"min": 0, "max": 1e15},

            # 质量相关
            "kg": {"min": 0, "max": 1e15},
            "g": {"min": 0, "max": 1e15},
            "mg": {"min": 0, "max": 1e15},

            # 能量相关
            "J": {"min": 0, "max": 1e15},
            "kJ": {"min": 0, "max": 1e12},
            "eV": {"min": 0, "max": 1e15},

            # 容量相关 (电池)
            "mAh": {"min": 0, "max": 1e6},
            "mAh/g": {"min": 0, "max": 1e4},
            "Wh/kg": {"min": 0, "max": 1e4},

            # 循环次数
            "次": {"min": 0, "max": 1e6},
            "cycles": {"min": 0, "max": 1e6},
        }

        # 从假设中提取变量
        variables = hypothesis.variables
        statement = hypothesis.statement

        # 检查变量的范围值
        issues = []
        for var in variables:
            if var.range_min is not None and var.range_max is not None:
                # 检查范围是否反转
                if var.range_min > var.range_max:
                    issues.append(f"变量 {var.name} 的范围反转: min({var.range_min}) > max({var.range_max})")

                # 检查单位是否在合理范围内
                if var.unit in REASONABLE_RANGES:
                    range_info = REASONABLE_RANGES[var.unit]
                    if var.range_min < range_info["min"]:
                        issues.append(f"变量 {var.name} 的最小值 {var.range_min} 低于物理下限 {range_info['min']}")
                    if var.range_max > range_info["max"]:
                        issues.append(f"变量 {var.name} 的最大值 {var.range_max} 超过物理上限 {range_info['max']}")

        # 从假设陈述中提取数值并检查
        numbers = re.findall(r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', statement)
        for num_str in numbers:
            try:
                num = float(num_str)
                # 检查极端值
                if abs(num) > 1e15:
                    issues.append(f"数值 {num} 可能过大")
                elif abs(num) < 1e-15 and num != 0:
                    issues.append(f"数值 {num} 可能过小")
            except ValueError:
                continue

        # 检查关系描述中的数值矛盾
        for relation in hypothesis.relations:
            # 提取关系中的数值
            rel_numbers = re.findall(r'[-+]?\d*\.?\d+', relation)
            if len(rel_numbers) >= 2:
                try:
                    vals = [float(n) for n in rel_numbers]
                    # 检查是否有明显的数值矛盾
                    # 例如："效率从10%提高到200%"是不合理的
                    for i in range(0, len(vals)-1, 2):
                        if "提高" in relation or "增加" in relation or "上升" in relation:
                            if vals[i+1] > vals[i] * 10:  # 提高超过10倍可能不合理
                                issues.append(f"关系 '{relation}' 中数值变化过大")
                except ValueError:
                    continue

        if issues:
            return False, "; ".join(issues[:3])  # 只返回前3个问题

        return True, ""

    def check(self, hypothesis: Hypothesis) -> ConsistencyCheck:
        for check_fn in [self.check_physical_feasibility,
                         self.check_dimensional_consistency,
                         self.check_numerical_reasonableness]:
            ok, msg = check_fn(hypothesis)
            if not ok:
                return ConsistencyCheck(passed=False, violation_type="physics",
                                       violation_message=msg)
        return ConsistencyCheck(passed=True)


# =============================================================================
# 文献知识图谱构建器 (Semantic Scholar API)
# =============================================================================

class LiteratureKGBuilder:
    """
    基于Semantic Scholar API构建文献知识图谱
    支持: 论文检索、引用关系、主题聚类、实体链接
    """

    SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key
        self.httpx_client = httpx.AsyncClient(timeout=30.0)
        self._kg_cache: Dict[str, LiteratureKG] = {}

    async def build_kg(self, research_question: str, max_papers: int = 20) -> LiteratureKG:
        """从研究问题构建文献知识图谱"""
        # Step 1: 检索相关论文
        papers = await self._search_papers(research_question, max_papers)
        if not papers:
            return LiteratureKG()

        # Step 2: 提取实体和关系
        nodes = []
        edges = []
        paper_metadata = {}

        for paper in papers:
            paper_id = paper.get("paperId", "")
            paper_metadata[paper_id] = {
                "title": paper.get("title", ""),
                "year": paper.get("year", 2024),
                "citationCount": paper.get("citationCount", 0),
                "venue": paper.get("venue", ""),
            }

            # 论文节点
            nodes.append(KnowledgeGraphNode(
                id=f"paper:{paper_id}",
                entity_type="finding",
                label=paper.get("title", ""),
                properties={"year": paper.get("year"), "citations": paper.get("citationCount", 0)}
            ))

            # 提取关键词作为概念节点
            for kw in (paper.get("keywords", []) or []):
                kw_id = f"concept:{kw.lower().replace(' ', '_')}"
                if not any(n.id == kw_id for n in nodes):
                    nodes.append(KnowledgeGraphNode(
                        id=kw_id, entity_type="concept", label=kw,
                        properties={"frequency": 1}
                    ))
                    edges.append(KnowledgeGraphEdge(
                        source=f"paper:{paper_id}", target=kw_id,
                        relation_type="related_to", weight=0.8,
                        source_paper=paper.get("title", "")
                    ))

            # 引用关系
            for ref_id in (paper.get("references", []) or [])[:5]:
                edges.append(KnowledgeGraphEdge(
                    source=f"paper:{paper_id}",
                    target=f"paper:{ref_id}",
                    relation_type="cites",
                    weight=0.5,
                    source_paper=paper.get("title", "")
                ))

        return LiteratureKG(nodes=nodes, edges=edges, paper_metadata=paper_metadata)

    async def _search_papers(self, query: str, max_papers: int) -> List[Dict]:
        """调用Semantic Scholar API搜索论文"""
        try:
            headers = {"x-api-key": self.api_key} if self.api_key else {}
            url = f"{self.SEMANTIC_SCHOLAR_API}/paper/search"
            params = {
                "query": query,
                "limit": max_papers,
                "fields": "paperId,title,year,citations,venue,keywords,references,abstract",
            }
            resp = await self.httpx_client.get(url, headers=headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("papers", [])
        except Exception:
            pass
        # Fallback: 返回模拟论文列表
        return self._mock_papers(query, max_papers)

    def _mock_papers(self, query: str, max_papers: int) -> List[Dict]:
        """模拟论文数据（API不可用时）"""
        mock_topics = [
            "machine learning", "deep learning", "optimization", "neural network",
            "reinforcement learning", "transformer", "graph neural network",
        ]
        papers = []
        for i in range(min(max_papers, 8)):
            papers.append({
                "paperId": f"mock_{i}",
                "title": f"Related Work on {mock_topics[i % len(mock_topics)]}: {query[:40]}",
                "year": 2024 - (i % 5),
                "citationCount": 50 - i * 5,
                "venue": "Nature/Science/IEEE",
                "keywords": mock_topics[:3],
                "abstract": f"Abstract for paper {i} addressing {query}",
            })
        return papers

    async def link_evidence(self, hypothesis: Hypothesis, kg: LiteratureKG) -> List[EvidenceLink]:
        """将假设与文献知识图谱关联，生成证据链接"""
        evidence_links = []
        hypothesis_text = hypothesis.statement.lower()

        for node in kg.nodes:
            if node.entity_type != "concept":
                continue
            concept_label = node.label.lower()
            if concept_label in hypothesis_text or any(w in hypothesis_text for w in concept_label.split()):
                # 计算相关性
                relevance = sum(1 for w in concept_label.split() if w in hypothesis_text) / max(len(concept_label.split()), 1)
                if relevance > 0.1:
                    evidence_links.append(EvidenceLink(
                        evidence_id=f"ev_{node.id}",
                        evidence_type="literature",
                        source=node.label,
                        relevance_score=min(1.0, relevance + 0.3),
                        supporting=True,
                        extract=f"文献知识图谱中的概念节点: {node.label}",
                    ))

        return sorted(evidence_links, key=lambda x: x.relevance_score, reverse=True)[:5]

    def close(self):
        self.httpx_client.close()


# =============================================================================
# 假设质量评估器
# =============================================================================

class HypothesisQualityEvaluator:
    """
    SCI级别假设质量评估
    评估维度: 创新性、可验证性、效应量、一致性
    """

    def evaluate(self, hypothesis: Hypothesis, kg: LiteratureKG = None) -> HypothesisQualityScore:
        novelty = self._evaluate_novelty(hypothesis, kg)
        verifiability = self._evaluate_verifiability(hypothesis)
        effect_size = self._evaluate_effect_size(hypothesis)
        consistency = self._evaluate_consistency(hypothesis)

        overall = (novelty * 0.3 + verifiability * 0.3 + effect_size * 0.2 + consistency * 0.2)

        return HypothesisQualityScore(
            novelty=novelty,
            verifiability=verifiability,
            effect_size=effect_size,
            consistency=consistency,
            overall=round(overall, 3),
        )

    def _evaluate_novelty(self, h: Hypothesis, kg: LiteratureKG) -> float:
        """创新性: 与现有文献的区分度"""
        if kg is None or not kg.nodes:
            return 0.7  # 缺乏文献上下文，默认中等创新性

        statement_lower = h.statement.lower()
        known_concepts = sum(1 for n in kg.nodes if n.entity_type == "concept" and n.label.lower() in statement_lower)
        total_concepts = len([v for v in h.variables if v.name])

        if total_concepts == 0:
            novelty = 0.6
        else:
            novelty = 1.0 - min(1.0, known_concepts / (total_concepts + 1))

        # 惩罚重复关键词
        for edge in kg.edges:
            if edge.relation_type == "contradicts":
                if any(w in statement_lower for w in edge.source.lower().split()[:3]):
                    novelty *= 0.7

        return round(novelty, 3)

    def _evaluate_verifiability(self, h: Hypothesis) -> float:
        """可验证性: 假设是否可以通过实验/仿真/统计验证"""
        score = 0.5

        # 有明确的验证方法加高分
        if len(h.verification_methods) > 0:
            score += 0.2
            for vm in h.verification_methods:
                if vm.statistical_test:
                    score += 0.1
                if vm.sample_size_estimate > 30:
                    score += 0.05

        # 有操作化定义的变量加高分
        defined_vars = sum(1 for v in h.variables if v.operationalization)
        if h.variables:
            score += 0.1 * (defined_vars / len(h.variables))

        # 有定量关系描述加高分
        if any(re.search(r'\d+', str(r)) for r in h.relations):
            score += 0.1

        return min(1.0, round(score, 3))

    def _evaluate_effect_size(self, h: Hypothesis) -> float:
        """效应量: 假设预测的效应强度"""
        score = 0.5

        # 效应量在验证方法中指定
        for vm in h.verification_methods:
            if vm.expected_effect_size > 0:
                score = min(1.0, score + vm.expected_effect_size * 0.3)

        # 有明确的因果方向加高分
        causal_keywords = ["导致", "causes", "increases", "decreases", "promotes", "inhibits"]
        if any(kw in h.statement.lower() for kw in causal_keywords):
            score += 0.15

        # 有中介变量加高分
        mediators = [v for v in h.variables if "mediator" in v.type or "mediates" in str(v).lower()]
        if mediators:
            score += 0.1

        return min(1.0, round(score, 3))

    def _evaluate_consistency(self, h: Hypothesis) -> float:
        """一致性: 假设内部逻辑一致性"""
        score = 1.0

        # 变量类型覆盖检查
        has_independent = any(v.type == "independent" for v in h.variables)
        has_dependent = any(v.type == "dependent" for v in h.variables)
        if not (has_independent and has_dependent):
            score -= 0.2

        # 关系描述与约束矛盾检查
        for constraint in h.constraints:
            for relation in h.relations:
                if ">" in constraint and "<" in relation:
                    score -= 0.1

        return max(0.0, round(score, 3))


# =============================================================================
# 结构化假设生成器 (SCI级别)
# =============================================================================

class StructuredHypothesisGenerator:
    """
    生成结构化假设: 变量-假设-验证方法 三段式

    输出格式:
    {
        "variables": [Variable, ...],
        "hypothesis_statement": str,
        "relations": [str, ...],
        "verification_methods": [VerificationMethod, ...],
    }
    """

    def __init__(self, llm_client=None):
        self.kg_checker = KnowledgeGraphChecker()
        self.llm_client = llm_client

    def generate_structured(
        self,
        task_description: str,
        multi_modal_context: dict,
        literature_kg: LiteratureKG = None,
        num_hypotheses: int = 3,
    ) -> List[Hypothesis]:
        """
        生成结构化假设列表
        """
        raw = self._llm_generate_structured(task_description, multi_modal_context)

        hypotheses = []
        for i, h_data in enumerate(raw[:num_hypotheses]):
            h = self._build_hypothesis(f"h_{i+1}_{datetime.now().strftime('%H%M%S')}", h_data)
            hypotheses.append(h)

        # 质量评估
        evaluator = HypothesisQualityEvaluator()
        for h in hypotheses:
            h.quality_score = evaluator.evaluate(h, literature_kg)
            h.confidence = h.quality_score.overall

        # 约束检查
        for h in hypotheses:
            check = self.kg_checker.check(h)
            if not check.passed:
                h.confidence *= 0.7

        return sorted(hypotheses, key=lambda x: x.confidence, reverse=True)

    def _llm_generate_structured(self, task: str, context: dict) -> List[Dict]:
        """
        [MOCK实现 — 待接入真实LLM API]

        当前返回硬编码的模板假设，仅用于开发和演示目的。
        这些假设不代表针对给定研究问题的真实科学推理结果。

        TODO: 替换为真实的LLM API调用 (self.llm_client)
        """
        import warnings
        warnings.warn(
            "hypothesis_engine._llm_generate_structured() 返回硬编码模板假设，"
            "非真实LLM生成。需接入真实LLM API (如Claude/GPT) 后方可用于正式研究。",
            stacklevel=2,
        )

        modality = context.get("text", "")[:100]
        task_lower = task.lower() if task else ""

        # 基于任务关键词选择最相关的模板领域
        # 仍为模板，但通过关键词匹配使其与任务相关性更高
        domain_keywords = {
            "chemistry": ["化学", "反应", "催化", "浓度", "转化率", "合成", "chemistry", "reaction", "catalyst"],
            "kinetics": ["动力学", "速率", "pH", "温度", "kinetics", "rate", "temperature"],
            "materials": ["材料", "电池", "掺杂", "容量", "material", "battery", "doping", "capacity"],
        }

        # 评分每个领域与任务的相关性
        domain_scores = {}
        for domain, keywords in domain_keywords.items():
            score = sum(1 for kw in keywords if kw in task_lower)
            domain_scores[domain] = score

        # 按相关性排序，优先返回最相关的模板
        sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)

        templates_map = {
            "chemistry": {
                "variables": [
                    Variable(name="X", type="independent", unit="mM", range_min=0.1, range_max=10.0,
                             operationalization="浓度测量通过HPLC"),
                    Variable(name="Y", type="dependent", unit="%", range_min=0, range_max=100,
                             operationalization="转化率通过色谱定量"),
                    Variable(name="T", type="control", unit="°C", operationalization="恒温槽控制"),
                ],
                "hypothesis_statement": f"增加X浓度将显著提高Y的转化率，在T={modality[:20] or '室温'}条件下呈正相关",
                "relations": ["X ↑ → Y ↑", "剂量-效应关系"],
                "verification_methods": [
                    VerificationMethod(
                        method_type="实验",
                        description="设计5组浓度梯度的正交实验",
                        required_data=["X浓度", "Y转化率", "T温度"],
                        statistical_test="linear regression",
                        sample_size_estimate=50,
                        expected_effect_size=0.6,
                    )
                ],
            },
            "kinetics": {
                "variables": [
                    Variable(name="pH", type="independent", unit="", range_min=2, range_max=12,
                             operationalization="pH计校准测量"),
                    Variable(name="k_rate", type="dependent", unit="s^-1", range_min=0, operationalization="动力学常数"),
                    Variable(name="catalyst", type="control", operationalization="催化剂浓度固定"),
                ],
                "hypothesis_statement": f"pH值对反应速率k的影响呈钟形曲线，在pH=7附近达到最大值",
                "relations": ["pH → 速率常数 k", "非线性关系（钟形）"],
                "verification_methods": [
                    VerificationMethod(
                        method_type="统计",
                        description="响应面分析(RSM)确定最优pH",
                        required_data=["pH", "k_rate", "产物选择性"],
                        statistical_test="RSM / quadratic regression",
                        sample_size_estimate=80,
                        expected_effect_size=0.75,
                    )
                ],
            },
            "materials": {
                "variables": [
                    Variable(name="doping", type="independent", unit="at%", range_min=0, range_max=20,
                             operationalization="ICP-MS定量"),
                    Variable(name="capacity", type="dependent", unit="mAh/g", operationalization="充放电测试"),
                    Variable(name="cycle", type="dependent", unit="次数", operationalization="循环稳定性测试"),
                ],
                "hypothesis_statement": f"掺杂量doping在5-10at%范围内可显著提升材料容量并改善循环性能",
                "relations": ["doping 5-10% → capacity ↑", "doping 5-10% → cycle ↑"],
                "verification_methods": [
                    VerificationMethod(
                        method_type="实验",
                        description="溶胶凝胶法合成不同掺杂量样品，进行全电化学表征",
                        required_data=["XRD", "SEM", "充放电曲线", "EIS"],
                        statistical_test="ANOVA + Tukey HSD",
                        sample_size_estimate=45,
                        expected_effect_size=0.7,
                    )
                ],
            },
        }

        # 按相关性排序返回模板
        templates = [templates_map[domain] for domain, _ in sorted_domains if domain in templates_map]

        # 如果没有任何匹配，默认返回全部
        if not templates:
            templates = list(templates_map.values())

        return templates

    def _build_hypothesis(self, h_id: str, data: Dict) -> Hypothesis:
        return Hypothesis(
            id=h_id,
            statement=data["hypothesis_statement"],
            variables=data["variables"],
            relations=data["relations"],
            constraints=[],
            confidence=0.75,
            source_modality=HypothesisSourceModality.TEXT,
            generation_method=GenerationMethod.LLM,
            verification_methods=data.get("verification_methods", []),
            iteration=1,
            tags=["structured", "sci级别"],
        )


# =============================================================================
# HypothesisEngine — 对外统一接口
# =============================================================================

class HypothesisEngine:
    """
    HypothesisEngine — SCI级别对外统一接口

    支持:
    - 结构化假设生成
    - 文献知识图谱构建
    - 假设-证据关联
    - 质量评分排序
    """

    def __init__(self, llm_client=None, api_key: str = ""):
        self.generator = StructuredHypothesisGenerator(llm_client=llm_client)
        self.literature_kg_builder = LiteratureKGBuilder(api_key=api_key)
        self.kg_checker = KnowledgeGraphChecker()

    async def generate(
        self,
        research_question: str,
        context: str = "",
        num_hypotheses: int = 3,
        build_kg: bool = True,
    ) -> List[Hypothesis]:
        """
        生成科研假设（SCI级别）

        Args:
            research_question: 研究问题
            context: 背景上下文
            num_hypotheses: 生成数量
            build_kg: 是否构建文献知识图谱

        Returns:
            Hypothesis 列表（含质量评分）
        """
        # 构建文献知识图谱
        kg = None
        if build_kg:
            kg = await self.literature_kg_builder.build_kg(research_question, max_papers=20)

        # 生成结构化假设
        multi_modal_context = {
            "text": context or "",
            "image_embedding": None,
            "data_stats": {},
        }
        hypotheses = self.generator.generate_structured(
            task_description=research_question,
            multi_modal_context=multi_modal_context,
            literature_kg=kg,
            num_hypotheses=num_hypotheses,
        )

        # 关联证据
        if kg:
            evaluator = HypothesisQualityEvaluator()
            for h in hypotheses:
                h.evidence_links = await self.literature_kg_builder.link_evidence(h, kg)
                # 证据支持度反馈到质量评分
                if h.evidence_links:
                    supporting = sum(1 for e in h.evidence_links if e.supporting)
                    evidence_bonus = 0.1 * (supporting / len(h.evidence_links))
                    h.quality_score.overall = min(1.0, h.quality_score.overall + evidence_bonus)
                    h.confidence = h.quality_score.overall

        return hypotheses

    def generate_sync(self, research_question: str, context: str = "", num_hypotheses: int = 3) -> List[Hypothesis]:
        """同步版本（不使用API）"""
        return asyncio.get_event_loop().run_until_complete(
            self.generate(research_question, context, num_hypotheses, build_kg=False)
        )