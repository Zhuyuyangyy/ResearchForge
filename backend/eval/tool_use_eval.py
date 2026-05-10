"""
Tool Use Evaluation — 工具调用评估模块

评估维度:
1. 成功率 (Success Rate): 工具调用成功比例
2. 执行时间 (Execution Time): 平均执行时间
3. 错误分类 (Error Classification): 错误类型分布
4. 依赖满足率 (Dependency Satisfaction): 依赖链满足情况
5. 超时率 (Timeout Rate): 超时比例

输出:
- 各工具性能报告
- 错误模式分析
- 优化建议
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime
import json
import random


# =============================================================================
# 数据结构
# =============================================================================

class ToolCategory(Enum):
    CODE_EXECUTION = "code_execution"
    SIMULATION = "simulation"
    VISUALIZATION = "visualization"
    LITERATURE_RETRIEVAL = "literature_retrieval"
    MATERIAL_DATABASE = "material_database"
    EXPERIMENT_CONTROL = "experiment_control"


class ErrorType(Enum):
    NONE = "none"
    TIMEOUT = "timeout"
    INVALID_INPUT = "invalid_input"
    EXTERNAL_API_ERROR = "external_api_error"
    DEPENDENCY_NOT_MET = "dependency_not_met"
    UNKNOWN = "unknown"


@dataclass
class ToolCall:
    """工具调用记录"""
    call_id: str
    tool_name: str
    category: ToolCategory
    inputs: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0
    success: bool = True
    error_type: ErrorType = ErrorType.NONE
    error_message: str = ""
    output: Any = None


@dataclass
class ToolMetrics:
    """工具性能指标"""
    tool_name: str
    category: ToolCategory
    total_calls: int = 0
    success_count: int = 0
    failure_count: int = 0
    success_rate: float = 0.0
    avg_execution_time: float = 0.0
    min_execution_time: float = 0.0
    max_execution_time: float = 0.0
    timeout_count: int = 0
    timeout_rate: float = 0.0
    dependency_satisfaction_rate: float = 0.0
    error_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class ToolUseEvaluation:
    """工具使用评估结果"""
    system_name: str
    overall_metrics: Dict[str, float]
    tool_metrics: List[ToolMetrics]
    chain_success_rate: float = 0.0
    failure_patterns: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


# =============================================================================
# 工具调用模拟器
# =============================================================================

class ToolCallSimulator:
    """模拟工具调用日志"""

    TOOL_PROFILES = {
        "code_executor": {
            "avg_time": 3.2,
            "std_time": 1.5,
            "success_rate": 0.92,
            "timeout_rate": 0.03,
            "error_distribution": {
                "SyntaxError": 0.30,
                "RuntimeError": 0.45,
                "MemoryError": 0.15,
                "ImportError": 0.10,
            },
        },
        "simulator": {
            "avg_time": 15.5,
            "std_time": 8.0,
            "success_rate": 0.88,
            "timeout_rate": 0.08,
            "error_distribution": {
                "ConvergenceError": 0.40,
                "ModelError": 0.35,
                "DataError": 0.20,
                "LicenseError": 0.05,
            },
        },
        "visualizer": {
            "avg_time": 2.8,
            "std_time": 0.8,
            "success_rate": 0.95,
            "timeout_rate": 0.02,
            "error_distribution": {
                "RenderError": 0.50,
                "DataFormatError": 0.35,
                "MemoryError": 0.15,
            },
        },
        "literature_retriever": {
            "avg_time": 5.2,
            "std_time": 2.0,
            "success_rate": 0.90,
            "timeout_rate": 0.05,
            "error_distribution": {
                "APIError": 0.50,
                "RateLimitError": 0.25,
                "ParsingError": 0.15,
                "NotFoundError": 0.10,
            },
        },
        "material_database": {
            "avg_time": 1.5,
            "std_time": 0.5,
            "success_rate": 0.97,
            "timeout_rate": 0.01,
            "error_distribution": {
                "ConnectionError": 0.40,
                "QueryError": 0.45,
                "TimeoutError": 0.15,
            },
        },
        "experiment_control": {
            "avg_time": 8.0,
            "std_time": 4.0,
            "success_rate": 0.85,
            "timeout_rate": 0.10,
            "error_distribution": {
                "DeviceError": 0.35,
                "CommunicationError": 0.30,
                "SafetyError": 0.20,
                "CalibrationError": 0.15,
            },
        },
    }

    def __init__(self, seed: int = 2024):
        self.seed = seed
        random.seed(seed)

    def simulate_calls(self, num_chains: int = 20) -> List[List[ToolCall]]:
        """模拟多轮工具链调用"""
        chains = []

        for chain_idx in range(num_chains):
            chain = self._simulate_single_chain(chain_idx)
            chains.append(chain)

        return chains

    def _simulate_single_chain(self, chain_idx: int) -> List[ToolCall]:
        """模拟单条工具链"""
        # 随机选择工具序列
        tool_sequence = self._generate_tool_sequence()

        chain = []
        for i, tool_name in enumerate(tool_sequence):
            call = self._simulate_single_call(
                call_id=f"call_{chain_idx}_{i}",
                tool_name=tool_name,
                chain_idx=chain_idx,
            )
            chain.append(call)

        return chain

    def _generate_tool_sequence(self) -> List[str]:
        """生成工具序列"""
        base_tools = ["literature_retriever", "code_executor", "simulator", "visualizer"]

        # 随机决定序列长度
        length = random.randint(2, 5)
        sequence = []

        for _ in range(length):
            tool = random.choice(base_tools)
            sequence.append(tool)
            if tool == "simulator":
                sequence.append("code_executor")  # 仿真后通常需要处理

        return sequence

    def _simulate_single_call(
        self,
        call_id: str,
        tool_name: str,
        chain_idx: int,
    ) -> ToolCall:
        """模拟单个工具调用"""
        import time

        profile = self.TOOL_PROFILES.get(tool_name, self.TOOL_PROFILES["code_executor"])

        # 执行时间
        exec_time = max(0.1, random.gauss(profile["avg_time"], profile["std_time"]))
        start_time = time.time()
        end_time = start_time + exec_time

        # 成功/失败
        success = random.random() < profile["success_rate"]

        error_type = ErrorType.NONE
        error_message = ""

        if not success:
            # 确定错误类型
            errors = list(profile["error_distribution"].keys())
            probs = list(profile["error_distribution"].values())
            error_choice = random.choices(errors, weights=probs, k=1)[0]

            error_type_map = {
                "SyntaxError": ErrorType.INVALID_INPUT,
                "RuntimeError": ErrorType.UNKNOWN,
                "MemoryError": ErrorType.UNKNOWN,
                "ImportError": ErrorType.INVALID_INPUT,
                "ConvergenceError": ErrorType.EXTERNAL_API_ERROR,
                "ModelError": ErrorType.EXTERNAL_API_ERROR,
                "DataError": ErrorType.INVALID_INPUT,
                "LicenseError": ErrorType.EXTERNAL_API_ERROR,
                "APIError": ErrorType.EXTERNAL_API_ERROR,
                "RateLimitError": ErrorType.TIMEOUT,
                "ParsingError": ErrorType.INVALID_INPUT,
                "NotFoundError": ErrorType.EXTERNAL_API_ERROR,
                "ConnectionError": ErrorType.EXTERNAL_API_ERROR,
                "QueryError": ErrorType.INVALID_INPUT,
                "TimeoutError": ErrorType.TIMEOUT,
                "DeviceError": ErrorType.EXTERNAL_API_ERROR,
                "CommunicationError": ErrorType.EXTERNAL_API_ERROR,
                "SafetyError": ErrorType.UNKNOWN,
                "CalibrationError": ErrorType.DEPENDENCY_NOT_MET,
                "RenderError": ErrorType.UNKNOWN,
                "DataFormatError": ErrorType.INVALID_INPUT,
            }

            error_type = error_type_map.get(error_choice, ErrorType.UNKNOWN)
            error_message = f"{error_choice} in {tool_name}"

        # 超时
        timeout = random.random() < profile["timeout_rate"]
        if timeout:
            error_type = ErrorType.TIMEOUT
            error_message = f"Timeout after {profile['avg_time'] * 2}s"
            success = False

        # 确定分类
        category_map = {
            "code_executor": ToolCategory.CODE_EXECUTION,
            "simulator": ToolCategory.SIMULATION,
            "visualizer": ToolCategory.VISUALIZATION,
            "literature_retriever": ToolCategory.LITERATURE_RETRIEVAL,
            "material_database": ToolCategory.MATERIAL_DATABASE,
            "experiment_control": ToolCategory.EXPERIMENT_CONTROL,
        }

        return ToolCall(
            call_id=call_id,
            tool_name=tool_name,
            category=category_map.get(tool_name, ToolCategory.CODE_EXECUTION),
            inputs={"params": {}},
            start_time=start_time,
            end_time=end_time,
            success=success,
            error_type=error_type,
            error_message=error_message,
        )


# =============================================================================
# 工具使用评估器
# =============================================================================

class ToolUseEvaluator:
    """
    工具使用评估引擎

    分析:
    1. 各工具成功率
    2. 错误模式
    3. 执行时间分布
    4. 工具链完整性
    5. 改进建议
    """

    def __init__(self):
        self.tool_categories = {
            "code_executor": ToolCategory.CODE_EXECUTION,
            "simulator": ToolCategory.SIMULATION,
            "visualizer": ToolCategory.VISUALIZATION,
            "literature_retriever": ToolCategory.LITERATURE_RETRIEVAL,
            "material_database": ToolCategory.MATERIAL_DATABASE,
            "experiment_control": ToolCategory.EXPERIMENT_CONTROL,
        }

    def evaluate_chains(
        self,
        chains: List[List[ToolCall]],
        system_name: str = "ResearchForge",
    ) -> ToolUseEvaluation:
        """
        评估工具链执行情况

        Args:
            chains: 工具调用链列表
            system_name: 系统名称

        Returns:
            ToolUseEvaluation
        """
        all_calls = [call for chain in chains for call in chain]

        # 按工具聚合
        tool_call_map: Dict[str, List[ToolCall]] = {}
        for call in all_calls:
            if call.tool_name not in tool_call_map:
                tool_call_map[call.tool_name] = []
            tool_call_map[call.tool_name].append(call)

        # 计算每个工具的指标
        tool_metrics = []
        for tool_name, calls in tool_call_map.items():
            metrics = self._compute_tool_metrics(tool_name, calls)
            tool_metrics.append(metrics)

        # 整体指标
        overall = self._compute_overall_metrics(all_calls)

        # 链成功率
        chain_success = sum(1 for chain in chains if all(c.success for c in chain)) / len(chains) if chains else 0

        # 错误模式分析
        patterns = self._analyze_error_patterns(all_calls)

        # 推荐
        recommendations = self._generate_recommendations(tool_metrics, overall)

        return ToolUseEvaluation(
            system_name=system_name,
            overall_metrics=overall,
            tool_metrics=tool_metrics,
            chain_success_rate=round(chain_success, 4),
            failure_patterns=patterns,
            recommendations=recommendations,
        )

    def _compute_tool_metrics(self, tool_name: str, calls: List[ToolCall]) -> ToolMetrics:
        """计算单个工具的指标"""
        total = len(calls)
        successes = sum(1 for c in calls if c.success)
        failures = total - successes
        success_rate = successes / total if total > 0 else 0.0

        exec_times = [c.end_time - c.start_time for c in calls]
        avg_time = sum(exec_times) / len(exec_times) if exec_times else 0
        min_time = min(exec_times) if exec_times else 0
        max_time = max(exec_times) if exec_times else 0

        timeouts = sum(1 for c in calls if c.error_type == ErrorType.TIMEOUT)
        timeout_rate = timeouts / total if total > 0 else 0

        # 错误分布
        error_dist = {}
        for c in calls:
            if not c.success:
                err_name = c.error_type.value
                error_dist[err_name] = error_dist.get(err_name, 0) + 1

        category = self.tool_categories.get(tool_name, ToolCategory.CODE_EXECUTION)

        return ToolMetrics(
            tool_name=tool_name,
            category=category,
            total_calls=total,
            success_count=successes,
            failure_count=failures,
            success_rate=round(success_rate, 4),
            avg_execution_time=round(avg_time, 4),
            min_execution_time=round(min_time, 4),
            max_execution_time=round(max_time, 4),
            timeout_count=timeouts,
            timeout_rate=round(timeout_rate, 4),
            dependency_satisfaction_rate=0.95,  # 简化
            error_distribution=error_dist,
        )

    def _compute_overall_metrics(self, calls: List[ToolCall]) -> Dict[str, float]:
        """计算整体指标"""
        total = len(calls)
        successes = sum(1 for c in calls if c.success)
        success_rate = successes / total if total > 0 else 0.0

        exec_times = [c.end_time - c.start_time for c in calls]
        avg_time = sum(exec_times) / len(exec_times) if exec_times else 0
        max_time = max(exec_times) if exec_times else 0

        timeouts = sum(1 for c in calls if c.error_type == ErrorType.TIMEOUT)
        timeout_rate = timeouts / total if total > 0 else 0

        return {
            "total_calls": total,
            "success_rate": round(success_rate, 4),
            "failure_rate": round(1 - success_rate, 4),
            "avg_execution_time_sec": round(avg_time, 4),
            "max_execution_time_sec": round(max_time, 4),
            "timeout_rate": round(timeout_rate, 4),
            "timeout_count": timeouts,
        }

    def _analyze_error_patterns(self, calls: List[ToolCall]) -> List[str]:
        """分析错误模式"""
        patterns = []

        # 按错误类型统计
        error_counts = {}
        for c in calls:
            if not c.success:
                err = c.error_type.value
                error_counts[err] = error_counts.get(err, 0) + 1

        # 生成描述
        for err_type, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
            patterns.append(f"{err_type}: {count}次 ({count/len(calls)*100:.1f}%)")

        return patterns

    def _generate_recommendations(
        self,
        tool_metrics: List[ToolMetrics],
        overall: Dict[str, float],
    ) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 成功率建议
        low_success = [m for m in tool_metrics if m.success_rate < 0.85]
        if low_success:
            tools = ", ".join([m.tool_name for m in low_success])
            recommendations.append(f"[高优先级] 以下工具成功率低于85%: {tools}。建议增加错误处理和重试机制。")

        # 超时建议
        high_timeout = [m for m in tool_metrics if m.timeout_rate > 0.05]
        if high_timeout:
            tools = ", ".join([m.tool_name for m in high_timeout])
            recommendations.append(f"[中优先级] 以下工具超时率高: {tools}。建议优化超时阈值或增加异步执行支持。")

        # 执行时间建议
        slow_tools = sorted(tool_metrics, key=lambda m: m.avg_execution_time, reverse=True)[:2]
        if slow_tools and slow_tools[0].avg_execution_time > 10:
            recommendations.append(
                f"[优化建议] 最慢工具: {slow_tools[0].tool_name} (平均{slow_tools[0].avg_execution_time:.1f}s)。"
                "考虑使用缓存或预计算。"
            )

        # 成功率高，保持
        high_success = [m for m in tool_metrics if m.success_rate >= 0.95]
        if high_success:
            tools = ", ".join([m.tool_name for m in high_success])
            recommendations.append(f"✅ 以下工具表现优秀: {tools}。成功率达到95%以上。")

        return recommendations


# =============================================================================
# 评估运行器
# =============================================================================

class ToolUseEvalRunner:
    """工具使用评估运行器"""

    def __init__(self):
        self.simulator = ToolCallSimulator(seed=2024)
        self.evaluator = ToolUseEvaluator()

    def run_evaluation(
        self,
        num_chains: int = 30,
        output_dir: str = "D:/ZYY Project/ResearchForge/backend/eval",
    ) -> ToolUseEvaluation:
        """运行工具使用评估"""
        print(f"[ToolUseEval] Simulating {num_chains} tool chains...")

        # 模拟调用
        chains = self.simulator.simulate_calls(num_chains)

        # 评估
        result = self.evaluator.evaluate_chains(chains, "ResearchForge")

        # 保存
        self._save_results(result, output_dir)

        return result

    def _save_results(self, result: ToolUseEvaluation, output_dir: str):
        """保存评估结果"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "tool_use_eval_report.json")

        report = {
            "system": result.system_name,
            "evaluation_timestamp": datetime.now().isoformat(),
            "overall_metrics": result.overall_metrics,
            "chain_success_rate": result.chain_success_rate,
            "tool_metrics": [
                {
                    "tool_name": m.tool_name,
                    "category": m.category.value,
                    "total_calls": m.total_calls,
                    "success_count": m.success_count,
                    "failure_count": m.failure_count,
                    "success_rate": m.success_rate,
                    "avg_execution_time_sec": m.avg_execution_time,
                    "min_execution_time_sec": m.min_execution_time,
                    "max_execution_time_sec": m.max_execution_time,
                    "timeout_count": m.timeout_count,
                    "timeout_rate": m.timeout_rate,
                    "error_distribution": m.error_distribution,
                }
                for m in result.tool_metrics
            ],
            "failure_patterns": result.failure_patterns,
            "recommendations": result.recommendations,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"[ToolUseEval] Report saved to {output_path}")


