# SCI 方向矩阵

> 覆盖项目：AgentShield V3、Embodied-TCM-AI、ReflexMarket-AI、ResearchForge、PatentCaptor
> 生成日期：2026-05-10

## SCI 方向总表

| # | SCI 方向 | 期刊/会议 | 对应项目 | 实验类型 | 创新性 | 可实现度 |
|---|---------|---------|---------|---------|--------|---------|
| 1 | 多 Agent 安全治理框架 | CCS/S&P/IEEE S&P | AgentShield V3 | 对比实验 | 高 | 高 |
| 2 | AI Agent 可解释性与溯源 | NeurIPS/ICML/ICLR | AgentShield V3 | 消融实验 | 高 | 高 |
| 3 | 具身智能的物理约束推理 | ICRA/IROS/Nature MI | Embodied-TCM-AI | Sim-to-Real | 高 | 中 |
| 4 | 机械臂阻抗控制人机共融 | IEEE Trans. Robotics/ICRA | Embodied-TCM-AI | 用户实验 | 中 | 中 |
| 5 | 复杂系统多 Agent 建模（金融反身性） | Nature Computational Science/AAMAS | ReflexMarket-AI | 仿真实验 | 高 | 高 |
| 6 | 监管科技与异常检测 | IEEE TKDE/ICIS | ReflexMarket-AI | 异常检测 | 中 | 高 |
| 7 | AI 辅助科研假设生成 | Nature AI Review/NeurIPS/AIME | ResearchForge | 用户研究 | 高 | 中 |
| 8 | 主动学习与实验自动设计 | ICML/NeurIPS/ICLR | ResearchForge | 主动学习 | 高 | 中 |
| 9 | 创新检测算法（ novelty detection） | KDD/WWW/ACL | PatentCaptor | 算法对比 | 中 | 高 |
| 10 | 会议挖掘与知识抽取 | ACL/EMNLP/KDD | PatentCaptor | 数据集实验 | 中 | 高 |

---

## 按项目详解

### AgentShield V3

#### 方向 1：多 Agent 安全治理框架（最佳 SCI）
- **适合会议：** IEEE S&P 2025 / CCS 2025
- **实验设计：**
  - Baseline：无治理的纯 LangChain 多 Agent 系统
  - 实验组：接入 AgentShield V3
  - 对比指标：风险检测率、误报率、审计延迟
  - 场景：100 条 benchmark + 真实 Dify 工作流
- **评价指标：** Detection Rate / False Positive Rate / Latency
- **创新点：** 行为链级别的实时治理，区别于传统 API 监控
- **消融实验：** 因果传播 ON/OFF、反事实推演 ON/OFF

#### 方向 2：AI Agent 可解释性
- **适合会议：** NeurIPS 2025 / ICLR 2025
- **实验设计：** 行为链可视化 vs 无可视化的审计可靠性
- **Baseline：** 传统日志审计（ELK Stack）、事后分析
- **评价指标：** 溯源准确率、因果链完整性、审计员效率

---

### Embodied-TCM-AI

#### 方向 3：具身智能的物理约束推理（最佳 SCI）
- **适合期刊：** Nature Machine Intelligence / ICRA 2025
- **实验设计：**
  - Baseline：纯位置控制、固定刚度阻抗控制
  - 实验组：PI-GNN 数字孪生 + 自适应阻抗
  - 指标：Sim-to-Real Gap、操作精度、力控制稳定性
- **注意：** 需要仿真平台（MuJoCo/PyBullet）+ 真实机械臂数据
- **消融实验：** PI-GNN ON/OFF、知识图谱约束 ON/OFF

#### 方向 4：机械臂人机共融
- **适合期刊：** IEEE Transactions on Robotics / ICRA
- **实验设计：** 固定刚度 vs 自适应阻抗的接触力稳定性
- **评价指标：** 接触力超调量、稳态误差、安全截断次数

---

### ReflexMarket-AI

#### 方向 5：金融反身性多 Agent 建模（最佳 SCI）
- **适合期刊：** Nature Computational Science / AAMAS 2025
- **实验设计：**
  - 仿真场景：泡沫形成、恐慌传播、信任崩塌、KOL 协同放大
  - Baseline：现有 Agent-based 金融模型（SFI-ASM）
  - 指标：叙事传播速度、泡沫幅度、崩盘时间
- **创新点：** 首个将叙事-信任-行为-资金流统一建模的系统
- **消融实验：** Narrative ON/OFF、KOL ON/OFF、Price Feedback ON/OFF

#### 方向 6：监管科技异常检测
- **适合期刊：** IEEE TKDE / ICIS 2025
- **实验设计：** 对比 ManipulationRiskAgent 与传统异常检测算法
- **Baseline：** Isolation Forest、OC-SVM、LSTM-VAE
- **评价指标：** Precision/Recall/F1 @ 不同风险阈值

---

### ResearchForge

#### 方向 7：AI 辅助科研假设生成（最佳 SCI）
- **适合期刊：** Nature AI Review / ACM CHI 2025
- **实验设计：**
  - Baseline：纯 LLM（GPT-4）+ RAG
  - 实验组：ResearchForge（HypothesisEngine + KG约束）
  - 任务：从 50 篇论文摘要生成可验证假设
  - 评价：假设新颖性（人工评估）、可验证性、KL 散度新颖性评分
- **消融实验：** KG 约束 ON/OFF、反事实推理 ON/OFF

#### 方向 8：主动学习实验设计
- **适合会议：** ICML 2025 / NeurIPS 2025
- **实验设计：** 对比主动学习循环 vs 随机实验选择
- **Baseline：** Random Search、Bayesian Optimization（传统）
- **评价指标：** 假设收敛速度、实验次数到假设验证

---

### PatentCaptor

#### 方向 9：创新检测算法
- **适合会议：** KDD 2025 / WWW 2025
- **实验设计：** 对比 Novelty Score 与现有 novelty detection 算法
- **Baseline：** BERT-ND、DeepSVDD、LOF
- **评价指标：** AUC-ROC、F1@K、MRR

#### 方向 10：会议挖掘
- **适合会议：** ACL 2025 / EMNLP 2025
- **实验设计：** 在自建数据集（会议录音+转写+专利标签）上评估
- **Baseline：** 关键词匹配、传统信息抽取
- **评价指标：** 专利点识别准确率、召回率