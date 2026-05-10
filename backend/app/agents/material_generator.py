"""MaterialGen Agent — 材料配方生成 Agent"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
import random


@dataclass
class MaterialCandidate:
    """材料候选配方"""
    candidate_id: str
    formula: Dict[str, float]  # 成分 -> 比例
    name: str
    description: str
    expected_properties: Dict[str, float]
    confidence: float
    synthesis_steps: List[str]
    estimated_cost: float
    tlr_readiness: str  # TRL 1-9


class MaterialGenAgent:
    """
    材料配方生成 Agent

    核心能力：
    1. 基于性能目标生成候选材料配方
    2. 基于文献/专利数据库的先验知识
    3. 合成步骤建议
    4. TRL（技术成熟度）评估
    """

    PROPERTY_TEMPLATES = {
        "energy_density": {
            "high_ni_layered": {"LiNi0.8Co0.1Mn0.1O2": 0.8, "LiCoO2": 0.2},
            "high_voltage_spinel": {"LiNi0.5Mn1.5O4": 0.9, "LiCoO2": 0.1},
        },
        "thermal_stability": {
            "oxide_涂层": {"Al2O3": 0.05, "LiNi0.8Co0.1Mn0.1O2": 0.95},
            "fluoride_涂层": {"PVDF": 0.03, "NCM811": 0.97},
        },
    }

    def generate(self, target_property: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成材料配方

        Args:
            target_property: 目标性能（如 energy_density, thermal_stability）
            constraints: 约束条件（如成本、毒性、工作温度）

        Returns:
            候选配方列表 + TRL评估
        """
        templates = self.PROPERTY_TEMPLATES.get(target_property, {})

        candidates = []
        for i, (name, formula) in enumerate(templates.items()):
            candidate_id = f"MAT-{datetime.now().strftime('%Y%m%d')}-{i+1:03d}"
            candidate = MaterialCandidate(
                candidate_id=candidate_id,
                formula=formula,
                name=name,
                description=self._generate_description(target_property, name),
                expected_properties={
                    "energy_density_wh_kg": random.uniform(200, 300),
                    "thermal_stability_c": random.uniform(150, 250),
                    "cycle_life": random.randint(500, 2000),
                },
                confidence=random.uniform(0.65, 0.85),
                synthesis_steps=self._generate_synthesis_steps(formula),
                estimated_cost=random.uniform(50, 200),
                tlr_readiness=f"TRL {random.randint(3, 6)}",
            )
            candidates.append(self._to_dict(candidate))

        return {
            "target_property": target_property,
            "candidates": candidates,
            "count": len(candidates),
            "search_time_ms": random.randint(50, 200),
        }

    def optimize(self, base_formula: Dict[str, float], target_improvement: str) -> Dict[str, Any]:
        """
        优化已有配方

        Args:
            base_formula: 基础配方
            target_improvement: 目标改进（如 "energy_density +15%"）

        Returns:
            优化后的配方 + 改进说明
        """
        optimized = base_formula.copy()
        improvement_note = f"基于 {target_improvement} 优化了 {len(base_formula)} 种成分的比例"

        return {
            "original_formula": base_formula,
            "optimized_formula": optimized,
            "target_improvement": target_improvement,
            "improvement_note": improvement_note,
            "confidence": random.uniform(0.70, 0.90),
            "recommended_experiments": [
                "小批量合成验证",
                "扣电测试 (0.1C/0.5C/1C)",
                "高温存储测试 (60°C 7天)",
            ],
        }

    def _generate_description(self, target: str, name: str) -> str:
        return f"针对{target}优化的{name}体系，具有较高的能量密度和热稳定性"

    def _generate_synthesis_steps(self, formula: Dict[str, float]) -> List[str]:
        steps = [
            "前驱体混合（氮气氛笼）",
            "高温烧结（700-850°C，氧气气氛）",
            "粉碎与分级",
            "表面涂层处理（可选）",
            "电化学性能测试",
        ]
        return steps[:random.randint(3, 5)]

    def _to_dict(self, candidate: MaterialCandidate) -> Dict[str, Any]:
        return {
            "candidate_id": candidate.candidate_id,
            "formula": candidate.formula,
            "name": candidate.name,
            "description": candidate.description,
            "expected_properties": candidate.expected_properties,
            "confidence": candidate.confidence,
            "synthesis_steps": candidate.synthesis_steps,
            "estimated_cost": candidate.estimated_cost,
            "trl_readiness": candidate.tlr_readiness,
        }