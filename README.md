# ResearchForge — 科研自动化多智能体系统

> 基于 OpenClaw + ASF-BGT Framework + CrewAI 构建的科研自动化多智能体协作平台

## 定位

**一句话：** 让 AI Agent 自主完成"读文献 → 提出假设 → 设计实验 → 仿真验证 → 迭代修正"的科研闭环。

**与 OpenClaw 的关系：**
- OpenClaw = 多通道接入 + 多智能体路由 + 边缘执行 + Canvas 可视化
- ResearchForge = OpenClaw 在科研场景的具体落地实现

## 核心架构

```
OpenClaw Gateway (多通道接入)
        ↓
ASF-BGT Framework (行为治理底座)
  ├── World (共享状态)
  ├── BranchTree (分支演化树)
  ├── Simulator (状态推演)
  └── CounterfactualEngine (反事实引擎)
        ↓
V3ShieldEngine (行为审计与风险治理) ← AgentShield V3
        ↓
CrewAI Multi-Agent Core (科研智能体编排)
  ├── HGE: Hypothesis Generation Engine
  ├── LCC: Logical Consistency Checker
  ├── TCO: Tool Chain Orchestrator
  └── FRE: Feedback Refinement Engine
        ↓
Domain Modules (领域专用模块)
  ├── PatentMiner: 专利 prior-art mining + 可专利点识别
  ├── LabAutomation: 自主实验规划 + HPC/仪器调度
  ├── MaterialGen: 材料配方生成 + 可制造性筛选
  └── KnowledgeGraph: 知识图谱构建 + 因果推理
```

## 目录结构

```
D:\ZYY Project\ResearchForge\
├── backend/
│   ├── app/
│   │   ├── core/                    # 核心引擎
│   │   │   ├── __init__.py
│   │   │   ├── research_agent.py    # 主智能体 + FRE
│   │   │   ├── hypothesis_engine.py # HGE: 假设生成
│   │   │   ├── tool_orchestrator.py # TCO: 工具链编排
│   │   │   ├── kg_constraints.py     # LCC: 知识图谱约束检查
│   │   │   └── counterfactual.py     # 反事实推理引擎
│   │   ├── agents/                  # 各领域 Agent
│   │   │   ├── patent_miner.py      # 专利挖掘 Agent
│   │   │   ├── lab_automation.py    # 实验自动化 Agent
│   │   │   ├── material_gen.py      # 材料生成 Agent
│   │   │   └── research_writer.py    # 学术写作 Agent
│   │   ├── api/
│   │   │   └── routes.py            # FastAPI 路由
│   │   ├── shield/                  # V3 行为审计（复用 AgentShield V3）
│   │   │   ├── v3_engine.py         # ← 复制自 AgentShield V3
│   │   │   ├── v3_audit_logger.py
│   │   │   └── agent_behavior_graph.py
│   │   ├── kg/                     # 知识图谱模块
│   │   │   └── tcm_kg.py            # 中医/通用知识图谱
│   │   ├── rag/                    # RAG 模块
│   │   │   └── document_search.py
│   │   └── main.py                 # 服务入口（端口 8012）
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

## 已实现模块

### ✅ PatentMiner (专利挖掘 Agent) — v1.0
- 三元组 prior-art mining（专利/论文/产品）
- 可专利点实时识别
- 技术空白点分析
- 权利要求对比

### 🔄 LabAutomation (实验自动化) — 规划中
- 文献检索与抽取
- 实验计划生成
- HPC/仿真接口调度
- 失败模式追踪

### 🔄 MaterialGen (材料配方生成) — 规划中
- 配方生成 + 可制造性评估
- 主动学习闭环

## 端口

| 服务 | 端口 | 说明 |
|------|------|------|
| AgentShield V3 | 8011 | 行为审计引擎 |
| ResearchForge | **8012** | 科研自动化平台 |
| MarketingCouncil | 8009 | 辩论平台 |
| TCM-Mind-RAG | 8000 | 中医问诊 |

## 创新点

1. **闭环科研智能体**：假设生成 → 实验设计 → 仿真验证 → 迭代修正，全流程可审计
2. **V3 行为治理**：所有工具调用经 AgentShield V3 审计，确保实验安全执行
3. **反事实推演**：在假阳性/假阴性之间做 what-if 分析
4. **可解释约束**：知识图谱因果约束防止"幻觉假设"

## 快速启动

```bash
cd backend
$env:PYTHONIOENCODING="utf-8"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8012
```

## API

### POST /api/v1/research/hypothesis
输入研究问题，输出结构化假设列表 + 验证路径

### POST /api/v1/research/priorart
输入技术描述，输出专利/论文/产品 prior-art 分析

### GET /api/v1/health
系统健康检查

---

*对应项目：deep-research-report.md Top10 ideas 落地实现*
*基于：OpenClaw + ASF-BGT + CrewAI + AgentShield V3*