"""
ResearchForge Smoke Tests
=========================
冒烟测试: 验证核心模块可导入、基础数据结构正确、关键逻辑可执行。
运行方式: cd backend && pytest ../tests/test_smoke.py -v
"""

import sys
import os
import asyncio
from pathlib import Path

# 确保 backend/ 在 sys.path 中
_backend = Path(__file__).resolve().parent.parent / "backend"
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

import pytest


# ---------------------------------------------------------------------------
# Module Import Tests
# ---------------------------------------------------------------------------

class TestImports:
    """验证所有核心模块可正常导入"""

    def test_import_main(self):
        from app.main import app
        assert app.title == "ResearchForge"

    def test_import_hypothesis_engine(self):
        from app.core.hypothesis_engine import (
            HypothesisEngine, Hypothesis, Variable,
            VerificationMethod, HypothesisQualityScore,
            KnowledgeGraphChecker, LiteratureKG,
        )
        assert HypothesisEngine is not None

    def test_import_tool_orchestrator(self):
        from app.core.tool_orchestrator import (
            ToolChainOrchestrator, ToolRegistry,
            ToolState, ToolCall, ToolResult,
        )
        assert ToolChainOrchestrator is not None

    def test_import_research_agent(self):
        from app.core.research_agent import ResearchAgent, ResearchTask, AgentConfig
        assert ResearchAgent is not None

    def test_import_lab_automation(self):
        from app.agents.lab_automation import (
            LabAutomationAgent, DoEEngine, FMEAEngine,
            DoEFactor, DoEMethod, ExperimentAnalysisEngine,
        )
        assert LabAutomationAgent is not None

    def test_import_material_generator(self):
        from app.agents.material_generator import MaterialGenAgent, MaterialCandidate
        assert MaterialGenAgent is not None

    def test_import_patent_miner(self):
        from app.agents.patent_miner import PatentMinerAgent, PriorArtItem, PatentablePoint
        assert PatentMinerAgent is not None

    def test_import_project_ingestor(self):
        from app.services.project_ingestor import ingest_project, ProjectDigest
        assert ingest_project is not None

    def test_import_shield_modules(self):
        from app.shield.agent_behavior_graph import AgentBehaviorGraph, BehaviorNode
        from app.shield.v3_audit_logger import V3AuditLogger
        assert AgentBehaviorGraph is not None
        assert V3AuditLogger is not None

    def test_import_routes(self):
        from app.api.routes import router
        assert router.prefix == "/api/v1"


# ---------------------------------------------------------------------------
# Data Structure Tests
# ---------------------------------------------------------------------------

class TestHypothesisStructures:
    """假设引擎数据结构基本验证"""

    def test_variable_creation(self):
        from app.core.hypothesis_engine import Variable
        v = Variable(name="temperature", type="independent", unit="°C", range_min=20, range_max=800)
        assert v.name == "temperature"
        assert v.type == "independent"
        assert v.unit == "°C"

    def test_hypothesis_creation(self):
        from app.core.hypothesis_engine import Hypothesis
        h = Hypothesis(id="h1", statement="test hypothesis", confidence=0.8)
        assert h.id == "h1"
        assert h.statement == "test hypothesis"
        assert h.confidence == 0.8
        assert h.variables == []
        assert h.evidence_links == []

    def test_quality_score_defaults(self):
        from app.core.hypothesis_engine import HypothesisQualityScore
        qs = HypothesisQualityScore()
        assert qs.novelty == 0.0
        assert qs.overall == 0.0

    def test_knowledge_graph_checker(self):
        from app.core.hypothesis_engine import KnowledgeGraphChecker, Hypothesis
        checker = KnowledgeGraphChecker()
        h = Hypothesis(id="h1", statement="正常假设")
        result = checker.check(h)
        assert result.passed is True

    def test_physics_violation_detected(self):
        from app.core.hypothesis_engine import KnowledgeGraphChecker, Hypothesis
        checker = KnowledgeGraphChecker()
        h = Hypothesis(id="h2", statement="违反能量守恒的永动机")
        result = checker.check(h)
        assert result.passed is False
        assert "energy" in result.violation_type.lower() or "violation" in result.violation_message.lower()


