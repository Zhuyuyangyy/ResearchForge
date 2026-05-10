"""
Retrieval Accuracy Evaluation — 文献检索评估模块

评估维度:
1. 精确率 (Precision): 检索结果中相关文献的比例
2. 召回率 (Recall): 召回的相关文献占全部相关文献的比例
3. F1分数: 精确率和召回率的调和平均
4. NDCG: 排序质量评估
5. MRR: 平均倒数排名

输出:
- 各指标得分
- PR曲线数据
- 检索案例详细分析
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json
import math


# =============================================================================
# 数据结构
# =============================================================================

class RelevanceLevel(Enum):
    IRRELEVANT = 0
    PARTIAL = 1
    RELEVANT = 2
    HIGHLY_RELEVANT = 3


@dataclass
class RetrievalQuery:
    """检索查询"""
    query_id: str
    query_text: str
    ground_truth_ids: List[str]  # 相关文档ID
    domain: str = ""


@dataclass
class RetrievedDocument:
    """检索到的文档"""
    doc_id: str
    title: str
    abstract: str = ""
    score: float = 0.0
    rank: int = 0
    relevance_level: RelevanceLevel = RelevanceLevel.IRRELEVANT


@dataclass
class RetrievalMetrics:
    """检索评估指标"""
    precision_at_k: float  # P@K
    recall_at_k: float
    f1_at_k: float
    ndcg: float
    mrr: float
    average_precision: float  # AP


@dataclass
class RetrievalEvalResult:
    """单次检索评估结果"""
    query_id: str
    query_text: str
    metrics: RetrievalMetrics
    retrieved_docs: List[RetrievedDocument]
    analysis: str = ""


# =============================================================================
# 评估引擎
# =============================================================================

class RetrievalAccuracyEvaluator:
    """
    文献检索准确性评估引擎

    支持评估:
    - Semantic Scholar API 检索
    - 关键词检索
    - 向量相似度检索
    - RAG系统检索
    """

    def __init__(self):
        self.k_values = [5, 10, 20]  # 评估的K值

    def evaluate_query(
        self,
        query: RetrievalQuery,
        retrieved_docs: List[RetrievedDocument],
        k: int = 10,
    ) -> RetrievalEvalResult:
        """
        评估单个查询的检索结果

        Args:
            query: 检索查询
            retrieved_docs: 检索到的文档列表
            k: 评估前k个结果

        Returns:
            RetrievalEvalResult
        """
        # 限制结果数量
        top_k_docs = retrieved_docs[:k]

        # 计算相关文档数
        ground_truth = set(query.ground_truth_ids)
        retrieved_set = set(doc.doc_id for doc in top_k_docs)

        # 精确率
        relevant_retrieved = len(ground_truth & retrieved_set)
        precision = relevant_retrieved / k if k > 0 else 0.0

        # 召回率
        total_relevant = len(ground_truth)
        recall = relevant_retrieved / total_relevant if total_relevant > 0 else 0.0

        # F1
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        # AP (Average Precision)
        ap = self._calculate_ap(top_k_docs, ground_truth)

        # NDCG
        ndcg = self._calculate_ndcg(top_k_docs, ground_truth)

        # MRR
        mrr = self._calculate_mrr(top_k_docs, ground_truth)

        metrics = RetrievalMetrics(
            precision_at_k=round(precision, 4),
            recall_at_k=round(recall, 4),
            f1_at_k=round(f1, 4),
            ndcg=round(ndcg, 4),
            mrr=round(mrr, 4),
            average_precision=round(ap, 4),
        )

        analysis = self._generate_analysis(query, top_k_docs, metrics)

        return RetrievalEvalResult(
            query_id=query.query_id,
            query_text=query.query_text,
            metrics=metrics,
            retrieved_docs=top_k_docs,
            analysis=analysis,
        )

    def evaluate_batch(
        self,
        queries: List[RetrievalQuery],
        retrieval_func: callable,  # function(query) -> List[RetrievedDocument]
    ) -> Dict[str, Any]:
        """
        批量评估检索系统

        Args:
            queries: 查询列表
            retrieval_func: 检索函数，接收query返回doc列表

        Returns:
            批量评估报告
        """
        results = []
        all_precisions = []
        all_recalls = []
        all_f1s = []
        all_ndcgs = []
        all_mrrs = []
        all_aps = []

        for query in queries:
            retrieved = retrieval_func(query)
            result = self.evaluate_query(query, retrieved, k=10)
            results.append(result)

            all_precisions.append(result.metrics.precision_at_k)
            all_recalls.append(result.metrics.recall_at_k)
            all_f1s.append(result.metrics.f1_at_k)
            all_ndcgs.append(result.metrics.ndcg)
            all_mrrs.append(result.metrics.mrr)
            all_aps.append(result.metrics.average_precision)

        # 汇总统计
        report = {
            "summary": {
                "total_queries": len(queries),
                "mean_precision@10": round(sum(all_precisions) / len(all_precisions), 4),
                "mean_recall@10": round(sum(all_recalls) / len(all_recalls), 4),
                "mean_f1@10": round(sum(all_f1s) / len(all_f1s), 4),
                "mean_ndcg": round(sum(all_ndcgs) / len(all_ndcgs), 4),
                "mean_mrr": round(sum(all_mrrs) / len(all_mrrs), 4),
                "mean_average_precision": round(sum(all_aps) / len(all_aps), 4),
            },
            "per_query_results": [
                {
                    "query_id": r.query_id,
                    "query_text": r.query_text[:50],
                    "precision@10": r.metrics.precision_at_k,
                    "recall@10": r.metrics.recall_at_k,
                    "f1@10": r.metrics.f1_at_k,
                    "ndcg": r.metrics.ndcg,
                    "mrr": r.metrics.mrr,
                    "analysis": r.analysis,
                }
                for r in results
            ],
            "top_performing_queries": [],
            "worst_performing_queries": [],
        }

        # 排序找出最好/最差
        sorted_by_ap = sorted(zip(all_aps, results), key=lambda x: x[0], reverse=True)
        report["top_performing_queries"] = [
            {"query_id": r.query_id, "ap": round(ap, 4)}
            for ap, r in sorted_by_ap[:3]
        ]
        report["worst_performing_queries"] = [
            {"query_id": r.query_id, "ap": round(ap, 4)}
            for ap, r in sorted_by_ap[-3:]
        ]

        return report

    def _calculate_ap(self, docs: List[RetrievedDocument], ground_truth: set) -> float:
        """计算Average Precision"""
        hits = 0
        sum_precisions = 0.0

        for i, doc in enumerate(docs):
            if doc.doc_id in ground_truth:
                hits += 1
                precision_at_i = hits / (i + 1)
                sum_precisions += precision_at_i

        ap = sum_precisions / len(ground_truth) if ground_truth else 0.0
        return ap

    def _calculate_ndcg(self, docs: List[RetrievedDocument], ground_truth: set) -> float:
        """计算NDCG@K"""
        k = len(docs)
        if k == 0:
            return 0.0

        # DCG
        dcg = 0.0
        for i, doc in enumerate(docs):
            relevance = 1.0 if doc.doc_id in ground_truth else 0.0
            dcg += relevance / math.log2(i + 2)  # i+2 because i is 0-indexed

        # IDCG (ideal DCG)
        num_relevant = min(len(ground_truth), k)
        idcg = sum(1.0 / math.log2(i + 2) for i in range(num_relevant)) if num_relevant > 0 else 0.0

        ndcg = dcg / idcg if idcg > 0 else 0.0
        return ndcg

    def _calculate_mrr(self, docs: List[RetrievedDocument], ground_truth: set) -> float:
        """计算Mean Reciprocal Rank"""
        for i, doc in enumerate(docs):
            if doc.doc_id in ground_truth:
                return 1.0 / (i + 1)
        return 0.0

    def _generate_analysis(
        self,
        query: RetrievalQuery,
        docs: List[RetrievedDocument],
        metrics: RetrievalMetrics,
    ) -> str:
        """生成分析文本"""
        relevant_count = sum(1 for d in docs if d.doc_id in set(query.ground_truth_ids))

        analysis = f"检索查询 '{query.query_text[:30]}...' "
        analysis += f"返回 {len(docs)} 篇文档，其中 {relevant_count} 篇相关。"

        if metrics.precision_at_k >= 0.7:
            analysis += " 精确率较高。"
        elif metrics.precision_at_k >= 0.4:
            analysis += " 精确率一般，存在一定噪声。"
        else:
            analysis += " 精确率较低，检索结果相关性不足。"

        if metrics.recall_at_k >= 0.8:
            analysis += " 召回率优秀。"
        elif metrics.recall_at_k >= 0.5:
            analysis += " 召回率一般。"
        else:
            analysis += " 召回率低，可能遗漏重要文献。"

        if metrics.ndcg >= 0.8:
            analysis += " 排序质量良好。"
        elif metrics.ndcg >= 0.5:
            analysis += " 排序质量中等。"
        else:
            analysis += " 排序质量较差，相关文献排名靠后。"

        return analysis

    def generate_mock_retrieval(
        self,
        query: RetrievalQuery,
        system_name: str = "ResearchForge",
    ) -> List[RetrievedDocument]:
        """
        生成模拟检索结果（用于测试）

        基于查询主题词生成模拟文档
        """
        import random
        random.seed(hash(query.query_id) % 2**32)

        topic_keywords = query.query_text.split()[:5]

        mock_papers = [
            {
                "doc_id": f"paper_{i}",
                "title": f"关于{'/'.join(topic_keywords[:2])}的{'研究' if i%2 else '进展'}_{2024-i}",
                "abstract": f"本文研究了{query.query_text[:50]}，通过实验验证了方法的有效性。结果表明该方法在性能指标上提升了{i*5}%。",
            }
            for i in range(15)
        ]

        # 打分排序
        for paper in mock_papers:
            score = random.uniform(0.3, 0.95)
            # 注入一些确定相关的（ground truth）
            if paper["doc_id"] in query.ground_truth_ids:
                score = 0.85 + random.uniform(0, 0.15)
            paper["score"] = score

        mock_papers.sort(key=lambda x: x["score"], reverse=True)

        retrieved = []
        for rank, paper in enumerate(mock_papers[:10]):
            retrieved.append(RetrievedDocument(
                doc_id=paper["doc_id"],
                title=paper["title"],
                abstract=paper["abstract"],
                score=round(paper["score"], 4),
                rank=rank + 1,
                relevance_level=RelevanceLevel.HIGHLY_RELEVANT if paper["doc_id"] in set(query.ground_truth_ids) else RelevanceLevel.RELEVANT,
            ))

        return retrieved


# =============================================================================
# 批量检索评估
# =============================================================================

class RetrievalEvalRunner:
    """检索评估运行器"""

    def __init__(self):
        self.evaluator = RetrievalAccuracyEvaluator()

    def run_evaluation(
        self,
        test_queries: List[RetrievalQuery],
        output_dir: str = "D:/ZYY Project/ResearchForge/backend/eval",
    ) -> Dict[str, Any]:
        """
        运行完整检索评估

        Args:
            test_queries: 测试查询列表
            output_dir: 输出目录

        Returns:
            评估报告
        """
        print(f"[RetrievalEval] Running evaluation with {len(test_queries)} queries...")

        # 使用模拟检索函数
        def mock_retrieval(query):
            return self.evaluator.generate_mock_retrieval(query, "ResearchForge")

        # 批量评估
        report = self.evaluator.evaluate_batch(test_queries, mock_retrieval)

        # 保存报告
        import os
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "retrieval_eval_report.json")

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"[RetrievalEval] Report saved to {output_path}")

        return report

    def get_standard_test_queries(self) -> List[RetrievalQuery]:
        """获取标准测试查询集"""
        return [
            RetrievalQuery(
                query_id="BAT-001",
                query_text="锂离子电池NCM811正极材料倍率性能优化策略",
                ground_truth_ids=["paper_0", "paper_3", "paper_7"],
                domain="battery",
            ),
            RetrievalQuery(
                query_id="BAT-002",
                query_text="固态电解质界面稳定性锂金属负极",
                ground_truth_ids=["paper_1", "paper_5", "paper_9"],
                domain="battery",
            ),
            RetrievalQuery(
                query_id="CAT-001",
                query_text="氢气析出反应催化剂活性和稳定性",
                ground_truth_ids=["paper_2", "paper_6"],
                domain="catalysis",
            ),
            RetrievalQuery(
                query_id="MAT-001",
                query_text="钙钛矿太阳能电池稳定性提升方法",
                ground_truth_ids=["paper_0", "paper_4", "paper_8"],
                domain="materials",
            ),
            RetrievalQuery(
                query_id="MAT-002",
                query_text="高熵合金力学性能和变形机制",
                ground_truth_ids=["paper_2", "paper_7", "paper_10"],
                domain="materials",
            ),
        ]


# =============================================================================
# 入口
# =============================================================================

def run_retrieval_evaluation():
    """运行文献检索评估示例"""
    runner = RetrievalEvalRunner()
    queries = runner.get_standard_test_queries()
    report = runner.run_evaluation(queries)

    print("\n" + "=" * 60)
    print("RETRIEVAL EVALUATION RESULTS")
    print("=" * 60)
    print(f"\nTotal queries: {report['summary']['total_queries']}")
    print(f"Mean Precision@10: {report['summary']['mean_precision@10']:.4f}")
    print(f"Mean Recall@10: {report['summary']['mean_recall@10']:.4f}")
    print(f"Mean F1@10: {report['summary']['mean_f1@10']:.4f}")
    print(f"Mean NDCG: {report['summary']['mean_ndcg']:.4f}")
    print(f"Mean MRR: {report['summary']['mean_mrr']:.4f}")
    print(f"Mean Average Precision: {report['summary']['mean_average_precision']:.4f}")

    print("\nTop performing queries:")
    for q in report["top_performing_queries"]:
        print(f"  {q['query_id']}: AP={q['ap']:.4f}")

    print("\nWorst performing queries:")
    for q in report["worst_performing_queries"]:
        print(f"  {q['query_id']}: AP={q['ap']:.4f}")

    return report


if __name__ == "__main__":
    run_retrieval_evaluation()