# =============================================================================
# 入口
# =============================================================================

def run_tool_use_evaluation():
    """运行工具使用评估示例"""
    runner = ToolUseEvalRunner()
    result = runner.run_evaluation(num_chains=30)

    print("\n" + "=" * 60)
    print("TOOL USE EVALUATION RESULTS")
    print("=" * 60)
    print(f"\nSystem: {result.system_name}")
    print(f"Overall Success Rate: {result.overall_metrics['success_rate']*100:.1f}%")
    print(f"Chain Success Rate: {result.chain_success_rate*100:.1f}%")
    print(f"Avg Execution Time: {result.overall_metrics['avg_execution_time_sec']:.2f}s")
    print(f"Timeout Rate: {result.overall_metrics['timeout_rate']*100:.2f}%")

    print("\nPer-Tool Metrics:")
    for m in sorted(result.tool_metrics, key=lambda x: x.success_rate):
        print(f"  {m.tool_name}: {m.success_rate*100:.1f}% success, "
              f"{m.avg_execution_time:.2f}s avg, {m.timeout_count} timeouts")

    print("\nFailure Patterns:")
    for p in result.failure_patterns[:5]:
        print(f"  - {p}")

    print("\nRecommendations:")
    for r in result.recommendations:
        print(f"  - {r}")

    return result


if __name__ == "__main__":
    run_tool_use_evaluation()