class TestToolOrchestratorStructures:
    """工具编排器数据结构验证"""

    def test_tool_call_creation(self):
        from app.core.tool_orchestrator import ToolCall
        tc = ToolCall(tool_name="code_executor", inputs={"code": "1+1"}, output_key="result")
        assert tc.tool_name == "code_executor"
        assert tc.timeout == 30.0
        assert tc.max_retries == 3

    def test_tool_registry(self):
        from app.core.tool_orchestrator import ToolRegistry
        registry = ToolRegistry()
        tools = registry.list_tools()
        assert "code_executor" in tools
        assert "simulator" in tools
        assert "visualizer" in tools
        assert "literature_retriever" in tools

    def test_tool_state_enum(self):
        from app.core.tool_orchestrator import ToolState
        assert ToolState.READY.value == "ready"
        assert ToolState.DONE.value == "done"
        assert ToolState.FAILED.value == "failed"


class TestLabAutomationStructures:
    """实验自动化数据结构验证"""

    def test_doe_factor_creation(self):
        from app.agents.lab_automation import DoEFactor
        f = DoEFactor(name="温度", levels=[750, 800, 850], unit="°C", real_min=700, real_max=900)
        assert f.name == "温度"
        assert len(f.levels) == 3

    def test_failure_mode_rpn(self):
        from app.agents.lab_automation import FailureMode
        fm = FailureMode(
            mode_id="FM-01", failure_mode="test", potential_effect="test",
            potential_cause="test", severity=7, occurrence=4, detection=3,
        )
        assert fm.rpn == 7 * 4 * 3  # 84


# ---------------------------------------------------------------------------
# Functional Tests (no network, no external dependencies)
# ---------------------------------------------------------------------------

class TestHypothesisEngineFunctional:
    """假设引擎功能性测试"""

    def test_generate_hypotheses_sync(self):
        from app.core.hypothesis_engine import HypothesisEngine
        engine = HypothesisEngine()
        hypotheses = engine.generate_sync("如何提高锂电池倍率性能？", num_hypotheses=2)
        assert len(hypotheses) >= 1
        for h in hypotheses:
            assert h.statement
            assert h.confidence > 0
            assert h.quality_score is not None

    @pytest.mark.asyncio
    async def test_generate_hypotheses_async(self):
        from app.core.hypothesis_engine import HypothesisEngine
        engine = HypothesisEngine()
        hypotheses = await engine.generate("如何提高锂电池倍率性能？", num_hypotheses=3, build_kg=False)
        assert len(hypotheses) >= 1
        for h in hypotheses:
            assert len(h.variables) > 0
            assert len(h.verification_methods) > 0

    def test_quality_evaluator(self):
        from app.core.hypothesis_engine import (
            HypothesisQualityEvaluator, Hypothesis, Variable, VerificationMethod,
        )
        h = Hypothesis(
            id="h_eval", statement="增加X浓度导致Y转化率提高",
            variables=[
                Variable(name="X", type="independent"),
                Variable(name="Y", type="dependent"),
            ],
            verification_methods=[
                VerificationMethod(method_type="实验", description="test", statistical_test="t-test"),
            ],
        )
        evaluator = HypothesisQualityEvaluator()
        score = evaluator.evaluate(h)
        assert 0.0 <= score.overall <= 1.0
        assert 0.0 <= score.novelty <= 1.0
        assert 0.0 <= score.verifiability <= 1.0


