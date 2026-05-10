# Evidence 索引

> 覆盖项目：AgentShield V3、Embodied-TCM-AI、ReflexMarket-AI、ResearchForge、PatentCaptor
> 生成日期：2026-05-10

## AgentShield V3（证据链最完整）

| 证据类型 | 路径/文件 | 内容 | 用途 |
|---------|---------|------|------|
| Benchmark 测试结果 | `benchmark/benchmark_report.json` | 100条测试，Score 100%，Action 86% | SCI/专利 |
| 核心引擎代码 | `backend/app/shield/v3_engine.py` | _governance_decision, _counterfactual_whatif | 专利/代码 |
| 行为图模块 | `backend/app/shield/agent_behavior_graph.py` | add_tool_call_as_node, compute_risk_propagation | 专利/代码 |
| ASF-BGT Framework | `D:\ZYY Project\ASF-BGT-Framework/` | World/BranchTree/CounterfactualEngine | 基础设施 |
| 治理门控代码 | `D:\ZYY Project\ASF-BGT-Framework/governance/gates.py` | GovernanceAction 枚举，三级门控 | 专利/代码 |
| 修复报告 | `docs/AgentShield_V3_Action_Repair_Report.md` | 修复前后对比，混淆矩阵 | 项目文档 |
| README | `README.md` | 项目概述，架构图 | 项目主页 |

---

## Embodied-TCM-AI

| 证据类型 | 路径/文件 | 内容 | 用途 |
|---------|---------|------|------|
| 五元组代码 | `src/models/massage_params.py` | M={F,A,V,T,S} 数据类 | 专利/代码 |
| 阻抗控制 | `src/motion_compliance_agent/` | ImpedanceController, get_control_mode | 专利/代码 |
| 知识图谱 | `backend/app.py`（init_knowledge_graph） | 5个穴位+4种手法+4条经络 | 专利/代码 |
| PI-GNN 模型 | `src/models/PI-GNN.py` | 物理信息消息传递层 | 专利/代码 |
| WebSocket Demo | `docs/websocket_demo_evidence.json` | 10个时间步实时流数据 | Demo/文档 |
| WebSocket 报告 | `docs/WebSocket_Realtime_Demo_Report.md` | 架构图+字段说明+Future Work | 项目文档 |
| 专利技术交底书 | `专利技术交底书.md` | 5条权利要求完整版 | 专利 |
| 多Agent编排 | `src/orchestrator/engine.py` | 四Agent协作引擎 | 代码 |
| 后端API | `backend/app.py` | /api/massage/execute, /api/kg/*, WS | API文档 |

---

## ReflexMarket-AI

| 证据类型 | 路径/文件 | 内容 | 用途 |
|---------|---------|------|------|
| README | `README.md` | 版本路线（V0.2-V0.5）+架构图 | 项目主页 |
| V0.2 Demo 证据 | `docs/demo_evidence_v0.2/` | 泡沫/恐慌/反转仿真数据 | SCI/专利 |
| V0.3 Demo 证据 | `docs/demo_evidence_v0.3/` | 信任崩塌实验数据 | SCI |
| V0.4 Demo 证据 | `docs/demo_evidence_v0.4/` | 异常检测数据 | SCI |
| V0.5 Demo 证据 | `docs/demo_evidence_v0.5/` | 监管干预数据 | SCI |
| 核心Agent代码 | `src/agents/` | Narrative/Trust/Emotion/Behavior/Capital Agent | 代码 |
| 反身性监控 | `src/agents/reflexivity_monitor.py` | 反身性回路量化 | 专利/代码 |
| 操纵风险检测 | `src/agents/manipulation_risk_agent.py` | volume_spike 异常检测 | 专利/代码 |
| 监管Agent | `src/agents/regulator_agent.py` | V0.5监管干预 | SCI |

---

## ResearchForge

| 证据类型 | 路径/文件 | 内容 | 用途 |
|---------|---------|------|------|
| README | `README.md` | 架构图+API列表 | 项目主页 |
| 核心引擎 | `backend/app/core/hypothesis_engine.py` | HGE假设生成引擎 | 专利/代码 |
| 工具编排器 | `backend/app/core/tool_orchestrator.py` | TCO工具链编排 | 代码 |
| KG约束 | `backend/app/core/kg_constraints.py` | LCC知识图谱约束 | 专利/代码 |
| PatentMiner Agent | `backend/app/agents/patent_miner.py` | v1.0专利挖掘 | 专利/代码 |
| 科研写作Agent | `backend/app/agents/research_writer.py` | 学术写作 | 代码 |
| 反事实引擎 | `backend/app/core/counterfactual.py` | 反事实推理 | 专利/代码 |
| SCI论文大纲 | `docs/SCI_PAPER_OUTLINE.md` | 论文框架 | SCI |
| 实验设计 | `docs/EXPERIMENT_DESIGN.md` | 消融实验设计 | SCI |
| **Future Work** | LabAutomation / MaterialGen Agent | **尚未实现** | — |

---

## PatentCaptor

| 证据类型 | 路径/文件 | 内容 | 用途 |
|---------|---------|------|------|
| 专利技术交底书 | `docs/专利技术交底书.md` | 5条权利要求完整版 | 专利 |
| MeetingListener Agent | `backend/app/agents/meeting_listener.py` | 核心逻辑（未实测） | 专利/代码 |
| API路由 | `backend/app/api/routes.py` | analyze/summary/alert三接口 | API |
| SCI论文大纲 | `docs/SCI_PAPER_OUTLINE.md` | 论文框架（规划中） | SCI |
| **Future Work** | Whisper ASR 集成 | **尚未实现** | — |
| **Future Work** | 专利数据库接口 | **尚未实现** | — |
| **Future Work** | 发明点构图模块 | **规划中，未实现** | — |

---

## 证据丰富度排名

| 项目 | 代码证据 | Demo证据 | 文档证据 | 总体 |
|------|---------|---------|---------|------|
| AgentShield V3 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **最完整** |
| Embodied-TCM-AI | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **完整** |
| ReflexMarket-AI | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 完整 |
| ResearchForge | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | 中等 |
| PatentCaptor | ⭐⭐ | ⭐ | ⭐⭐ | 较弱（缺实测） |

---

## 快速索引

**专利申报找证据 →**
- AgentShield V3：看 `benchmark_report.json` + `v3_engine.py`
- Embodied-TCM-AI：看 `专利技术交底书.md` + `massage_params.py`
- ReflexMarket-AI：看 `docs/demo_evidence_v0.2/` 文件夹

**SCI 写实验找证据 →**
- AgentShield V3：看 `benchmark/evaluate.py` 评分逻辑
- ReflexMarket-AI：看 V0.2-V0.5 各 demo_evidence 文件夹
- Embodied-TCM-AI：看 `PI-GNN.py` + `motion_compliance_agent/`