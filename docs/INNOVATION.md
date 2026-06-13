# ResearchForge Innovation Documentation

> Technical innovation analysis and patent-ready contributions of the ResearchForge multi-agent system.

---

## 1. System-Level Innovation: Closed-Loop Research Automation

### Problem Statement

Existing AI-for-Science tools (GPT-4 Science Mode, Semantic Scholar, Elicit) provide isolated capabilities: literature search, text summarization, or hypothesis suggestion. None implements a **complete closed-loop** from hypothesis generation through experimental verification back to hypothesis refinement.

### Innovation: Full-Cycle Research Agent Loop

ResearchForge implements a four-phase iterative loop:

```
Hypothesis Generation (HGE)
    -> Tool Chain Execution (TCO)
        -> Feedback Refinement (FRE)
            -> Knowledge Graph Constraint Check (LCC)
                -> (loop back to HGE if confidence < threshold)
```

**Novelty**: This is the first system that integrates structured hypothesis generation, automated experimental design, simulation execution, and iterative refinement into a single agent-driven loop with formal quality scoring and governance.

---

## 2. Hypothesis Generation Engine (HGE)

### 2.1 Structured Hypothesis Format

Unlike free-text hypothesis suggestion, HGE generates **structured hypotheses** with explicit variable definitions, verification methods, and quality scores:

| Field | Description | Innovation |
|-------|-------------|------------|
| `variables` | Independent/dependent/control/mediator/moderator with operationalization | Enables automated experiment design |
| `relations` | Directional relationships (e.g., "X up -> Y down") | Enables causal reasoning |
| `verification_methods` | Statistical test, sample size, effect size, confidence level | Bridges hypothesis to experiment |
| `quality_score` | 4-dimensional scoring (novelty, verifiability, effect_size, consistency) | Quantitative hypothesis ranking |
| `evidence_links` | Links to literature KG nodes with relevance scores | Evidence-grounded generation |

### 2.2 Literature Knowledge Graph (LKG)

**Technical Approach**: Async construction of a literature knowledge graph via Semantic Scholar API, with fallback mock generation for offline use.

- Node types: `paper`, `concept`, `finding`, `method`
- Edge types: `cites`, `related_to`, `contradicts`, `part_of`
- Entity linking: Concepts extracted from papers linked to hypothesis variables

### 2.3 Quality Scoring System

Four-dimensional scoring with configurable weights:

| Dimension | Weight | Method |
|-----------|--------|--------|
| Novelty | 30% | Concept overlap with LKG nodes |
| Verifiability | 30% | Presence of statistical tests, sample sizes, operationalized variables |
| Effect Size | 20% | Causal keywords, mediator variables, declared effect sizes |
| Consistency | 20% | Variable type coverage, constraint-relation contradiction check |

### 2.4 Knowledge Graph Constraint Checker (LCC)

**Physics Law Validation**: Checks hypotheses against fundamental conservation laws (energy, mass, momentum, charge) using keyword matching.

**Dimensional Consistency**: Framework for unit checking (extensible).

**Novelty**: KG is used not just for retrieval but as an active constraint filter on generated hypotheses.

---

## 3. Tool Chain Orchestrator (TCO)

### 3.1 State Machine Architecture

```
READY -> EXECUTING -> VALIDATING -> FEEDBACK -> REFINE -> DONE
                                                      \-> FAILED
```

### 3.2 Dependency Resolution

**Kahn's Algorithm** for topological sorting of tool call dependencies. Each `ToolCall` declares:
- `dependencies`: list of output keys it depends on
- `output_key`: key for its result in the shared cache
- `timeout`: per-call timeout
- `max_retries`: retry policy

### 3.3 Built-in Tool Registry

| Tool | Function |
|------|----------|
| `code_executor` | Python code execution (sandboxed) |
| `simulator` | External simulation software integration |
| `visualizer` | Chart/figure generation |
| `literature_retriever` | Paper search and retrieval |

**Novelty**: Automatic dependency resolution means researchers can declare what they need without specifying execution order.

---

## 4. Lab Automation Agent

### 4.1 Design of Experiments (DoE) Engine

Supports five experimental design methods:

| Method | Implementation | Use Case |
|--------|---------------|----------|
| Orthogonal (L9/L18/L36) | Custom factorial generator | Factor screening |
| RSM (CCD) | 2^n + 2n axial + center points | Response surface modeling |
| Latin Hypercube Sampling | Stratified uniform sampling | Space-filling designs |
| Taguchi | 2-level orthogonal | Robust design |
| Full Factorial | CCD without center points | Complete enumeration |

### 4.2 FMEA Engine (Failure Mode and Effects Analysis)