class TestToolOrchestratorFunctional:
    """工具编排器功能性测试"""

    def test_plan_generation(self):
        from app.core.tool_orchestrator import ToolChainOrchestrator
        tco = ToolChainOrchestrator()
        plan = tco.plan("需要代码计算和仿真模型", ["code_executor", "simulator", "visualizer"])
        assert len(plan) >= 2
        tool_names = [p.tool_name for p in plan]
        assert "code_executor" in tool_names

    def test_topological_sort(self):
        from app.core.tool_orchestrator import ToolChainOrchestrator, ToolCall
        tco = ToolChainOrchestrator()
        calls = [
            ToolCall(tool_name="visualizer", inputs={}, dependencies=["simulation_data"], output_key="chart"),
            ToolCall(tool_name="code_executor", inputs={}, dependencies=[], output_key="code_result"),
            ToolCall(tool_name="simulator", inputs={}, dependencies=["code_result"], output_key="simulation_data"),
        ]
        sorted_calls = tco.topological_sort(calls)
        keys = [c.output_key for c in sorted_calls]
        assert keys.index("code_result") < keys.index("simulation_data")
        assert keys.index("simulation_data") < keys.index("chart")

    @pytest.mark.asyncio
    async def test_execute_plan(self):
        from app.core.tool_orchestrator import ToolChainOrchestrator, ToolCall
        tco = ToolChainOrchestrator()
        plan = [
            ToolCall(tool_name="code_executor", inputs={"code": "1+1", "params": {}}, output_key="result"),
        ]
        results = await tco.execute_plan(plan)
        assert len(results) == 1
        assert results[0].success is True

    def test_reset(self):
        from app.core.tool_orchestrator import ToolChainOrchestrator, ToolState
        tco = ToolChainOrchestrator()
        tco.state = ToolState.DONE
        tco.reset()
        assert tco.state == ToolState.READY
        assert len(tco.execution_log) == 0


class TestLabAutomationFunctional:
    """实验自动化功能性测试"""

    def test_design_experiment(self):
        from app.agents.lab_automation import LabAutomationAgent
        agent = LabAutomationAgent()
        result = agent.design_experiment("h_test_001", {"type": "synthesis"})
        assert result["experiment_id"].startswith("EXP-")
        assert len(result["steps"]) > 0
        assert "fmea_report" in result

    def test_doe_orthogonal(self):
        from app.agents.lab_automation import LabAutomationAgent, DoEFactor
        agent = LabAutomationAgent()
        factors = [
            DoEFactor("温度", [750, 800, 850], "°C", real_min=700, real_max=900),
            DoEFactor("时间", [8, 12, 16], "h", real_min=4, real_max=20),
        ]
        result = agent.design_doe("h_test_002", factors, method="orthogonal")
        assert result["design_type"] == "orthogonal"
        assert result["run_count"] > 0

    def test_doe_rsm(self):
        from app.agents.lab_automation import LabAutomationAgent, DoEFactor
        agent = LabAutomationAgent()
        factors = [
            DoEFactor("temp", [0, 1], "°C", real_min=700, real_max=900),
            DoEFactor("time", [0, 1], "h", real_min=4, real_max=20),
        ]
        result = agent.design_doe("h_test_003", factors, method="rsm")
        assert result["design_type"] == "response_surface"
        assert result["run_count"] >= 9  # 2^2 + 2*2 + 5 center

    def test_fmea_generation(self):
        from app.agents.lab_automation import LabAutomationAgent
        agent = LabAutomationAgent()
        fmea = agent.generate_fmea("synthesis", ["配料", "混合", "烧结"])
        assert len(fmea["failure_modes"]) > 0
        assert all(fm["rpn"] > 0 for fm in fmea["failure_modes"])
        assert fmea["top_risks"]

    def test_run_simulation(self):
        from app.agents.lab_automation import LabAutomationAgent
        agent = LabAutomationAgent()
        result = agent.run_simulation({"experiment_id": "EXP-TEST-001"})
        assert result["status"] == "completed"
        assert result["simulation"] is True
        assert "results" in result

    def test_analyze_results(self):
        from app.agents.lab_automation import LabAutomationAgent
        agent = LabAutomationAgent()
        design_matrix = [
            {"temp": 750, "time": 8},
            {"temp": 800, "time": 12},
            {"temp": 850, "time": 16},
        ]
        response_data = {"yield": [0.82, 0.90, 0.87]}
        result = agent.analyze_results(design_matrix, response_data)
        assert "descriptive_statistics" in result
        assert "model_fitting" in result
        assert result["model_fitting"]["r_squared"] > 0


