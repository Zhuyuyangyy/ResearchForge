# ResearchForge — 闭环科研自动化多智能体系统

> **SCI Innovation**: 基于 OpenClaw + ASF-BGT Framework + CrewAI + AgentShield V3 构建的科研自动化平台
>
> 实现"读文献 → 提出假设 → 设计实验 → 仿真验证 → 迭代修正"的全流程闭环。

---

## Table of Contents

- [Overview](#overview)
- [Key Innovations](#key-innovations)
- [System Architecture](#system-architecture)
- [Core Components](#core-components)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Modules](#modules)
- [Configuration](#configuration)
- [Technical Details](#technical-details)
- [Citation](#citation)

---

## Overview

ResearchForge is an academic research system that implements a **closed-loop research automation multi-agent framework**. It enables AI agents to autonomously execute the full research cycle: literature review, hypothesis generation, experimental design, simulation verification, and iterative refinement.

### Core Technology Stack

| Layer | Component | Function |
|-------|-----------|----------|
| Behavioral Governance | ASF-BGT Framework | World + BranchTree + Simulator + CounterfactualEngine |
| Behavioral Audit | AgentShield V3 | Multi-agent collaboration security and risk governance |
| Agent Orchestration | CrewAI Multi-Agent Core | HGE + LCC + TCO + FRE |
| Domain Modules | PatentMiner + LabAutomation + MaterialGen + KnowledgeGraph | Vertical domain expertise |

### System Positioning

- **OpenClaw** = Multi-channel access + Multi-agent routing + Edge execution + Canvas visualization
- **ResearchForge** = OpenClaw concretely implemented for the research automation scenario

---

## Key Innovations

### 1. Hypothesis Engine (HGE)

**Structured Hypothesis Generation** with Variable-Hypothesis-VerificationMethod three-part format:

```python
class Hypothesis:
    id: str
    statement: str                    # Natural language description
    variables: List[Variable]          # independent/dependent/control/mediator/moderator
    relations: List[str]               # e.g., ["X ↑ → Y ↓", "dose-effect relationship"]
    constraints: List[str]             # Boundary conditions
    quality_score: HypothesisQualityScore  # novelty/verifiability/effect_size/consistency
    verification_methods: List[VerificationMethod]  # Statistical tests, sample sizes
    evidence_links: List[EvidenceLink] # Literature evidence associations
```

**Quality Scoring System**:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Novelty | 30% | How novel is the hypothesis vs. existing literature |
| Verifiability | 30% | Can it be tested experimentally? |
| Effect Size | 20% | Expected magnitude of the effect |
| Consistency | 20% | Consistency with known physics laws and prior results |

### 2. DoE Optimization (Design of Experiments)

Integrated experimental design optimization using multiple methods:

| Method | Use Case | Characteristics |
|--------|----------|-----------------|
| Orthogonal (L9/L18) | Screening | Find key factors from many candidates |
| RSM (CCD/BBD) | Response Surface | Model nonlinear relationships |
| LHS (Latin Hypercube) | Sampling | Maximize information coverage |
| Taguchi | Robustness | Minimize sensitivity to noise |
| Full Factorial | Comprehensive | All factor-level combinations |

```python
class DoEFactor:
    name: str           # Factor name
    unit: str           # Physical unit
    levels: List[float] # Factor levels
    type: str           # "continuous" / "discrete"

class DoEDesign:
    method: DoEMethod
    factors: List[DoEFactor]
    design_matrix: List[Dict[str, float]]  # Experimental conditions
    suggested_replicates: int
```

### 3. FMEA Failure Mode and Effects Analysis

Knowledge-driven risk assessment engine:

```python
class FailureMode:
    mode_id: str           # e.g., "FM-01-Y"
    failure_mode: str      # What can go wrong
    potential_effect: str  # Impact on results
    potential_cause: str   # Root cause hypothesis
    severity: int          # S (1-10)
    occurrence: int        # O (1-10)
    detection: int         # D (1-10)
    rpn: int               # RPN = S × O × D (risk priority number)
```

**FMEA Templates** by experiment type:

```
synthesis:
  - FM-01-Y: 产率下降 (Temperature control deviation)
  - FM-02-P: 纯度不达标 (Raw material contamination)
  - FM-03-T: 粒度分布宽 (Improper ball milling parameters)

characterization:
  - FM-04-S: 样品损坏 (Poor sample preparation)
  - FM-05-D: 仪器噪声大 (Instrument calibration issues)

performance_test:
  - FM-06-C: 容量衰减快 (Electrolyte decomposition)
  - FM-07-E: 倍率性能差 (Kinetic bottleneck)
```

### 4. Multi-Agent Collaboration Loop

```
+------------------------------------------------------------------------------+
|                    ResearchForge Research Loop                                |
+------------------------------------------------------------------------------+

    +------------------+      +-------------------+      +--------------------+
    |  Hypothesis      |      |  Tool Chain       |      |  Feedback          |
    |  Generation (HGE) | ---> |  Execution (TCO)  | ---> |  Refinement (FRE)  |
    +------------------+      +-------------------+      +--------------------+
           ^                                                        |
           |                                                        v
    +------+------+      +-------------------+      +--------------------+
    |  Literature   |      |  Experiment       |      |  KG Constraint    |
    |  Knowledge    | <--- |  Results          |      |  Check (LCC)      |
    |  Graph         |      |  Analysis         |      |  Physics Laws     |
    +---------------+      +-------------------+      +--------------------+
           ^                                                        |
           |                                                        |
           +----------------- Iterative Refinement -----------------+
```

**Research Agent Core Loop (research_agent.py)**:

```python
async def run_task(self, task: ResearchTask) -> Dict[str, Any]:
    # Phase 1: Hypothesis Generation
    hypotheses = await self._generate_hypotheses(task)

    # Phase 2: Tool Chain Execution
    tool_results = await self._execute_tools(task, hypotheses)

    # Phase 3: Feedback Refinement (FRE)
    refined_hypotheses = await self._refine_hypotheses(task, hypotheses, tool_results)

    # Phase 4: Knowledge Graph Constraint Check (LCC)
    final_hypotheses = self._kg_constraint_check(refined_hypotheses)

    return {
        "task_id": task.task_id,
        "status": "completed",
        "hypotheses": [h.__dict__ for h in final_hypotheses],
        "tool_results": tool_results,
    }
```

### 5. V3Shield Behavior Audit Engine

Multi-agent collaboration safety through **future behavior chain** risk projection:

```python
class V3ShieldEngine:
    # Governance decision thresholds
    ALLOW_THRESHOLD = 0.70
    REVIEW_THRESHOLD = 0.90
    BLOCK_THRESHOLD = 0.90

    def process_tool_call(
        self,
        agent_id: str,
        tool_name: str,
        params: Dict[str, Any],
        risk_score: float,
        fuse_action: str,
    ) -> Dict[str, Any]:
        # 1. Add to behavior graph
        node = self.behavior_graph.add_tool_call_as_node(...)

        # 2. Generate future branches
        branches = self._generate_future_branches(agent_id, tool_name, risk_score)

        # 3. Governance decision
        gate_result = self._governance_decision(risk_score, branches)

        # 4. Counterfactual What-If analysis
        if self.enable_counterfactual and risk_score >= self.risk_threshold:
            what_if = self._counterfactual_whatif(agent_id, tool_name, risk_score, fuse_action)
```

**Governance Actions**:

| Risk Level | Action | Description |
|------------|--------|-------------|
| < 0.70 | ALLOW | Normal execution |
| 0.70-0.90 | REVIEW | Requires human review |
| >= 0.90 | BLOCK | Direct blocking |

### 6. Counterfactual What-If Engine

BranchTree-based what-if scenario analysis for false positive/negative assessment:

```python
class WhatIfScenario:
    scenario_id: str
    label: str              # e.g., "假设拦截 agent_id.tool_name"
    hypothesis: Dict         # Intervention description
    projected_risk: float    # Risk after intervention
    projected_outcome: Dict  # Expected outcome after block
    comparison_with_baseline: Dict  # delta analysis

# Example:
{
    "scenario_id": "whatif_a1b2c3d4",
    "label": "假设拦截 agent_01.send_email",
    "projected_risk": 0.35,  # 50% reduction from 0.70
    "projected_outcome": {
        "blocked": True,
        "risk_reduced_by": 0.35,
        "agents_affected": ["agent_01"]
    },
    "comparison": {
        "baseline_risk": 0.70,
        "projected_risk_after_block": 0.35,
        "delta": -0.35
    }
}
```

---

## System Architecture

```
+-------------------------------------------------------------------------------------------+
|                              ResearchForge System Architecture                              |
+-------------------------------------------------------------------------------------------+

  +---------------------------+          +---------------------------+
  |     OpenClaw Gateway      |          |     External APIs          |
  |   (Multi-channel Access)  |          |  (Semantic Scholar, ArXiv)|
  +-----------+---------------+          +------------+--------------+
              |                                        |
              v                                        v
  +---------------------------------------------------------------+
  |                    ASF-BGT Framework                          |
  |  +-------------+  +-------------+  +-------------+             |
  |  |    World    |  | BranchTree  |  |  Simulator  |             |
  |  | (Shared     |  | (Branch     |  |  (State     |             |
  |  |  State)     |  |  Evolution) |  |  Projection)|             |
  |  +-------------+  +-------------+  +-------------+             |
  |  +-----------------------------+                              |
  |  |    CounterfactualEngine     |                              |
  |  |    (What-If Analysis)       |                              |
  |  +-----------------------------+                              |
  +---------------------------------------------------------------+
              |
              v
  +---------------------------------------------------------------+
  |              V3ShieldEngine (AgentShield V3)                   |
  |  +---------------------+  +----------------------+            |
  |  |  AgentBehaviorGraph  |  |   V3AuditLogger      |            |
  |  |  (Multi-Agent Risk  |  |   (Audit Trail)       |            |
  |  |   Propagation)      |  |                       |            |
  |  +---------------------+  +----------------------+            |
  +---------------------------------------------------------------+
              |
              v
  +---------------------------------------------------------------+
  |               CrewAI Multi-Agent Core                          |
  |                                                               |
  |  +-------------+  +-------------+  +-------------+             |
  |  |     HGE     |  |     LCC     |  |     TCO     |             |
  |  | Hypothesis  |  |   KG        |  |   Tool      |             |
  |  | Generation  |  |  Constraint |  |  Orchestr.  |             |
  |  |   Engine    |  |   Check     |  |             |             |
  |  +-------------+  +-------------+  +-------------+             |
  |                                                               |
  |  +-------------+                                              |
  |  |     FRE     |                                              |
  |  |  Feedback   |                                              |
  |  | Refinement  |                                              |
  |  +-------------+                                              |
  +---------------------------------------------------------------+
              |
              v
  +---------------------------------------------------------------+
  |                    Domain Modules                              |
  |                                                               |
  |  +----------------+  +------------------+  +----------------+  |
  |  |  PatentMiner   |  |  LabAutomation   |  |  MaterialGen  |  |
  |  |  - Prior-art  |  |  - DoE Engine    |  |  - Formula     |  |
  |  |  - Gap find   |  |  - FMEA Engine   |  |    generation  |  |
  |  |  - Claim dir. |  |  - Exp. Analysis |  |  - Manufact.  |  |
  |  +----------------+  +------------------+  +----------------+  |
  |                                                               |
  |  +----------------+  +------------------+                     |
  |  |  ResearchWriter|  |  KnowledgeGraph   |                     |
  |  |  - Paper draft |  |  - TCM KG        |                     |
  |  |  - Methods     |  |  - Causal推理    |                     |
  |  +----------------+  +------------------+                     |
  +---------------------------------------------------------------+

+-------------------------------------------------------------------------------------------+
|                              Data Flow Example                                             |
+-------------------------------------------------------------------------------------------+

Input: "研究新型锂离子电池正极材料的倍率性能优化"

Step 1: HGE (Hypothesis Generation Engine)
    -> 生成3个结构化假设 (变量-关系-验证方法)
    -> 假设1: "LiCoO2掺杂Al2O3涂层可提高倍率性能"
        Variables: [涂层厚度(自), 放电倍率(因), 温度(控)]
        Verification: 电化学阻抗谱 + 充放电测试

Step 2: DoE Optimization
    -> 正交实验 L9(3^4) 设计
    -> 4因子3水平: 掺杂量、涂层厚度、烧结温度、保温时间

Step 3: FMEA Analysis
    -> 识别关键失效模式: FM-06-C 容量衰减快
    -> RPN = 8×5×3 = 120 (高风险)

Step 4: TCO Tool Chain Execution
    -> 文献检索 (Semantic Scholar API)
    -> 实验执行 (HPC任务提交)
    -> 数据可视化 (Matplotlib)

Step 5: FRE Feedback Refinement
    -> 基于实验结果的假设修正
    -> 迭代优化直到收敛

Step 6: LCC KG Constraint Check
    -> 物理定律一致性检查 (能量守恒、电荷守恒)
    -> 维度一致性检查
    -> 数值合理性检查

Output: 最终验证通过的假设 + 实验报告
```

---

## Core Components

### 1. ResearchAgent (主智能体)

The central orchestrator managing the research loop lifecycle.

**File**: `backend/app/core/research_agent.py`

**AgentConfig**:
```python
@dataclass
class AgentConfig:
    max_iterations: int = 10
    confidence_threshold: float = 0.70
    enable_counterfactual: bool = True
    enable_kg_constraint: bool = True
```

**ResearchTask**:
```python
@dataclass
class ResearchTask:
    task_id: str
    research_question: str
    context: Dict[str, Any] = {}
    status: str = "pending"  # pending, running, completed, failed
    iterations: int = 0
    hypotheses: List[Hypothesis] = []
    tool_results: List[Dict] = []
```

### 2. HypothesisEngine (假设生成引擎)

SCI-level structured hypothesis generation with quality scoring.

**File**: `backend/app/core/hypothesis_engine.py`

**Key Classes**:
- `Variable`: independent / dependent / control / mediator / moderator
- `Hypothesis`: Full hypothesis with structured fields
- `HypothesisQualityScore`: novelty / verifiability / effect_size / consistency
- `VerificationMethod`: statistical_test / sample_size_estimate / expected_effect_size
- `KnowledgeGraphChecker`: Physics law consistency checks

**HypothesisQualityEvaluator**:
```python
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
```

### 3. ToolOrchestrator (工具链编排器)

Topological sorting of tool execution dependencies.

**File**: `backend/app/core/tool_orchestrator.py`

**State Machine**:
```
READY → EXECUTING → VALIDATING → FEEDBACK → REFINE → DONE
```

**ToolRegistry Available Tools**:
- `CodeExecutor`: Python code execution
- `Simulator`: External simulation software invocation
- `Visualizer`: Data visualization (Matplotlib/Plotly)
- `LiteratureRetriever`: Academic literature search

**Kahn Algorithm Topological Sort**:
```python
def topological_sort(self, calls: list[ToolCall]) -> list[ToolCall]:
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
```

### 4. PatentMiner (专利挖掘Agent)

Prior-art mining and patentability analysis.

**File**: `backend/app/agents/patent_miner.py`

**Core Functions**:
1. **Triplet Prior-Art Mining**: Patent / Paper / Product sources
2. **Patentable Point Identification**: Novelty, inventive step, technical effect assessment
3. **Technology Gap Analysis**: Automatic discovery of domain gaps
4. **Claim Direction**: Claim writing suggestions

**PriorArtItem**:
```python
@dataclass
class PriorArtItem:
    type: str              # patent / paper / product
    title: str
    source: str
    date: str
    key_claims: list[str]
    relevance_score: float  # 0.0 - 1.0
    gap_description: str
```

**Gap Analysis Examples**:
```python
# Detection: experiment closed-loop
if "experiment" in tech_desc and "闭环" in tech_desc:
    gaps.append({
        "gap_id": "GAP-001",
        "category": "实验闭环",
        "description": "Existing tech does not implement complete loop",
        "opportunity": "自主实验闭环 + 失败模式追踪"
    })

# Detection: causal reasoning
if "因果" in tech_desc or "causal" in tech_desc:
    gaps.append({
        "gap_id": "GAP-002",
        "category": "因果推理",
        "description": "现有系统缺乏因果约束的假设验证机制",
        "opportunity": "反事实推理 + 因果图约束"
    })
```

### 5. LabAutomation (实验自动化Agent)

DoE optimization and FMEA risk assessment.

**File**: `backend/app/agents/lab_automation.py`

**DoE Methods**:
```python
class DoEMethod(Enum):
    ORTHOGONAL = "orthogonal"      # L9/L18
    RSM = "rsm"                     # Response Surface (CCD/BBD)
    LHS = "lhs"                     # Latin Hypercube
    TAGUCHI = "taguchi"            # Robust design
    FULL_FACTORIAL = "full_factorial"

def generate_design(
    self,
    method: DoEMethod,
    factors: List[DoEFactor],
    **kwargs,
) -> DoEDesign:
    if method == DoEMethod.ORTHOGONAL:
        return self.design_orthogonal(factors, level=kwargs.get("level", 3))
    elif method == DoEMethod.RSM:
        return self.design_rsm(factors, center_points=kwargs.get("center_points", 5))
    elif method == DoEMethod.LHS:
        return self.design_lhs(factors, n_samples=kwargs.get("n_samples", 50))
```

**FMEA Engine**:
```python
class FMEAEngine:
    def analyze(
        self,
        experiment_type: str,       # "synthesis" / "characterization" / "performance_test"
        process_steps: List[str],
        materials: List[str] = None,
    ) -> FMEAResult:
        failure_modes = []
        for i, step in enumerate(process_steps):
            for template in self._get_failure_templates(experiment_type):
                fm = FailureMode(
                    mode_id=f"FM-{i+1:02d}-{template['suffix']}",
                    failure_mode=f"{step}过程中发生{template['mode']}",
                    severity=template['severity'],
                    occurrence=template['occurrence'],
                    detection=template['detection'],
                )
                failure_modes.append(fm)
        return FMEAResult(
            failure_modes=failure_modes,
            critical_items=[fm.mode_id for fm in failure_modes if fm.rpn > 100],
            top_risks=sorted([(fm.mode_id, fm.rpn) for fm in failure_modes], reverse=True)[:5],
        )
```

**Experiment Analysis Engine**:
- Descriptive statistics (mean, std, CV%)
- ANOVA variance analysis
- Response surface regression fitting
- Optimal condition solving

### 6. V3ShieldEngine (行为审计引擎)

AgentShield V3 for multi-agent behavior governance.

**File**: `backend/app/shield/v3_engine.py`

**Architecture**:
```
ASF-BGT Core:
  - World: Shared state storage
  - BranchTree: Branch evolution tree
  - Simulator: State projection
  - CounterfactualEngine: What-if analysis

AgentShield V3:
  - AgentBehaviorGraph: Multi-agent risk propagation
  - V3AuditLogger: Audit trail
  - V3Engine: Governance decisions
```

---

## Quick Start

### Installation

```bash
cd backend
pip install fastapi uvicorn httpx asyncio
```

### Start Server

```bash
cd backend
$env:PYTHONIOENCODING="utf-8"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8012
```

### API Usage

#### 1. Generate Hypotheses

```bash
curl -X POST http://localhost:8012/api/v1/research/hypothesis \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "研究石墨烯掺杂对锂离子电池正极材料倍率性能的影响",
    "context": {
      "domain": "电池材料",
      "prior_work": ["LiFePO4橄榄石结构", "掺杂改性研究"]
    }
  }'
```

**Response**:
```json
{
  "hypotheses": [
    {
      "id": "H-001",
      "statement": "石墨烯涂层可显著提高LiFePO4的倍率性能",
      "variables": [
        {"name": "石墨烯含量", "type": "independent", "unit": "wt%", "range_min": 0, "range_max": 10},
        {"name": "放电倍率", "type": "dependent", "unit": "C"},
        {"name": "温度", "type": "control", "unit": "°C"}
      ],
      "relations": ["石墨烯含量↑ → 电子电导率↑ → 倍率性能↑"],
      "quality_score": {"novelty": 0.85, "verifiability": 0.90, "overall": 0.87},
      "verification_methods": [
        {"method_type": "实验", "statistical_test": "ANOVA", "sample_size_estimate": 27}
      ]
    }
  ]
}
```

#### 2. Prior-Art Mining

```bash
curl -X POST http://localhost:8012/api/v1/research/priorart \
  -H "Content-Type: application/json" \
  -d '{
    "tech_description": "基于闭环控制的自主实验系统，结合FMEA故障分析"
  }'
```

**Response**:
```json
{
  "prior_art": {
    "patents": [...],
    "papers": [...],
    "products": [...]
  },
  "gaps": [
    {
      "gap_id": "GAP-001",
      "category": "实验闭环",
      "opportunity": "自主实验闭环 + 失败模式追踪"
    }
  ],
  "patentable_points": [
    {
      "id": "PP-001",
      "novelty": "首次将FMEA与DoE结合用于闭环实验优化",
      "inventive_step": "通过RPN指导实验参数迭代"
    }
  ]
}
```

#### 3. Health Check

```bash
curl http://localhost:8012/api/v1/health
```

**Response**:
```json
{
  "status": "healthy",
  "service": "ResearchForge",
  "port": 8012,
  "version": "1.0.0"
}
```

### Python Client Example

```python
import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # 1. Generate hypotheses
        resp = await client.post(
            "http://localhost:8012/api/v1/research/hypothesis",
            json={
                "research_question": "研究新型正极材料的倍率性能优化",
                "context": {"domain": "电池材料"}
            }
        )
        hypotheses = resp.json()["hypotheses"]
        print(f"Generated {len(hypotheses)} hypotheses")

        # 2. Prior-art mining
        resp = await client.post(
            "http://localhost:8012/api/v1/research/priorart",
            json={"tech_description": "闭环实验系统 + FMEA"}
        )
        gaps = resp.json()["gaps"]
        print(f"Found {len(gaps)} technology gaps")

        # 3. Health check
        resp = await client.get("http://localhost:8012/api/v1/health")
        print(resp.json())

asyncio.run(main())
```

---

## API Reference

### POST /api/v1/research/hypothesis

Generate structured research hypotheses.

**Request**:
```json
{
  "research_question": "string",
  "context": {
    "domain": "string",
    "prior_work": ["string"],
    "constraints": ["string"]
  }
}
```

**Response**:
```json
{
  "hypotheses": [
    {
      "id": "string",
      "statement": "string",
      "variables": [...],
      "relations": [...],
      "constraints": [...],
      "quality_score": {
        "novelty": 0.0-1.0,
        "verifiability": 0.0-1.0,
        "effect_size": 0.0-1.0,
        "consistency": 0.0-1.0,
        "overall": 0.0-1.0
      },
      "verification_methods": [...],
      "evidence_links": [...],
      "iteration": 1
    }
  ]
}
```

### POST /api/v1/research/priorart

Prior-art mining and technology gap analysis.

**Request**:
```json
{
  "tech_description": "string",
  "search_depth": "standard|deep"
}
```

**Response**:
```json
{
  "prior_art": {
    "patents": [...],
    "papers": [...],
    "products": [...]
  },
  "gaps": [
    {
      "gap_id": "string",
      "category": "string",
      "description": "string",
      "opportunity": "string"
    }
  ],
  "patentable_points": [
    {
      "id": "string",
      "novelty": "string",
      "inventive_step": "string",
      "technical_effect": "string",
      "confidence": 0.0-1.0,
      "claim_direction": [...]
    }
  ]
}
```

### GET /api/v1/health

Service health check.

**Response**:
```json
{
  "status": "healthy",
  "service": "ResearchForge",
  "port": 8012,
  "version": "1.0.0"
}
```

---

## Modules

### Directory Structure

```
D:\ZYY Project\ResearchForge\
├── backend/
│   ├── app/
│   │   ├── core/                    # Core engines
│   │   │   ├── research_agent.py    # Main agent + FRE
│   │   │   ├── hypothesis_engine.py # HGE: Hypothesis generation
│   │   │   ├── tool_orchestrator.py # TCO: Tool chain orchestration
│   │   │   ├── kg_constraints.py    # LCC: Knowledge graph constraint check
│   │   │   └── counterfactual.py    # Counterfactual reasoning engine
│   │   ├── agents/                  # Domain agents
│   │   │   ├── patent_miner.py      # Patent mining agent
│   │   │   ├── lab_automation.py    # Experiment automation agent
│   │   │   ├── material_gen.py      # Material generation agent
│   │   │   └── research_writer.py   # Academic writing agent
│   │   ├── api/
│   │   │   └── routes.py            # FastAPI routes
│   │   ├── shield/                  # V3 behavior audit
│   │   │   ├── v3_engine.py         # AgentShield V3
│   │   │   ├── v3_audit_logger.py   # Audit logger
│   │   │   └── agent_behavior_graph.py
│   │   ├── kg/                     # Knowledge graph
│   │   │   └── tcm_kg.py           # TCM/general knowledge graph
│   │   ├── rag/                    # RAG module
│   │   │   └── document_search.py
│   │   └── main.py                 # Service entry (port 8012)
│   └── tests/
│       └── test_research_agent.py
├── docs/
│   ├── 专利技术交底书_总稿.md
│   ├── 权利要求书.md
│   └── 实施例证据索引.md
├── benchmark/
│   ├── evaluate.py
│   └── test_cases/
│       └── test_cases.json
└── README.md
```

### Module Status

| Module | Status | Description |
|--------|--------|-------------|
| PatentMiner | v1.0 (Implemented) | Prior-art mining, gap analysis, patentable point identification |
| LabAutomation | Planning | Literature retrieval, experiment planning, HPC/instrument scheduling |
| MaterialGen | Planning | Formula generation, manufacturability screening |
| ResearchWriter | Planning | Academic paper drafting |

---

## Configuration

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| AgentShield V3 | 8011 | Behavior audit engine |
| **ResearchForge** | **8012** | Research automation platform |
| MarketingCouncil | 8009 | Debate platform |
| TCM-Mind-RAG | 8000 | TCM consultation |

### AgentConfig Defaults

```python
@dataclass
class AgentConfig:
    max_iterations: int = 10          # Maximum research iterations
    confidence_threshold: float = 0.70  # Hypothesis confidence threshold
    enable_counterfactual: bool = True  # Enable what-if analysis
    enable_kg_constraint: bool = True   # Enable KG constraint checking
```

### V3Shield Thresholds

```python
ALLOW_THRESHOLD = 0.70   # Below this: ALLOW
REVIEW_THRESHOLD = 0.90 # Above this: REVIEW / BLOCK
```

---

## Technical Details

### Knowledge Graph Constraint Check (LCC)

Physics law consistency validation prevents "hallucinated hypotheses":

```python
class KnowledgeGraphChecker:
    PHYSICS_LAWS = {
        "energy_conservation": ["能量", "守恒", "conservation", "energy"],
        "mass_conservation": ["质量", "守恒", "mass"],
        "momentum_conservation": ["动量", "守恒", "momentum"],
        "charge_conservation": ["电荷", "守恒", "charge"],
    }

    def check(self, hypothesis: Hypothesis) -> ConsistencyCheck:
        for check_fn in [
            self.check_physical_feasibility,      # Physics laws satisfied?
            self.check_dimensional_consistency,   # Units consistent?
            self.check_numerical_reasonableness,  # Values in reasonable range?
        ]:
            ok, msg = check_fn(hypothesis)
            if not ok:
                return ConsistencyCheck(
                    passed=False,
                    violation_type="physics",
                    violation_message=msg
                )
        return ConsistencyCheck(passed=True)
```

### Literature Knowledge Graph (Semantic Scholar API)

Automatic literature graph construction:

```python
class LiteratureKG:
    nodes: List[KnowledgeGraphNode]   # concept, variable, finding, method
    edges: List[KnowledgeGraphEdge]   # causes, correlates, contradicts, part_of
    paper_metadata: Dict[str, Dict]   # ArXiv/Semantic Scholar metadata

class EvidenceLink:
    evidence_id: str
    evidence_type: str        # empirical / theoretical / simulation
    source: str               # paper title, database, experiment id
    relevance_score: float    # 0-1
    supporting: bool          # True=supports, False=contradicts
    extract: str              # Key evidence excerpt
```

### Counterfactual What-If Analysis

BranchTree-based branching for future behavior risk projection:

```python
def _generate_future_branches(
    self, agent_id: str, tool_name: str, risk_score: float
) -> List[Branch]:
    if risk_score < self.risk_threshold:
        return []

    candidates = self._candidate_next_tools(agent_id, tool_name)
    cand_labels = [f"branch{i+1}:{agent_id}->{c}" for i, c in enumerate(candidates[:self.max_branches])]

    bp = self.branch_tree.fork(
        point_label=f"future:{agent_id}.{tool_name}",
        state_snapshot=self.world.state.data,
        candidate_labels=cand_labels,
        governance_results=[...],
        step=0,
    )
    return bp.candidates
```

---

## Citation

If you use ResearchForge in your research, please cite:

```bibtex
@software{researchforge,
  title = {ResearchForge: Closed-Loop Research Automation Multi-Agent System},
  author = {ResearchForge contributors},
  url = {https://github.com/your-repo/ResearchForge},
  year = {2024}
}
```

---

*Corresponding project: deep-research-report.md Top10 ideas落地实现*
*Based on: OpenClaw + ASF-BGT Framework + CrewAI + AgentShield V3*