Automated FMEA for experimental processes:

- **RPN Calculation**: Risk Priority Number = Severity x Occurrence x Detection
- **Critical Item Identification**: RPN > 100 flagged as critical
- **Template-based**: Pre-defined failure templates for synthesis, characterization, and performance testing

### 4.3 Experiment Result Analysis

- Descriptive statistics (mean, std, CV%)
- Simplified ANOVA (p-values per factor)
- Model fitting (R-squared, adjusted R-squared)
- Optimal condition prediction

**Novelty**: End-to-end from experiment design through FMEA risk analysis to statistical result analysis in a single agent.

---

## 5. Material Generation Agent

### 5.1 Template-Based Material Design

Domain-specific templates for:
- Energy density optimization (Ni-rich layered oxides, high-voltage spinels)
- Thermal stability improvement (oxide/fluoride coatings)

### 5.2 TRL Assessment

Each candidate material includes:
- Technology Readiness Level (TRL 1-9)
- Estimated cost
- Synthesis step count
- Expected properties (energy density, thermal stability, cycle life)

**Novelty**: Automated material candidate generation with integrated TRL assessment and synthesis route suggestion.

---

## 6. Patent Mining Agent

### 6.1 Prior Art Triangulation

Three-source prior art search:
- **Patents**: Keyword-matched patent family search
- **Papers**: Literature key-findings matching
- **Products**: Capability-matching against known products

### 6.2 Gap Analysis

Automated technology gap identification across four categories:
1. Experiment closed-loop completeness
2. Causal reasoning capability
3. Knowledge graph constraint utilization
4. Multi-agent collaboration governance

### 6.3 Patentable Point Generation

Each gap maps to:
- Novelty statement
- Inventive step description
- Technical effect
- Claim direction suggestions

---

## 7. AgentShield V3: Behavioral Governance

### 7.1 Behavior Graph

Multi-agent tool call sequences modeled as a directed graph:
- **Nodes**: Agent identity + tool call + risk score + fuse action
- **Edges**: Agent-to-agent invocation, data flow
- **Risk Propagation**: Computed across the graph to identify cascading risks

### 7.2 Future Branch Prediction

When risk score exceeds threshold, the engine generates **future branches** predicting possible next tool calls and their risk profiles.

### 7.3 Counterfactual What-If Analysis

For high-risk tool calls, a counterfactual engine projects:
- "What if we blocked this call?"
- Risk delta estimation
- Affected agent list

### 7.4 V3 Audit Logger

Tamper-evident audit chain:
- Each record includes hash of previous record
- Chain integrity verifiable by recomputing hashes
- Exportable as JSON for compliance review

**Novelty**: First system to combine behavior graph risk propagation with counterfactual analysis for multi-agent research governance.

---

## 8. Architectural Innovations

### 8.1 Modular Agent Design

Each agent (HypothesisEngine, LabAutomation, MaterialGen, PatentMiner) is independently testable and composable. The ResearchAgent orchestrates them through a standard interface.

### 8.2 Sync/Async Dual Interface

HypothesisEngine provides both:
- `generate()` - async for API/server use
- `generate_sync()` - for CLI/testing use

### 8.3 Graceful Degradation

- Literature KG falls back to mock data when API unavailable
- Tool execution uses timeout/retry for resilience
- Quality scoring handles missing fields with defaults

---

## 9. Patent-Ready Claims Summary

| ID | Claim | Category |
|----|-------|----------|
| PP-001 | Complete loop: hypothesis -> experiment -> verification -> refinement | Experiment closed-loop |
| PP-002 | Counterfactual reasoning + causal graph for hypothesis verification | Causal reasoning |
| PP-003 | KG-constrained hypothesis generation with consistency checking | KG constraints |
| PP-004 | Multi-agent behavioral governance with risk propagation graph | Agent governance |
| PP-005 | Integrated DoE + FMEA + statistical analysis in single agent | Lab automation |
| PP-006 | Structured hypothesis format with 4-dimensional quality scoring | Hypothesis quality |

---

## 10. Comparison with Existing Systems

| Capability | GPT-4 Science | Elicit | Semantic Scholar | ResearchForge |
|-----------|---------------|--------|------------------|---------------|
| Literature search | Partial | Yes | Yes | Yes |
| Hypothesis suggestion | Text only | No | No | Structured + scored |
| Experiment design | No | No | No | DoE + FMEA |
| Simulation execution | No | No | No | Yes |
| Iterative refinement | No | No | No | FRE loop |
| Behavioral governance | No | No | No | AgentShield V3 |
| Patent analysis | No | No | No | PatentMiner |
