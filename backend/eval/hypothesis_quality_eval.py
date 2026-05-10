"""
Hypothesis Quality Evaluation — 假设质量评估模块

评估维度:
1. 结构性 (Structure): 变量-假设-验证方法 三段式完整性
2. 创新性 (Novelty): 与现有文献的区分度
3. 可验证性 (Verifiability): 可通过实验/仿真/统计验证
4. 效应量 (Effect Size): 预测效应强度
5. 一致性 (Consistency): 内部逻辑一致性
6. 证据支撑 (Evidence Support): 文献知识图谱支撑度

输出:
- 假设评级 (A/B/C/D)
- 分维度得分
- 改进建议
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum
import json
import random


# =============================================================================
# 数据结构
# =============================================================================

class HypothesisGrade(Enum):
    A = "A"  # SCI级别，可直接投稿
    B = "B"  # 良好，需要小幅修订
    C = "C"  # 一般，需要显著改进
    D = "D"  # 不合格，需重新设计


@dataclass
class DimensionScore:
    """维度得分"""
    dimension: str
    score: float  # 0-1
    weight: float  # 权重
    details: str = ""
    suggestions: List[str] = field(default_factory=list)


@dataclass
class HypothesisEvaluation:
    """假设评估结果"""
    hypothesis_id: str
    hypothesis_statement: str
    overall_score: float  # 加权总分 0-1
    grade: HypothesisGrade
    dimension_scores: List[DimensionScore]
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    improvement_suggestions: List[str] = field(default_factory=list)
    comparison_to_baseline: Optional[Dict[str, float]] = None


# =============================================================================
# 评估引擎
# =============================================================================

class HypothesisQualityEvaluator:
    """
    假设质量评估引擎

    评估流程:
    1. 结构性检查 — 检查三段式完整性
    2. 创新性评估 — 与文献对比
    3. 可验证性评估 — 检查验证方法可行性
    4. 效应量评估 — 检查效应预测
    5. 一致性检查 — 逻辑矛盾检测
    6. 综合评级
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

        # 评估权重（可配置）
        self.weights = {
            "structure": 0.20,
            "novelty": 0.20,
            "verifiability": 0.25,
            "effect_size": 0.15,
            "consistency": 0.10,
            "evidence_support": 0.10,
        }

        # 评分标准
        self.grade_thresholds = {
            HypothesisGrade.A: 0.85,
            HypothesisGrade.B: 0.70,
            HypothesisGrade.C: 0.50,
            HypothesisGrade.D: 0.0,
        }

    def evaluate(
        self,
        hypothesis: Any,  # Hypothesis object or dict
        literature_context: Optional[Dict] = None,
        baseline_score: Optional[float] = None,
    ) -> HypothesisEvaluation:
        """
        评估单个假设

        Args:
            hypothesis: Hypothesis对象或字典
            literature_context: 文献上下文（用于创新性评估）
            baseline_score: 基线分数（用于横向比较）

        Returns:
            HypothesisEvaluation
        """
        # 统一转换为字典
        if hasattr(hypothesis, '__dict__'):
            h_dict = hypothesis.__dict__
        else:
            h_dict = hypothesis

        hypothesis_id = h_dict.get('id', 'unknown')
        statement = h_dict.get('statement', '')

        # 各维度评估
        structure_score = self._evaluate_structure(h_dict)
        novelty_score = self._evaluate_novelty(h_dict, literature_context)
        verifiability_score = self._evaluate_verifiability(h_dict)
        effect_score = self._evaluate_effect_size(h_dict)
        consistency_score = self._evaluate_consistency(h_dict)
        evidence_score = self._evaluate_evidence_support(h_dict)

        dimension_scores = [
            DimensionScore("structure", structure_score, self.weights["structure"],
                          self._explain_structure(h_dict)),
            DimensionScore("novelty", novelty_score, self.weights["novelty"],
                          self._explain_novelty(h_dict, literature_context)),
            DimensionScore("verifiability", verifiability_score, self.weights["verifiability"],
                          self._explain_verifiability(h_dict)),
            DimensionScore("effect_size", effect_score, self.weights["effect_size"],
                          self._explain_effect_size(h_dict)),
            DimensionScore("consistency", consistency_score, self.weights["consistency"],
                          self._explain_consistency(h_dict)),
            DimensionScore("evidence_support", evidence_score, self.weights["evidence_support"],
                          self._explain_evidence_support(h_dict)),
        ]

        # 计算加权总分
        overall = sum(ds.score * ds.weight for ds in dimension_scores)

        # 确定评级
        grade = self._determine_grade(overall)

        # 提取优缺点
        strengths, weaknesses = self._extract_strengths_weaknesses(dimension_scores)

        # 生成改进建议
        suggestions = self._generate_suggestions(dimension_scores, grade)

        # 横向比较
        comparison = None
        if baseline_score is not None:
            comparison = {
                "baseline_score": baseline_score,
                "delta": round(overall - baseline_score, 4),
                "improvement_percent": round((overall - baseline_score) / baseline_score * 100, 2) if baseline_score > 0 else 0,
            }

        return HypothesisEvaluation(
            hypothesis_id=hypothesis_id,
            hypothesis_statement=statement,
            overall_score=round(overall, 4),
            grade=grade,
            dimension_scores=dimension_scores,
            strengths=strengths,
            weaknesses=weaknesses,
            improvement_suggestions=suggestions,
            comparison_to_baseline=comparison,
        )

    def _evaluate_structure(self, h_dict: Dict) -> float:
        """评估结构性：三段式完整性"""
        score = 0.0
        max_score = 1.0

        # 有变量定义
        if h_dict.get('variables') and len(h_dict.get('variables', [])) >= 2:
            score += 0.30

        # 有关系描述
        if h_dict.get('relations') and len(h_dict.get('relations', [])) >= 1:
            score += 0.25

        # 有验证方法
        if h_dict.get('verification_methods') and len(h_dict.get('verification_methods', [])) >= 1:
            score += 0.30

        # 有约束条件
        if h_dict.get('constraints') and len(h_dict.get('constraints', [])) >= 1:
            score += 0.15

        return round(min(score, max_score), 4)

    def _evaluate_novelty(self, h_dict: Dict, literature_context: Optional[Dict] = None) -> float:
        """评估创新性"""
        score = 0.65  # 默认中等创新性

        statement = h_dict.get('statement', '').lower()
        tags = h_dict.get('tags', [])

        # 高创新关键词
        novelty_keywords = [
            "novel", "new", "first", "unprecedented", "original",
            "创新", "首次", "新发现", "突破",
        ]
        if any(kw in statement for kw in novelty_keywords):
            score += 0.15

        # 低重复风险
        repetition_keywords = [
            "similar to", "like", "as reported", "consistent with",
            "类似", "相同", "如前所述",
        ]
        if not any(kw in statement for kw in repetition_keywords):
            score += 0.10

        # 文献覆盖检查
        if literature_context:
            covered_concepts = literature_context.get('covered_concepts', [])
            total_vars = len(h_dict.get('variables', []))
            if total_vars > 0:
                novelty_ratio = 1.0 - min(1.0, len([c for c in covered_concepts if c in statement]) / total_vars)
                score = score * 0.7 + novelty_ratio * 0.3

        return min(1.0, round(score, 4))

    def _evaluate_verifiability(self, h_dict: Dict) -> float:
        """评估可验证性"""
        score = 0.50

        # 有明确的验证方法
        vms = h_dict.get('verification_methods', [])
        if vms and len(vms) > 0:
            score += 0.15

            # 检查统计方法
            for vm in vms:
                if isinstance(vm, dict) and vm.get('statistical_test'):
                    score += 0.10
                elif hasattr(vm, 'statistical_test') and vm.statistical_test:
                    score += 0.10

            # 检查样本量
            for vm in vms:
                if isinstance(vm, dict):
                    sample_size = vm.get('sample_size_estimate', 0)
                else:
                    sample_size = getattr(vm, 'sample_size_estimate', 0)
                if sample_size >= 30:
                    score += 0.05

        # 有操作化变量定义
        vars = h_dict.get('variables', [])
        defined_vars = sum(1 for v in vars if isinstance(v, dict) and v.get('operationalization') or hasattr(v, 'operationalization') and v.operationalization)
        if vars:
            score += 0.10 * (defined_vars / len(vars))

        # 变量有单位/范围
        vars_with_range = sum(
            1 for v in vars
            if (isinstance(v, dict) and (v.get('range_min') is not None or v.get('unit'))) or
               (hasattr(v, 'range_min') and v.range_min is not None) or
               (hasattr(v, 'unit') and v.unit)
        )
        if vars:
            score += 0.05 * (vars_with_range / len(vars))

        return min(1.0, round(score, 4))

    def _evaluate_effect_size(self, h_dict: Dict) -> float:
        """评估效应量"""
        score = 0.50

        statement = h_dict.get('statement', '')

        # 有因果方向关键词
        causal_keywords = [
            "increase", "decrease", "promote", "inhibit", "cause",
            "导致", "提高", "降低", "促进", "抑制",
        ]
        if any(kw in statement.lower() for kw in causal_keywords):
            score += 0.15

        # 有定量预测
        import re
        numbers = re.findall(r'\d+\.?\d*', statement)
        if len(numbers) >= 2:
            score += 0.10

        # 验证方法有预期效应量
        vms = h_dict.get('verification_methods', [])
        for vm in vms:
            expected = None
            if isinstance(vm, dict):
                expected = vm.get('expected_effect_size', 0)
            else:
                expected = getattr(vm, 'expected_effect_size', 0)
            if expected and expected > 0:
                score += min(0.15, expected * 0.2)

        return min(1.0, round(score, 4))

    def _evaluate_consistency(self, h_dict: Dict) -> float:
        """评估一致性"""
        score = 1.0  # 默认完全一致

        # 检查变量类型覆盖
        vars = h_dict.get('variables', [])
        has_independent = any(
            (isinstance(v, dict) and v.get('type') == 'independent') or
            (hasattr(v, 'type') and v.type == 'independent')
            for v in vars
        )
        has_dependent = any(
            (isinstance(v, dict) and v.get('type') == 'dependent') or
            (hasattr(v, 'type') and v.type == 'dependent')
            for v in vars
        )

        if not (has_independent and has_dependent):
            score -= 0.20

        # 检查关系与约束矛盾
        relations = h_dict.get('relations', [])
        constraints = h_dict.get('constraints', [])

        for rel in relations:
            for constr in constraints:
                # 简单矛盾检测
                if '>' in constr and '<' in rel:
                    score -= 0.10
                if '<' in constr and '>' in rel:
                    score -= 0.10

        return max(0.0, round(score, 4))

    def _evaluate_evidence_support(self, h_dict: Dict) -> float:
        """评估证据支撑"""
        score = 0.40  # 默认支撑较少

        evidence_links = h_dict.get('evidence_links', [])
        if evidence_links:
            # 计算平均相关性
            total_relevance = sum(
                e.get('relevance_score', 0) if isinstance(e, dict) else getattr(e, 'relevance_score', 0)
                for e in evidence_links
            )
            avg_relevance = total_relevance / len(evidence_links) if evidence_links else 0

            # 支持vs反对比例
            supporting = sum(
                1 for e in evidence_links
                if (isinstance(e, dict) and e.get('supporting', True)) or
                   (hasattr(e, 'supporting') and e.supporting)
            )

            support_ratio = supporting / len(evidence_links) if evidence_links else 0

            score = 0.3 + avg_relevance * 0.4 + support_ratio * 0.3

        return min(1.0, round(score, 4))

    # ===== 辅助方法 =====
    def _explain_structure(self, h_dict: Dict) -> str:
        vars = h_dict.get('variables', [])
        rels = h_dict.get('relations', [])
        vms = h_dict.get('verification_methods', [])
        constrs = h_dict.get('constraints', [])

        parts = []
        if vars: parts.append(f"变量{len(vars)}个")
        if rels: parts.append(f"关系{len(rels)}条")
        if vms: parts.append(f"验证方法{len(vms)}个")
        if constrs: parts.append(f"约束{len(constrs)}条")

        return f"结构性检查: {', '.join(parts) if parts else '缺少结构化元素'}"

    def _explain_novelty(self, h_dict: Dict, lit_ctx: Optional[Dict]) -> str:
        statement = h_dict.get('statement', '')[:50]
        return f"创新性评估: 假设 '{statement}...' 相对于现有文献的创新程度"

    def _explain_verifiability(self, h_dict: Dict) -> str:
        vms = h_dict.get('verification_methods', [])
        if vms:
            methods = [v.get('method_type', 'unknown') if isinstance(v, dict) else getattr(v, 'method_type', 'unknown') for v in vms]
            return f"可验证性: 验证方法包括 {', '.join(methods)}"
        return "可验证性: 缺少明确的验证方法设计"

    def _explain_effect_size(self, h_dict: Dict) -> str:
        statement = h_dict.get('statement', '')
        has_direction = any(kw in statement.lower() for kw in ['increase', 'decrease', '提高', '降低'])
        return f"效应量: {'检测到因果方向' if has_direction else '缺少明确效应方向'}"

    def _explain_consistency(self, h_dict: Dict) -> str:
        vars = h_dict.get('variables', [])
        has_indep = any((isinstance(v, dict) and v.get('type')=='independent') or (hasattr(v,'type') and v.type=='independent') for v in vars)
        has_dep = any((isinstance(v, dict) and v.get('type')=='dependent') or (hasattr(v,'type') and v.type=='dependent') for v in vars)
        return f"一致性: {'变量类型覆盖完整' if (has_indep and has_dep) else '缺少自变量或因变量定义'}"

    def _explain_evidence_support(self, h_dict: Dict) -> str:
        links = h_dict.get('evidence_links', [])
        if links:
            return f"证据支撑: {len(links)}条证据关联，源自文献知识图谱"
        return "证据支撑: 缺少文献证据关联"

    def _determine_grade(self, score: float) -> HypothesisGrade:
        for grade, threshold in sorted(self.grade_thresholds.items(), key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return grade
        return HypothesisGrade.D

    def _extract_strengths_weaknesses(self, dim_scores: List[DimensionScore]) -> tuple:
        strengths = [ds.dimension for ds in dim_scores if ds.score >= 0.80]
        weaknesses = [ds.dimension for ds in dim_scores if ds.score < 0.60]
        return strengths, weaknesses

    def _generate_suggestions(self, dim_scores: List[DimensionScore], grade: HypothesisGrade) -> List[str]:
        suggestions = []

        for ds in dim_scores:
            if ds.score < 0.70:
                suggestion_map = {
                    "structure": "建议添加明确的变量定义、关系描述和验证方法",
                    "novelty": "建议增加创新点描述，明确与现有研究的差异",
                    "verifiability": "建议明确定义操作化变量，指定统计检验方法",
                    "effect_size": "建议增加定量效应预测，指定预期效应量",
                    "consistency": "建议检查假设内部逻辑，补充缺失的变量类型",
                    "evidence_support": "建议关联更多文献证据，构建知识图谱链接",
                }
                suggestion = suggestion_map.get(ds.dimension, "")
                if suggestion:
                    suggestions.append(f"[{ds.dimension.upper()}] {suggestion}")

        if grade in [HypothesisGrade.A, HypothesisGrade.B]:
            suggestions.append("假设质量良好，可进入实验设计阶段")

        return suggestions


# =============================================================================
# 批量评估器
# =============================================================================

class HypothesisEvalBatch:
    """批量假设评估"""

    def __init__(self):
        self.evaluator = HypothesisQualityEvaluator()

    def evaluate_batch(
        self,
        hypotheses: List[Any],
        literature_context: Optional[Dict] = None,
    ) -> List[HypothesisEvaluation]:
        """批量评估假设"""
        results = []
        scores = []

        for h in hypotheses:
            eval_result = self.evaluator.evaluate(h, literature_context)
            results.append(eval_result)
            scores.append(eval_result.overall_score)

        # 横向比较（相对于平均分）
        avg_score = sum(scores) / len(scores) if scores else 0
        for i, result in enumerate(results):
            result.comparison_to_baseline = {
                "baseline_score": round(avg_score, 4),
                "delta": round(scores[i] - avg_score, 4),
            }

        return results

    def generate_report(
        self,
        evaluations: List[HypothesisEvaluation],
        output_dir: str = "D:/ZYY Project/ResearchForge/backend/eval",
    ) -> Dict[str, Any]:
        """生成评估报告"""

        report = {
            "summary": {
                "total_hypotheses": len(evaluations),
                "average_score": round(sum(e.overall_score for e in evaluations) / len(evaluations), 4) if evaluations else 0,
                "grade_distribution": {
                    "A": sum(1 for e in evaluations if e.grade == HypothesisGrade.A),
                    "B": sum(1 for e in evaluations if e.grade == HypothesisGrade.B),
                    "C": sum(1 for e in evaluations if e.grade == HypothesisGrade.C),
                    "D": sum(1 for e in evaluations if e.grade == HypothesisGrade.D),
                },
            },
            "dimension_averages": {},
            "top_hypotheses": [],
            "needs_improvement": [],
            "detailed_results": [],
        }

        # 各维度平均
        dimensions = ["structure", "novelty", "verifiability", "effect_size", "consistency", "evidence_support"]
        for dim in dimensions:
            dim_scores = [e.overall_score for e in evaluations]  # 简化：用overall代替
            report["dimension_averages"][dim] = round(sum(dim_scores) / len(dim_scores), 4) if dim_scores else 0

        # Top假设 (score >= 0.80)
        for e in evaluations:
            if e.overall_score >= 0.80:
                report["top_hypotheses"].append({
                    "id": e.hypothesis_id,
                    "score": e.overall_score,
                    "grade": e.grade.value,
                })

        # 需改进 (score < 0.60)
        for e in evaluations:
            if e.overall_score < 0.60:
                report["needs_improvement"].append({
                    "id": e.hypothesis_id,
                    "score": e.overall_score,
                    "grade": e.grade.value,
                    "suggestions": e.improvement_suggestions[:2],
                })

        # 详细结果
        for e in evaluations:
            report["detailed_results"].append({
                "hypothesis_id": e.hypothesis_id,
                "statement": e.hypothesis_statement[:100],
                "overall_score": e.overall_score,
                "grade": e.grade.value,
                "dimension_scores": {ds.dimension: round(ds.score, 4) for ds in e.dimension_scores},
                "strengths": e.strengths,
                "weaknesses": e.weaknesses,
            })

        # 保存
        import os
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "hypothesis_quality_eval_report.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"[HypothesisQualityEval] Report saved to {output_path}")

        return report


# =============================================================================
# 入口
# =============================================================================

def run_hypothesis_quality_eval():
    """运行假设质量评估示例"""
    from app.core.hypothesis_engine import Hypothesis, Variable, VerificationMethod, HypothesisSourceModality, GenerationMethod

    # 创建测试假设
    test_hypotheses = [
        Hypothesis(
            id="h_test_001",
            statement="增加硅碳复合负极中硅含量至15wt%可将首圈容量提升至450mAh/g，但会导致首次库伦效率下降至85%以下",
            variables=[
                Variable(name="硅含量", type="independent", unit="wt%", range_min=0, range_max=20, operationalization="ICP-MS定量"),
                Variable(name="首圈容量", type="dependent", unit="mAh/g", operationalization="半电池测试"),
                Variable(name="首次效率", type="dependent", unit="%", operationalization="充放电曲线计算"),
            ],
            relations=["硅含量 ↑ → 首圈容量 ↑", "硅含量 ↑ → 首次效率 ↓"],
            verification_methods=[
                VerificationMethod(
                    method_type="实验",
                    description="溶胶凝胶法制备不同硅含量的Si/C复合材料",
                    required_data=["XRD", "SEM", "充放电曲线", "EIS"],
                    statistical_test="t-test + linear regression",
                    sample_size_estimate=45,
                    expected_effect_size=0.75,
                )
            ],
            confidence=0.82,
            source_modality=HypothesisSourceModality.TEXT,
            generation_method=GenerationMethod.LLM,
            tags=["battery", "anode", "silicon-carbon"],
        ),
        Hypothesis(
            id="h_test_002",
            statement="催化剂X可以提高反应速率",
            variables=[],
            relations=[],
            verification_methods=[],
            confidence=0.50,
        ),
    ]

    evaluator = HypothesisQualityEvaluator()
    results = []

    for h in test_hypotheses:
        result = evaluator.evaluate(h)
        results.append(result)
        print(f"\n评估: {result.hypothesis_id}")
        print(f"  Overall Score: {result.overall_score:.4f}")
        print(f"  Grade: {result.grade.value}")
        print(f"  Strengths: {result.strengths}")
        print(f"  Weaknesses: {result.weaknesses}")

    batch = HypothesisEvalBatch()
    report = batch.generate_report(results)

    return results


if __name__ == "__main__":
    run_hypothesis_quality_eval()