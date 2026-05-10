# Test script for ResearchForge SCI upgrade
import sys
sys.path.insert(0, '.')

print("=" * 60)
print("ResearchForge SCI-Level Upgrade Test")
print("=" * 60)

# Test 1: Hypothesis Engine
print("\n[Test 1] Hypothesis Engine (hypothesis_engine.py)")
from app.core.hypothesis_engine import HypothesisEngine, Variable, VerificationMethod, Hypothesis
import asyncio

engine = HypothesisEngine()
hypotheses = asyncio.get_event_loop().run_until_complete(
    engine.generate('如何提高锂电池NCM811正极材料的倍率性能？', num_hypotheses=2, build_kg=False)
)
print(f"  Generated {len(hypotheses)} hypotheses")
for h in hypotheses:
    print(f"  - {h.id}: {h.statement[:40]}...")
    print(f"    confidence={h.confidence:.3f}, quality_score={h.quality_score.overall:.3f}")
    print(f"    variables={len(h.variables)}, verification_methods={len(h.verification_methods)}")

# Test 2: Lab Automation (DoE + FMEA)
print("\n[Test 2] Lab Automation Agent (lab_automation.py)")
from app.agents.lab_automation import LabAutomationAgent, DoEFactor, DoEMethod

agent = LabAutomationAgent()

factors = [
    DoEFactor('温度', [750, 800, 850], '°C', real_min=700, real_max=900),
    DoEFactor('时间', [8, 12, 16], 'h', real_min=4, real_max=20),
]
doe_result = agent.design_doe('h_test_001', factors, method='orthogonal')
print(f"  DoE design: {doe_result['design_type']}, runs={doe_result['run_count']}")
print(f"  Total runs with replicates: {doe_result['total_runs_with_replicates']}")
print(f"  Estimated cost: {doe_result['estimated_cost_aud']} AUD")

fmea = agent.generate_fmea('synthesis', ['配料', '混合', '烧结', '粉碎', '表征'])
print(f"  FMEA: {len(fmea['failure_modes'])} failure modes")
print(f"  Critical items: {fmea['critical_items']}")
print(f"  Top risk RPN: {fmea['top_risks'][0]['rpn']}")

# Test 3: Benchmark Suite
print("\n[Test 3] Benchmark Suite (experiments/benchmark_suite.py)")
from experiments.benchmark_suite import run_benchmark
benchmark = run_benchmark()
print(f"  ResearchForge rank: #{benchmark.researchforge_position}")
for r in benchmark.results:
    print(f"  #{r.rank} {r.system.value}: {r.overall_score:.4f}")

# Test 4: Ablation Study
print("\n[Test 4] Ablation Study (experiments/ablation_study.py)")
from experiments.ablation_study import run_ablation_study
ablation = run_ablation_study()
print(f"  Full system score: {ablation.full_system_score:.4f}")
for name, contrib in sorted(ablation.module_contributions.items(), key=lambda x: x[1], reverse=True):
    print(f"  {name}: {contrib:.4f}")

print("\n" + "=" * 60)
print("All tests passed!")
print("=" * 60)