# ResearchForge

**Closed-Loop Research Automation Multi-Agent System**

> A multi-agent framework that implements the full academic research cycle -- literature review, hypothesis generation, experimental design, simulation verification, and iterative refinement -- as an autonomous closed loop. ResearchForge integrates structured hypothesis generation with quality scoring, Design of Experiments (DoE) optimization, FMEA risk assessment, knowledge graph constraint checking, and behavior-governed multi-agent collaboration through the AgentShield V3 audit engine.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Core Modules](#core-modules)
- [API Reference](#api-reference)
- [Research and Academic Context](#research-and-academic-context)
- [Roadmap](#roadmap)
- [License](#license)
- [Contact](#contact)

---

## Overview

Scientific research follows a recurring cycle: read prior work, formulate hypotheses, design experiments, execute and analyze, then refine based on results. While individual tools exist for literature search, statistical analysis, and writing, no existing system integrates these into a fully autonomous closed loop with formal quality control at each stage.

ResearchForge addresses this by implementing a multi-agent system where specialized engines handle each phase of the research cycle:

1. **Hypothesis Generation Engine (HGE)** -- produces structured hypotheses with variables, relations, constraints, verification methods, and literature evidence links, scored on novelty, verifiability, effect size, and consistency.
2. **Tool Chain Orchestrator (TCO)** -- manages execution dependencies between research tools (code execution, simulation, visualization, literature retrieval) using topological sorting.
3. **Feedback Refinement Engine (FRE)** -- iteratively refines hypotheses based on experimental results and evaluation feedback.
4. **Knowledge Graph Constraint Checker (LCC)** -- validates hypotheses against physics laws (energy conservation, dimensional consistency, numerical reasonableness) to prevent physically impossible or hallucinated claims.

The system is further governed by **AgentShield V3**, a behavior audit engine that projects future behavior chains for multi-agent interactions and applies risk-gated governance decisions (allow, review, block).

---

## Key Features

### Structured Hypothesis Generation (HGE)

Generates hypotheses in a Variable-Hypothesis-VerificationMethod format with four-dimensional quality scoring:

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Novelty | 30% | Distinctiveness relative to existing literature |
| Verifiability | 30% | Experimental testability of the hypothesis |
| Effect Size | 20% | Expected magnitude of the proposed effect |
| Consistency | 20% | Alignment with known physics laws and prior results |

Each hypothesis includes structured variable definitions (independent, dependent, control, mediator, moderator), relation descriptions, boundary constraints, and linked verification methods (statistical tests, sample size estimates, expected effect sizes).

### Design of Experiments Optimization (DoE)

Integrated experimental design with multiple methods:

| Method | Use Case | Characteristics |
|--------|----------|-----------------|
| Orthogonal (L9/L18) | Factor screening | Identify key factors from many candidates |
| RSM (CCD/BBD) | Response surface | Model nonlinear factor-response relationships |
| Latin Hypercube (LHS) | Space-filling sampling | Maximize information coverage |
| Taguchi | Robust design | Minimize sensitivity to noise factors |
| Full Factorial | Comprehensive | All factor-level combinations |

### FMEA Risk Assessment

Knowledge-driven failure mode and effects analysis for experiment planning:

- **Failure Modes**: Template-based identification per experiment type (synthesis, characterization, performance testing).
- **Risk Priority Number (RPN)**: Severity x Occurrence x Detection scoring.
- **Critical Item Identification**: Automatic flagging of high-risk failure modes (RPN > 100).

### Knowledge Graph Constraint Checking (LCC)

Physics law consistency validation to prevent hallucinated hypotheses:

- **Physical Feasibility**: Checks against conservation laws (energy, mass, momentum, charge).
- **Dimensional Consistency**: Validates unit consistency across hypothesis variables.
- **Numerical Reasonableness**: Ensures proposed values fall within physically plausible ranges.

### Multi-Agent Research Loop

```
+------------------------------------------------------------------+
|                   ResearchForge Research Loop                     |
+------------------------------------------------------------------+
                                                                  |
    +------------------+      +-------------------+      +--------v--------+
    |  Hypothesis      |      |  Tool Chain       |      |  Feedback       |
    |  Generation (HGE)| ---> |  Execution (TCO)  | ---> |  Refinement(FRE)|
    +------------------+      +-------------------+      +--------+--------+
           ^                                                      |
           |                                                      v
    +------+--------+      +-------------------+      +-----------+------+
    |  Literature    |      |  Experiment       |      |  KG Constraint   |
    |  Knowledge     | <--- |  Results          |      |  Check (LCC)     |
    |  Graph         |      |  Analysis         |      |  Physics Laws    |
    +----------------+      +-------------------+      +------------------+
           ^                                                      |
           |                                                      |
           +------------------- Iterative Refinement --------------+
```

### AgentShield V3 Behavior Governance

Multi-agent collaboration safety through future behavior chain risk projection:

| Risk Level | Action | Threshold |
|------------|--------|-----------|
| Low | ALLOW | Risk score < 0.70 |
| Medium | REVIEW | Risk score 0.70 - 0.90 |
| High | BLOCK | Risk score >= 0.90 |

The engine performs counterfactual what-if analysis using a BranchTree-based branching mechanism to evaluate the projected outcomes of blocking vs. allowing specific agent actions.

### Patent Mining

Prior-art analysis across three source types (patents, papers, products) with:

- **Triplet Prior-Art Mining**: Automatic search across patent databases, academic literature, and product catalogs.
- **Patentable Point Identification**: Novelty, inventive step, and technical effect assessment.
- **Technology Gap Analysis**: Automatic discovery of domain gaps with opportunity descriptions.
- **Claim Direction**: Suggestions for patent claim structure.

---

## Architecture

```
+-------------------------------------------------------------------------------------------+
|                           ResearchForge System Architecture                                |
+-------------------------------------------------------------------------------------------+

  +---------------------------+          +---------------------------+
  |     OpenClaw Gateway      |          |     External APIs          |
  |   (Multi-channel Access)  |          | (Semantic Scholar, ArXiv) |
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
  |  +----------------+  +------------------+  +----------------+  |
  |  +----------------+  +------------------+                     |
  |  | ResearchWriter |  | KnowledgeGraph   |                     |
  |  +----------------+  +------------------+                     |
  +---------------------------------------------------------------+
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Python 3.10+, FastAPI, Uvicorn | API service |
| Agent Framework | CrewAI, LangChain | Multi-agent orchestration |
| Hypothesis Engine | Custom HGE with NumPy | Structured hypothesis generation and scoring |
| Tool Orchestration | Custom TCO with topological sort | Dependency-aware tool execution |
| Behavior Governance | AgentShield V3, ASF-BGT Framework | Multi-agent risk auditing |
| External APIs | httpx (Semantic Scholar, ArXiv) | Literature retrieval |
| Knowledge Graph | Custom KG with physics law constraints | Hypothesis validation |
| Testing | pytest, pytest-asyncio | Test suite |

---

## Quick Start

### Prerequisites

- Python 3.10 or later
- pip

### 1. Install Dependencies

```bash
cd ResearchForge
pip install -r requirements.txt
```

### 2. Start the Server

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8012
```

The service starts on `http://localhost:8012`.

### 3. Generate Hypotheses

```bash
curl -X POST http://localhost:8012/api/v1/research/hypothesis \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "Investigate the effect of graphene doping on the rate performance of lithium-ion battery cathode materials",
    "context": {
      "domain": "Battery Materials",
      "prior_work": ["LiFePO4 olivine structure", "Doping modification studies"]
    }
  }'
```

### 4. Perform Prior-Art Mining

```bash
curl -X POST http://localhost:8012/api/v1/research/priorart \
  -H "Content-Type: application/json" \
  -d '{
    "tech_description": "Closed-loop autonomous experiment system with FMEA failure analysis"
  }'
```

### 5. Run Tests

```bash
cd ResearchForge
python -m pytest tests/ -v
```

---

## Project Structure

```
ResearchForge/
├── backend/
│   ├── app/
│   │   ├── core/                         # Core engines
│   │   │   ├── research_agent.py         # Main agent + FRE (Feedback Refinement)
│   │   │   ├── hypothesis_engine.py      # HGE: Hypothesis generation and scoring
│   │   │   ├── tool_orchestrator.py      # TCO: Tool chain topological orchestration
│   │   │   ├── kg_constraints.py         # LCC: Knowledge graph constraint checking
│   │   │   └── counterfactual.py         # Counterfactual reasoning engine
│   │   ├── agents/                       # Domain-specific agents
│   │   │   ├── patent_miner.py           # Prior-art mining and gap analysis
│   │   │   ├── lab_automation.py         # DoE optimization and FMEA analysis
│   │   │   ├── material_generator.py     # Material formula generation
│   │   │   └── research_writer.py        # Academic writing agent
│   │   ├── shield/                       # AgentShield V3 behavior governance
│   │   │   ├── v3_engine.py              # Core V3 governance engine
│   │   │   ├── v3_audit_logger.py        # Audit trail logger
│   │   │   └── agent_behavior_graph.py   # Multi-agent risk propagation graph
│   │   ├── kg/                           # Knowledge graph modules
│   │   │   └── tcm_kg.py                # TCM/general knowledge graph
│   │   ├── rag/                          # Retrieval-augmented generation
│   │   │   └── document_search.py        # Document search module
│   │   ├── services/
│   │   │   └── project_ingestor.py       # Project data ingestion
│   │   ├── api/
│   │   │   └── routes.py                 # FastAPI route definitions
│   │   └── main.py                       # Application entry point (port 8012)
│   ├── eval/                             # Evaluation scripts
│   │   ├── hypothesis_quality_eval.py    # Hypothesis quality evaluation
│   │   ├── retrieval_eval.py             # Retrieval quality evaluation
│   │   └── tool_use_eval.py              # Tool usage evaluation
│   ├── experiments/                      # Experimental results
│   │   ├── benchmark_suite.py            # Benchmark test suite
│   │   ├── ablation_study.py             # Ablation study runner
│   │   ├── benchmark_results.json        # Benchmark results data
│   │   └── ablation_results.json         # Ablation study results
│   └── test_sci.py                       # SCI-level integration tests
├── docs/
│   ├── EXPERIMENT_DESIGN.md              # Experiment design document
│   ├── INNOVATION.md                     # Innovation analysis
│   └── SCI_PAPER_OUTLINE.md              # SCI paper outline
├── researchforge_outputs/                # Generated analysis outputs
│   ├── AgentShield_V3_成果分析.md
│   ├── Embodied_TCM_AI_成果分析.md
│   ├── Evidence_Index.md
│   ├── SCI方向矩阵.md
│   └── 专利点矩阵.md
├── tests/
│   ├── conftest.py                       # Test fixtures
│   ├── test_smoke.py                     # Smoke tests
│   └── __init__.py
├── docs/
│   ├── 专利技术交底书_总稿.md              # Patent disclosure
│   ├── 权利要求书.md                       # Patent claims
│   └── 实施例证据索引.md                   # Implementation evidence index
├── requirements.txt                      # Python dependencies
├── start.sh                              # Startup script
├── REPRODUCE.md                          # Reproduction guide
├── SCI_FRAMEWORK.md                      # SCI paper framework
├── 专利技术交底书.md                       # Patent technical disclosure
└── README.md
```

---

## Core Modules

### ResearchAgent (`backend/app/core/research_agent.py`)

The central orchestrator managing the research loop lifecycle. Executes the four-phase cycle:

1. **Hypothesis Generation (HGE)** -- generates structured hypotheses from the research question.
2. **Tool Chain Execution (TCO)** -- executes research tools with dependency-aware ordering.
3. **Feedback Refinement (FRE)** -- iteratively refines hypotheses based on tool results.
4. **Knowledge Graph Constraint Check (LCC)** -- validates hypotheses against physics laws.

**Configuration:**

```python
@dataclass
class AgentConfig:
    max_iterations: int = 10            # Maximum research iterations
    confidence_threshold: float = 0.70  # Hypothesis confidence threshold
    enable_counterfactual: bool = True  # Enable what-if analysis
    enable_kg_constraint: bool = True   # Enable KG constraint checking
```

### HypothesisEngine (`backend/app/core/hypothesis_engine.py`)

Generates structured hypotheses with multi-modal support (text, image, data) and evaluates quality across four dimensions. Integrates with external literature APIs (Semantic Scholar) for evidence-grounded hypothesis generation.

Key classes:

- `Variable` -- independent, dependent, control, mediator, moderator types.
- `Hypothesis` -- full structured hypothesis with variables, relations, constraints, and evidence links.
- `HypothesisQualityScore` -- four-dimensional scoring (novelty, verifiability, effect_size, consistency).
- `VerificationMethod` -- statistical test specifications with sample size and effect size estimates.
- `KnowledgeGraphChecker` -- physics law consistency validation.

### ToolOrchestrator (`backend/app/core/tool_orchestrator.py`)

Manages tool execution dependencies using Kahn's algorithm for topological sorting. Available tools:

- `CodeExecutor` -- Python code execution.
- `Simulator` -- External simulation software invocation.
- `Visualizer` -- Data visualization (Matplotlib/Plotly).
- `LiteratureRetriever` -- Academic literature search.

**State Machine**: READY -> EXECUTING -> VALIDATING -> FEEDBACK -> REFINE -> DONE

### PatentMiner (`backend/app/agents/patent_miner.py`)

Prior-art mining and patentability analysis across patent, paper, and product sources. Identifies technology gaps and generates claim direction suggestions.

### LabAutomation (`backend/app/agents/lab_automation.py`)

DoE optimization engine with five experimental design methods and FMEA risk assessment with template-based failure mode identification.

### V3ShieldEngine (`backend/app/shield/v3_engine.py`)

AgentShield V3 behavior governance engine built on the ASF-BGT Framework. Performs:

- Future behavior chain risk projection.
- Multi-agent risk propagation analysis.
- Counterfactual what-if scenario evaluation.
- Gated governance decisions (allow/review/block).

---

## API Reference

### Health Check

```
GET /api/v1/health
```

Returns service status, port, and version.

### Generate Hypotheses

```
POST /api/v1/research/hypothesis
```

**Request:**

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

**Response:**

```json
{
  "hypotheses": [
    {
      "id": "H-001",
      "statement": "string",
      "variables": [
        {"name": "string", "type": "independent", "unit": "string", "range_min": 0, "range_max": 10}
      ],
      "relations": ["string"],
      "quality_score": {
        "novelty": 0.85,
        "verifiability": 0.90,
        "effect_size": 0.80,
        "consistency": 0.88,
        "overall": 0.87
      },
      "verification_methods": [
        {"method_type": "string", "statistical_test": "string", "sample_size_estimate": 27}
      ]
    }
  ]
}
```

### Prior-Art Mining

```
POST /api/v1/research/priorart
```

**Request:**

```json
{
  "tech_description": "string",
  "search_depth": "standard|deep"
}
```

**Response:**

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
      "category": "string",
      "description": "string",
      "opportunity": "string"
    }
  ],
  "patentable_points": [
    {
      "id": "PP-001",
      "novelty": "string",
      "inventive_step": "string",
      "technical_effect": "string",
      "confidence": 0.85,
      "claim_direction": [...]
    }
  ]
}
```

Full API documentation is available at `http://localhost:8012/docs` when the service is running.

---

## Research and Academic Context

ResearchForge is designed to support the full academic research lifecycle, with particular emphasis on materials science, battery research, and Traditional Chinese Medicine domains. The system produces structured outputs suitable for SCI paper preparation and patent filing.

### Accompanying Documents

- **SCI Paper Framework**: `SCI_FRAMEWORK.md` -- structured outline for a journal submission.
- **Patent Disclosure**: `专利技术交底书.md` -- technical disclosure for patent filing.
- **Patent Claims**: `docs/权利要求书.md` -- formal patent claim language.
- **Experiment Design**: `docs/EXPERIMENT_DESIGN.md` -- detailed experiment design documentation.
- **Innovation Analysis**: `docs/INNOVATION.md` -- innovation point analysis.

### Module Status

| Module | Status | Description |
|--------|--------|-------------|
| PatentMiner | Implemented (v1.0) | Prior-art mining, gap analysis, patentable point identification |
| LabAutomation | In Development | DoE optimization, FMEA risk assessment, experiment analysis |
| MaterialGen | Planned | Formula generation, manufacturability screening |
| ResearchWriter | Planned | Academic paper drafting |

---

## Roadmap

- [ ] Complete LabAutomation module with full DoE and FMEA integration.
- [ ] Implement MaterialGen for automated material formula generation.
- [ ] Add ResearchWriter for automated academic paper drafting.
- [ ] Integration with HPC clusters for simulation task submission.
- [ ] Real-time experiment monitoring and adaptive DoE adjustment.
- [ ] Cross-domain knowledge transfer between research domains.
- [ ] Web UI for interactive research project management.
- [ ] Support for multi-institution collaborative research workflows.

---

## License

This project is released under the MIT License. See `LICENSE` for details.

---

## Contact

For questions, collaborations, or academic inquiries, please open an issue on the repository or contact the maintainers directly.
