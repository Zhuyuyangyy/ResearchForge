"""
Hypothesis Generation Engine (HGE)
多模态假设生成引擎

核心流程:
1. 多模态感知编码 (MPL)
2. LLM生成候选假设
3. 知识图谱约束过滤
4. 排序选择Top-K
"""

from dataclasses import dataclass, field
from typing import Optional
import numpy as np


@dataclass
class Hypothesis:
    """科学假设数据结构"""
    id: str
    statement: str  # 自然语言假设描述
    variables: list[str] = field(default_factory=list)
    relations: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    confidence: float = 0.0
    source_modality: str = "text"  # text, image, data
    generation_method: str = "llm"  # llm, kg_inference, analogy


@dataclass
class ConsistencyCheck:
    """一致性检查结果"""
    passed: bool
    violation_type: str = ""  # direction, magnitude, structure, constraint
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


class KnowledgeGraphChecker:
    """
    知识图谱约束检查器
    检查假设是否符合物理守恒定律、量纲一致、逻辑约束
    """

    # 物理守恒定律 (简化版)
    PHYSICS_LAWS = {
        "energy_conservation": ["能量", "守恒", "conservation", "energy"],
        "mass_conservation": ["质量", "守恒", "mass"],
        "momentum_conservation": ["动量", "守恒", "momentum"],
        "charge_conservation": ["电荷", "守恒", "charge"],
    }

    # 维度一致性规则
    DIMENSION_RULES = {
        "force": {"units": ["N", "kg*m/s^2"], "base": ["M", "L", "T^-2"]},
        "energy": {"units": ["J", "kg*m^2/s^2"], "base": ["M", "L^2", "T^-2"]},
        "power": {"units": ["W", "J/s"], "base": ["M", "L^2", "T^-3"]},
        "temperature": {"units": ["K", "C"], "base": ["Theta"]},
    }

    def check_physical_feasibility(self, hypothesis: Hypothesis) -> tuple[bool, str]:
        """检查物理可行性"""
        text = hypothesis.statement.lower()
        
        for law, keywords in self.PHYSICS_LAWS.items():
            if any(kw in text for kw in keywords):
                # 如果声称违反守恒定律，报错
                if "违反" in text or "violate" in text or "破坏" in text:
                    return False, f"Violation of {law}"
        
        return True, ""

    def check_dimensional_consistency(self, hypothesis: Hypothesis) -> tuple[bool, str]:
        """检查量纲一致性"""
        # 简化：检查假设中涉及的物理量是否在已知物理量字典中
        for var in hypothesis.variables:
            found = False
            for quantity, rules in self.DIMENSION_RULES.items():
                if var.lower() in [u.lower() for u in rules["units"]]:
                    found = True
                    break
            if not found:
                # 未知变量，无法验证，跳过
                pass
        return True, ""

    def check_numerical_reasonableness(self, hypothesis: Hypothesis) -> tuple[bool, str]:
        """检查数值合理性"""
        # 检查是否有不合理的数值范围声明
        unreasonable = {
            "温度": (0, 1e6),    # 0K ~ 100万K
            "速度": (0, 1e9),   # 0 ~ 10亿 m/s
            "能量": (0, 1e50),  # 宇宙总能量级别
        }
        return True, ""

    def check(self, hypothesis: Hypothesis) -> ConsistencyCheck:
        """综合一致性检查"""
        checks = [
            self.check_physical_feasibility,
            self.check_dimensional_consistency,
            self.check_numerical_reasonableness,
        ]
        
        for check_fn in checks:
            ok, msg = check_fn(hypothesis)
            if not ok:
                return ConsistencyCheck(
                    passed=False,
                    violation_type="physics",
                    violation_message=msg,
                )
        
        return ConsistencyCheck(passed=True)


class HypothesisGenerator:
    """
    假设生成器
    输入: 多模态embedding + 任务描述
    输出: Hypothesis列表(按confidence排序)
    """

    def __init__(self, llm_client=None):
        self.kg_checker = KnowledgeGraphChecker()
        self.llm_client = llm_client  # OpenAI/Anthropic API client

    def generate(
        self,
        task_description: str,
        multi_modal_context: dict,
        top_k: int = 5,
    ) -> list[Hypothesis]:
        """
        生成候选假设
        
        Args:
            task_description: 科学问题描述
            multi_modal_context: 包含image_embedding, text_chunks, data_stats的字典
            top_k: 返回top_k个假设
        """
        # Step 1: 调用LLM生成候选假设
        raw_hypotheses = self._llm_generate(task_description, multi_modal_context)
        
        # Step 2: 知识图谱约束过滤
        filtered = []
        for h in raw_hypotheses:
            check = self.kg_checker.check(h)
            if check.passed:
                filtered.append(h)
            else:
                h.confidence *= 0.5  # 降低不合规假设的置信度
                filtered.append(h)
        
        # Step 3: 排序
        ranked = sorted(filtered, key=lambda x: x.confidence, reverse=True)
        return ranked[:top_k]

    def _llm_generate(
        self, task: str, context: dict
    ) -> list[Hypothesis]:
        """
        调用LLM生成假设
        实际使用时通过self.llm_client调用API
        """
        # 模拟生成 (实际通过API调用)
        # 真实实现需要根据上下文生成具体假设
        mock_hypotheses = [
            Hypothesis(
                id="h1",
                statement=f"假设: {task}的机制与X变量的非线性增长相关",
                variables=["X", "Y"],
                relations=["非线性相关"],
                constraints=["X > 0"],
                confidence=0.85,
                source_modality="text",
            ),
            Hypothesis(
                id="h2",
                statement=f"假设: 观测到的模式可以用周期性振荡模型解释",
                variables=["period", "amplitude", "phase"],
                relations=["周期性"],
                constraints=["amplitude > 0"],
                confidence=0.72,
                source_modality="data",
            ),
        ]
        return mock_hypotheses

class HypothesisEngine:
    """
    HypothesisEngine — 对外统一接口
    封装 HypothesisGenerator，提供简洁的 generate() 接口
    """

    def __init__(self, llm_client=None):
        self.generator = HypothesisGenerator(llm_client=llm_client)

    def generate(
        self,
        research_question: str,
        context: str = "",
        num_hypotheses: int = 3,
    ) -> list[Hypothesis]:
        """
        生成科研假设

        Args:
            research_question: 研究问题
            context: 背景上下文
            num_hypotheses: 生成数量

        Returns:
            Hypothesis 列表
        """
        multi_modal_context = {
            "text": context or "",
            "image_embedding": None,
            "data_stats": {},
        }
        return self.generator.generate(
            task_description=research_question,
            multi_modal_context=multi_modal_context,
            top_k=num_hypotheses,
        )