class TestMaterialGenFunctional:
    """材料生成器功能性测试"""

    def test_generate_materials(self):
        from app.agents.material_generator import MaterialGenAgent
        agent = MaterialGenAgent()
        result = agent.generate("energy_density", {"max_cost": 200})
        assert result["count"] > 0
        assert len(result["candidates"]) > 0
        for c in result["candidates"]:
            assert c["candidate_id"].startswith("MAT-")
            assert c["confidence"] > 0

    def test_optimize_material(self):
        from app.agents.material_generator import MaterialGenAgent
        agent = MaterialGenAgent()
        base = {"LiNi0.8Co0.1Mn0.1O2": 0.8, "LiCoO2": 0.2}
        result = agent.optimize(base, "energy_density +15%")
        assert result["original_formula"] == base
        assert result["confidence"] > 0


class TestPatentMinerFunctional:
    """专利挖掘功能性测试"""

    def test_mine_patents(self):
        from app.agents.patent_miner import PatentMinerAgent
        agent = PatentMinerAgent()
        result = agent.mine("multi-agent experiment automation with knowledge graph")
        assert "prior_art" in result
        assert "gaps" in result
        assert "patentable_points" in result
        assert result["summary"]

    def test_gap_analysis(self):
        from app.agents.patent_miner import PatentMinerAgent
        agent = PatentMinerAgent()
        result = agent.mine("experiment 闭环 causal reasoning 知识图谱 multi-agent")
        assert len(result["gaps"]) > 0


class TestAuditLogger:
    """审计日志功能测试"""

    def test_log_and_export(self):
        from app.shield.v3_audit_logger import V3AuditLogger
        logger = V3AuditLogger()
        rec = logger.log(event="TEST_EVENT", session_id="sess_001", data={"key": "value"})
        assert rec["event"] == "TEST_EVENT"
        assert rec["record_hash"] != "0" * 64
        chain = logger.export_chain()
        assert chain["total_records"] == 1

    def test_chain_integrity(self):
        from app.shield.v3_audit_logger import V3AuditLogger
        logger = V3AuditLogger()
        logger.log("E1", "s1", {})
        logger.log("E2", "s1", {})
        logger.log("E3", "s1", {})
        assert len(logger.records) == 3
        # 每条记录的 previous_hash 应该是前一条的 record_hash
        assert logger.records[1]["previous_hash"] == logger.records[0]["record_hash"]
        assert logger.records[2]["previous_hash"] == logger.records[1]["record_hash"]


# ---------------------------------------------------------------------------
# FastAPI App Tests (using TestClient)
# ---------------------------------------------------------------------------

class TestFastAPIEndpoints:
    """FastAPI 端点冒烟测试"""

    @pytest.fixture
    def client(self):
        from fastapi.testclient import TestClient
        from app.main import app
        return TestClient(app)

    def test_health_endpoint(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ResearchForge"

    def test_list_domains(self, client):
        resp = client.get("/api/v1/research/domains")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["data"]["count"] == 5

    def test_patentable_points(self, client):
        resp = client.get("/api/v1/research/patentable-points")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

    def test_literature_gaps(self, client):
        resp = client.get("/api/v1/research/literature_gaps")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["data"]["count"] > 0

    def test_priorart_endpoint(self, client):
        resp = client.post("/api/v1/research/priorart", json={
            "tech_description": "multi-agent experiment automation",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

    def test_material_generate_endpoint(self, client):
        resp = client.post("/api/v1/research/material/generate", json={
            "target_property": "energy_density",
            "constraints": {},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

    def test_experiment_design_endpoint(self, client):
        resp = client.post("/api/v1/research/experiment/design", json={
            "hypothesis_id": "h_test_001",
            "hypothesis_context": {"type": "synthesis"},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"

    def test_validate_hypothesis_endpoint(self, client):
        resp = client.post("/api/v1/research/validate_hypothesis", json={
            "hypothesis": "test hypothesis",
            "prior_evidence": [{"support_strength": 0.7}],
            "new_evidence": {"support_strength": 0.8},
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert "posterior_probability" in data["data"]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
