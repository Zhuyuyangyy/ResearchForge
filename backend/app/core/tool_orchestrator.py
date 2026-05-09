"""
Tool Chain Orchestrator (TCO)
状态机驱动的工具链编排器

状态转换: READY -> EXECUTING -> VALIDATING -> FEEDBACK -> REFINE -> DONE

核心功能:
1. 依赖解析: 自动识别工具间数据依赖关系
2. 执行计划: 拓扑排序生成最小依赖执行计划
3. 状态机: 管理工具执行全流程
4. 超时/重试: 单点失败不影响整体流程
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import asyncio


class ToolState(Enum):
    READY = "ready"
    EXECUTING = "executing"
    VALIDATING = "validating"
    FEEDBACK = "feedback"
    REFINE = "refine"
    DONE = "done"
    FAILED = "failed"


@dataclass
class ToolCall:
    """单个工具调用"""
    tool_name: str
    inputs: dict
    dependencies: list[str] = field(default_factory=list)  # 依赖的tool_call_id列表
    output_key: str = ""  # 输出结果存储的key
    timeout: float = 30.0  # 超时秒数
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class ToolResult:
    """工具执行结果"""
    tool_call_id: str
    success: bool
    output: any = None
    error: str = ""
    execution_time: float = 0.0
    state: ToolState = ToolState.DONE


class CodeExecutor:
    """代码执行工具"""
    name = "code_executor"

    def __init__(self):
        self.results = {}

    async def execute(self, code: str, params: dict) -> dict:
        """执行Python代码，返回结果"""
        # 实际通过subprocess执行
        # 这里模拟返回
        try:
            # 真实场景: exec(code, {"__builtins__": {}})
            output = {"status": "success", "result": 42.0, "stdout": "computed"}
            return output
        except Exception as e:
            return {"status": "error", "error": str(e)}


class Simulator:
    """外部仿真工具"""
    name = "simulator"

    async def execute(self, model: str, params: dict) -> dict:
        """调用外部仿真软件"""
        try:
            # 模拟仿真执行
            result = {"status": "success", "simulation_data": [1.0, 2.0, 3.0]}
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}


class Visualizer:
    """数据可视化工具"""
    name = "visualizer"

    async def execute(self, data: list, chart_type: str = "line") -> dict:
        """生成可视化图表"""
        return {
            "status": "success",
            "chart_description": f"{chart_type} chart generated",
            "image_base64": "",  # 实际返回图像base64
        }


class LiteratureRetriever:
    """文献检索工具"""
    name = "literature_retriever"

    async def execute(self, keywords: list[str]) -> dict:
        """检索相关文献"""
        return {
            "status": "success",
            "papers": [
                {"title": "Related Work 1", "abstract": "...", "year": 2023},
                {"title": "Related Work 2", "abstract": "...", "year": 2024},
            ]
        }


class ToolRegistry:
    """工具注册表"""

    def __init__(self):
        self.tools = {
            "code_executor": CodeExecutor(),
            "simulator": Simulator(),
            "visualizer": Visualizer(),
            "literature_retriever": LiteratureRetriever(),
        }

    def get(self, name: str):
        return self.tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self.tools.keys())


class ToolChainOrchestrator:
    """
    工具链编排器
    核心功能:
    1. 依赖解析: 分析工具间数据依赖
    2. 执行计划: 拓扑排序
    3. 状态机执行
    4. 超时/重试
    """

    def __init__(self, registry: Optional[ToolRegistry] = None):
        self.registry = registry or ToolRegistry()
        self.state = ToolState.READY
        self.execution_log: list[ToolResult] = []
        self._cache: dict = {}  # 中间结果缓存

    def plan(self, hypothesis: str, available_tools: list[str]) -> list[ToolCall]:
        """
        将假设分解为工具调用序列
        基于假设内容智能规划工具使用顺序
        """
        plan = []

        # 简单启发式规划
        if "代码" in hypothesis or "计算" in hypothesis:
            plan.append(ToolCall(
                tool_name="code_executor",
                inputs={"code": "print('placeholder')", "params": {}},
                dependencies=[],
                output_key="code_result",
            ))

        if "仿真" in hypothesis or "模型" in hypothesis:
            plan.append(ToolCall(
                tool_name="simulator",
                inputs={"model": "default", "params": {}},
                dependencies=["code_result"] if plan else [],
                output_key="simulation_data",
            ))

        if "图表" in hypothesis or "可视化" in hypothesis:
            plan.append(ToolCall(
                tool_name="visualizer",
                inputs={"data": [], "chart_type": "line"},
                dependencies=["simulation_data"],  # 依赖仿真结果
                output_key="chart",
            ))

        if "文献" in hypothesis or "相关研究" in hypothesis:
            plan.append(ToolCall(
                tool_name="literature_retriever",
                inputs={"keywords": hypothesis.split()},
                dependencies=[],
                output_key="literature",
            ))

        return plan

    def topological_sort(self, calls: list[ToolCall]) -> list[ToolCall]:
        """
        拓扑排序: 生成最小依赖执行计划
        Kahn算法
        """
        # 计算入度
        in_degree = {c.output_key: 0 for c in calls}
        for call in calls:
            for dep in call.dependencies:
                if dep in in_degree:
                    in_degree[call.output_key] += 1

        queue = [c for c in calls if in_degree[c.output_key] == 0]
        sorted_calls = []

        while queue:
            call = queue.pop(0)
            sorted_calls.append(call)
            for c in calls:
                if call.output_key in c.dependencies:
                    in_degree[c.output_key] -= 1
                    if in_degree[c.output_key] == 0:
                        queue.append(c)

        return sorted_calls

    async def execute_plan(self, plan: list[ToolCall]) -> list[ToolResult]:
        """执行工具调用计划"""
        results = []
        self.state = ToolState.EXECUTING

        sorted_plan = self.topological_sort(plan)

        for call in sorted_plan:
            self.state = ToolState.EXECUTING

            # 检查依赖是否满足
            deps_ready = all(
                self._cache.get(dep) is not None
                for dep in call.dependencies
            )
            if not deps_ready:
                results.append(ToolResult(
                    tool_call_id=call.output_key,
                    success=False,
                    error="Dependencies not satisfied",
                    state=ToolState.FAILED,
                ))
                continue

            # 获取工具
            tool = self.registry.get(call.tool_name)
            if not tool:
                results.append(ToolResult(
                    tool_call_id=call.output_key,
                    success=False,
                    error=f"Tool {call.tool_name} not found",
                    state=ToolState.FAILED,
                ))
                continue

            # 执行工具
            try:
                import time
                t0 = time.time()

                # 注入依赖数据到输入
                inputs = call.inputs.copy()
                for dep in call.dependencies:
                    inputs[dep] = self._cache[dep]

                # 异步执行
                output = await asyncio.wait_for(
                    tool.execute(**inputs),
                    timeout=call.timeout,
                )

                elapsed = time.time() - t0
                success = output.get("status") == "success"

                result = ToolResult(
                    tool_call_id=call.output_key,
                    success=success,
                    output=output,
                    execution_time=elapsed,
                    state=ToolState.VALIDATING if success else ToolState.FAILED,
                )

                if success:
                    self._cache[call.output_key] = output

            except asyncio.TimeoutError:
                result = ToolResult(
                    tool_call_id=call.output_key,
                    success=False,
                    error=f"Timeout after {call.timeout}s",
                    state=ToolState.FAILED,
                )
            except Exception as e:
                result = ToolResult(
                    tool_call_id=call.output_key,
                    success=False,
                    error=str(e),
                    state=ToolState.FAILED,
                )

            results.append(result)
            self.execution_log.append(result)

            if result.state == ToolState.FAILED:
                self.state = ToolState.FEEDBACK
                break

        self.state = ToolState.DONE if all(r.success for r in results) else ToolState.FEEDBACK
        return results

    def reset(self):
        """重置状态"""
        self.state = ToolState.READY
        self.execution_log.clear()
        self._cache.clear()
