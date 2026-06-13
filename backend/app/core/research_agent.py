"""Research Agent Core — 主智能体 + FRE (Feedback Refinement Engine)"""

import asyncio
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from app.core.hypothesis_engine import Hypothesis, ConsistencyCheck, KnowledgeGraphChecker
from app.core.tool_orchestrator import ToolChainOrchestrator, ToolRegistry


@dataclass
class AgentConfig:
    """Agent 配置"""
    max_iterations: int = 10
    confidence_threshold: float = 0.70
    enable_counterfactual: bool = True
    enable_kg_constraint: bool = True


@dataclass
class ResearchTask:
    """科研任务"""
    task_id: str
    research_question: str
    context: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, completed, failed
    iterations: int = 0
    hypotheses: List[Hypothesis] = field(default_factory=list)
    tool_results: List[Dict] = field(default_factory=list)


class ResearchAgent:
    """
    ResearchForge 主智能体

    核心循环:
    1. Hypothesis Generation (HGE)
    2. Tool Chain Execution (TCO)
    3. Feedback Refinement (FRE)
    4. Knowledge Graph Constraint Check (LCC)
    """

    def __init__(
        self,
        hypothesis_engine=None,
        tool_orchestrator: ToolChainOrchestrator = None,
        config: AgentConfig = None,
    ):
        self.hypothesis_engine = hypothesis_engine
        self.tool_orchestrator = tool_orchestrator or ToolChainOrchestrator()
        self.config = config or AgentConfig()
        self.kg_checker = KnowledgeGraphChecker()
        self.task_history: Dict[str, ResearchTask] = {}

    async def run_task(self, task: ResearchTask) -> Dict[str, Any]:
        """
        执行完整科研任务

        Returns:
            {
                "task_id": str,
                "status": str,
                "hypotheses": [...],
                "tool_results": [...],
                "final_report": str,
            }
        """
        task.status = "running"

        try:
            # Phase 1: 假设生成
            hypotheses = await self._generate_hypotheses(task)
            task.hypotheses = hypotheses

            # Phase 2: 工具链执行
            tool_results = await self._execute_tools(task, hypotheses)
            task.tool_results = tool_results

            # Phase 3: 反馈优化
            refined_hypotheses = await self._refine_hypotheses(task, hypotheses, tool_results)
            task.hypotheses = refined_hypotheses

            # Phase 4: 知识图谱约束检查
            final_hypotheses = self._kg_constraint_check(refined_hypotheses)
            task.hypotheses = final_hypotheses
            task.status = "completed"

            return {
                "task_id": task.task_id,
                "status": "completed",
                "hypotheses": [h.__dict__ for h in final_hypotheses],
                "tool_results": tool_results,
                "iterations": task.iterations,
            }

        except Exception as e:
            task.status = "failed"
            return {
                "task_id": task.task_id,
                "status": "failed",
                "error": str(e),
            }

    async def _generate_hypotheses(self, task: ResearchTask) -> List[Hypothesis]:
        """调用假设生成引擎"""
        if self.hypothesis_engine:
            return self.hypothesis_engine.generate(
                task_description=task.research_question,
                multi_modal_context=task.context,
                top_k=5,
            )
        # Mock fallback
        return [
            Hypothesis(
                id="h1",
                statement=f"Hypothesis for: {task.research_question}",
                variables=["X", "Y"],
                relations=["positive correlation"],
                constraints=["X > 0"],
                confidence=0.80,
                source_modality="text",
            )
        ]

    async def _execute_tools(
        self, task: ResearchTask, hypotheses: List[Hypothesis]
    ) -> List[Dict[str, Any]]:
        """
        执行工具链

        [MOCK实现 — 待接入真实工具执行环境]

        当前返回模拟结果，仅用于开发和演示目的。
        模拟输出不代表真实工具执行的输出，不应用于正式研究结论。

        TODO: 替换为通过 tool_orchestrator 调用真实工具 (仿真/实验/检索)
        """
        results = []
        for h in hypotheses:
            results.append({
                "hypothesis_id": h.id,
                "tool": "simulation",
                "output": (
                    f"[MOCK/SIMULATED] 模拟结果: {h.statement[:50]}... "
                    "注意: 此结果由模拟环境生成，非真实工具执行输出。"
                    "需接入真实工具执行环境后方可用于正式研究。"
                ),
                "success": True,
                "_disclaimer": "mock_result",
            })
        return results

    async def _refine_hypotheses(
        self, task: ResearchTask,
        hypotheses: List[Hypothesis],
        tool_results: List[Dict],
    ) -> List[Hypothesis]:
        """FRE: 基于工具执行结果迭代优化假设"""
        task.iterations += 1

        # 如果置信度低于阈值，继续优化
        refined = []
        for h in hypotheses:
            if h.confidence < self.config.confidence_threshold:
                # 模拟置信度提升
                h.confidence = min(0.95, h.confidence * 1.1)
            refined.append(h)

        return refined

    def _kg_constraint_check(self, hypotheses: List[Hypothesis]) -> List[Hypothesis]:
        """LCC: 知识图谱约束检查"""
        if not self.config.enable_kg_constraint:
            return hypotheses

        filtered = []
        for h in hypotheses:
            check = self.kg_checker.check(h)
            if not check.passed:
                h.confidence *= 0.7  # 降低不合规假设置信度
            filtered.append(h)

        return filtered
