# ProjectIngestor 测试报告

**日期：** 2026-05-10
**状态：** ✅ 完成

---

## 测试目标

验证 ResearchForge ProjectIngestor 能正确读取已有项目并生成 ProjectDigest 结构。

---

## 测试项目

### 1. AgentShield V3

| 字段 | 值 |
|------|-----|
| 路径 | `D:\ZYY Project\AgentShield_V3` |
| Git Commit | `bf3bf42` |
| 检测到端口 | `8011` |
| 检测到模块 | `agents`, `api`, `shield` |
| 检测到 API | 6 条（见下） |

**检测到的 API：**
```
POST /process_call
GET /status/{session_id}
POST /fork_branch
GET /export_chain/{session_id}
GET /behavior_graph/{session_id}
POST /simulate_steps
```

**检测到的证据文件（8个）：**
- `benchmark/benchmark_fixed.json`
- `benchmark/benchmark_report.json`
- `benchmark/benchmark_v3_standard.json`
- `benchmark/test_cases/test_cases.json`
- `benchmark/test_cases/test_cases_100.json`
- `benchmark/test_cases/test_cases_extended.json`
- `benchmark/test_cases/test_cases_v3_standard.json`
- `benchmark/confusion_matrix_v3.json`

**文档：** `docs/AgentShield_V3_Action_Repair_Report.md`

---

### 2. Embodied-TCM-AI

| 字段 | 值 |
|------|-----|
| 路径 | `D:\ZYY Project\Embodied-TCM-AI` |
| 检测到端口 | `8016` |
| 检测到模块 | `digital_twin_agent`, `models`, `motion_compliance_agent`, `orchestrator`, `tcm_cognition_agent`, `utils`, `visual_perception_agent` |
| 检测到 API | 11 条（见下） |

**检测到的 API：**
```
POST /api/acupoint
GET /api/acupoint
GET /api/acupoint/{acupoint_id}
GET /api/kg/acupoint/{name}
GET /api/kg/techniques
GET /api/kg/meridians
POST /api/massage/execute
GET /api/massage/execution/{execution_id}
GET /api/massage/stream/{execution_id}
GET /health
GET /
```

**检测到的证据文件（1个）：**
- `docs/websocket_demo_evidence.json`

**文档：** `docs/WebSocket_Realtime_Demo_Report.md`

---

## 扫描结果统计

| 项目 | README | 文档 | 证据文件 | 测试文件 | API数 | 端口 |
|------|--------|------|----------|---------|-------|------|
| AgentShield V3 | 1 | 2 | 8 | 0 | 6 | 8011 |
| Embodied-TCM-AI | 1 | 2 | 1 | 0 | 11 | 8016 |

---

## 当前无法自动判断的内容（limitations）

以下内容**无法通过文件扫描自动判断**，需要后续模块补充：

| 局限 | 说明 |
|------|------|
| 代码运行正确性 | 需要实际执行验证，无法从源码判断 |
| SCI / 专利新颖性 | 需要领域专家判断，无法自动评估 |
| 机械臂硬件可用性 | 需要实际部署测试，无法从代码判断 |
| 模块功能描述 | 当前依赖启发式规则（目录名/Python文件名），可能误判 |

---

## 已有字段对接下一步模块

ProjectDigest 完整字段清单及下游模块对接建议：

```
project_name          → 可被 PatentDraftGenerator / SCIDraftPlanner 使用
project_path          → 用于定位项目
readme_files          → 可输入 HypothesisGenerator 生成研究假设
docs_files            → 可输入 EvidenceIndexer 提取关键证据
evidence_files        → 已有！可对接 AgentShield V3 基准报告
test_files            → 可输入 SCI Draft Planner 评估测试覆盖度
detected_modules      → 可输入 HypothesisGenerator 判断项目类型
detected_apis         → 可输入 PatentMiner 分析 API 层面的新颖性
detected_ports        → 可验证项目是否在运行
git_commit            → 可追踪项目版本
summary               → 可作为研究背景摘要
limitations           → 诚实说明当前能力边界
scan_errors           → 如有错误需人工介入
```

---

## API 端点

**POST /api/v1/research/ingest_project**

请求：
```json
{
  "project_path": "D:\\ZYY Project\\AgentShield_V3"
}
```

响应：
```json
{
  "status": "success",
  "data": { /* ProjectDigest */ },
  "message": "项目 D:\\ZYY Project\\AgentShield_V3 摄取完成，发现 3 个模块"
}
```

---

## 产出文件

- `researchforge_outputs/project_digest_agentshield_v3.json` — AgentShield V3 摄取结果
- `researchforge_outputs/project_digest_embodied_tcm_ai.json` — Embodied-TCM-AI 摄取结果
- `backend/app/services/project_ingestor.py` — 核心模块
- `backend/app/api/routes.py` — 已新增 `/ingest_project` 端点

---

## 结论

✅ 三个验收标准全部达成：
1. **API 可用** — POST /api/v1/research/ingest_project 返回结构化 JSON
2. **两个 digest 文件已生成** — project_digest_*.json
3. **报告已生成** — 本文档说明读到内容和未读内容

ResearchForge 现在已具备"母工厂"能力的第一步：摄取项目，结构化输出。下一步可接入 PatentDraftGenerator / SCIDraftPlanner。