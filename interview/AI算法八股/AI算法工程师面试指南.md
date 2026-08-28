# AI 算法工程师面试指南
---

## 一、高频考察模块总览

```text
1. 数学基础（10%）
2. 机器学习基础（15%）
3. 深度学习基础（25%）★重点
4. 方向知识：CV / NLP / LLM（20%）
5. 工程与部署能力（15%）
6. 项目深挖（10%）
7. 手撕代码（贯穿全程）
```

---

## 二、深度学习基础（必考）

### Q1. Transformer 结构讲一遍？Q/K/V 的作用？为什么要除以 √d？

**结构：** Encoder-Decoder 架构。核心组件：Multi-Head Self-Attention + Feed-Forward Network + 残差连接 + LayerNorm。位置编码注入序列顺序信息。

**Q/K/V 作用：**
- Q（Query）：当前位置的"提问"向量
- K（Key）：被比较位置的"标签"向量
- V（Value）：被比较位置的实际"内容"向量
- Attention(Q,K,V) = softmax(QKᵀ/√d) V

**除以 √d 的原因：** 点积 QKᵀ 的方差随维度 d 线性增长。维度大时点积绝对值变大 → softmax 进入饱和区 → 输出趋于 one-hot → 梯度趋零。除以 √d 把方差归一化到稳定区间，保证梯度健康。

---

### Q2. Attention 和 Self-Attention 的区别？

- **Self-Attention：** Q/K/V 来自同一个序列，序列内部任意两位置互相 attend。用于建模序列内部依赖。
- **Cross-Attention：** Q 来自一个序列（如 Decoder 当前位置），K/V 来自另一个序列（如 Encoder 输出）。用于两个序列之间的对齐。
- 广义的 Attention 是一种机制（Q·K→权重→加权V），Self/Cross 是它的两种实例化。

---

### Q3. BatchNorm 和 LayerNorm 的区别？为什么 Transformer 用 LN？

| 维度 | BatchNorm | LayerNorm |
|---|---|---|
| 归一化维度 | 沿 batch 维归一化（每个特征通道统计） | 沿特征维归一化（每个样本统计） |
| 依赖 batch | 是，batch 小时不稳定 | 否，单样本即可 |
| 训练/推理差异 | 有（推理用 running mean/var） | 无 |
| 适合场景 | CNN（batch 大、尺寸固定） | RNN/Transformer（变长序列） |

**Transformer 用 LN 的原因：**
1. 序列长度可变，BN 沿 batch 统计不稳定
2. batch 通常较小，BN 统计量噪声大
3. NLP 中同一 batch 不同句子差异大，BN 反而破坏特征

---

### Q4. 过拟合怎么解决？

```text
数据侧：增加数据、数据增强、清洗噪声样本
模型侧：降低模型复杂度（层数/参数）、Dropout
训练侧：正则化（L1/L2/Weight Decay）、早停 Early Stopping
归一化：BatchNorm / LayerNorm
集成方法：Bagging、模型集成
```

**如何判断过拟合：** 训练 loss 持续下降但验证 loss 上升或不再下降，训练准确率远高于验证准确率。

---

### Q5. 梯度消失/爆炸的原因和解决方法？

**原因：** 多层链式求导，激活函数导数 <1（如 sigmoid 最大 0.25）→ 连乘后趋零；>1 则爆炸。

**解决：**
- 激活函数：ReLU、LeakyReLU（解决 sigmoid 导数小）
- 残差连接（ResNet）：梯度直连通路
- LayerNorm / BN：稳定每层输入分布
- 梯度裁剪（Gradient Clipping）：防爆炸
- 合适的初始化：Xavier、He 初始化
- 门控机制（LSTM/GRU）：缓解 RNN 梯度消失

---

### Q6. Adam 和 SGD 的区别？各自适合什么场景？

| 维度 | SGD | Adam |
|---|---|---|
| 机制 | 固定学习率 + 梯度 | 自适应学习率 + 动量（一阶+二阶矩估计） |
| 收敛速度 | 慢 | 快 |
| 调参难度 | 需精调 lr 和 momentum | 默认参数即可启动 |
| 泛化能力 | 通常更好 | 可能稍差（收敛过快到 sharp minima） |
| 适合场景 | 大规模训练精调、CV SOTA 收尾 | 快速实验、NLP、Transformer 预训练 |

实际中常用：**AdamW**（Adam + 解耦 weight decay），是 Transformer 训练标配。

---

### Q7. 学习率调度策略有哪些？

```text
Warmup：前 N 步线性上升，避免早期发散
Step Decay：每 N epoch 衰减一次（×0.1）
Cosine Annealing：余弦退火，平滑下降
Linear Decay：线性下降到 0
OneCycle：先升后降
ReduceLROnPlateau：验证指标不提升时衰减
```

Transformer 常见组合：**Warmup + Cosine Decay**。

---

### Q8. ReLU 为什么常用？有什么问题？

**优点：**
- 计算简单（max(0,x)）
- 缓解梯度消失（正区间梯度恒为 1）
- 稀疏激活（负区间为 0），类似生物神经元

**问题：**
- **神经元死亡**：输入持续为负 → 梯度恒为 0 → 权重不再更新
- 输出非零均值，可能影响下一层分布

**改进：** LeakyReLU、PReLU、ELU、GELU（Transformer 常用）、SwiGLU（LLaMA）。

---

### Q9. 交叉熵 vs MSE，分类为什么不用 MSE？

**交叉熵：** L = -Σ y·log(ŷ)，配合 softmax 时梯度为 (ŷ - y)，与误差成正比，收敛快。

**MSE 用于分类的问题：**
1. 配合 sigmoid/softmax 时梯度含导数项，输出接近 0 或 1 时梯度趋零 → 学习极慢
2. MSE 假设输出为高斯分布，分类标签是离散的，概率假设不匹配
3. 对错误分类的惩罚力度不够

结论：**分类用交叉熵，回归用 MSE**。

---

### Q10. 训练不收敛你会怎么排查？

```text
1. 数据：标签是否错乱、是否归一化、是否有 NaN/Inf、batch 是否全同标签
2. 学习率：太大发散 / 太小不动 → 试 1e-3 ~ 1e-5
3. 损失函数：是否选错（分类用 CE）
4. 激活和初始化：最后一层是否漏激活、初始化是否合理
5. 梯度：检查梯度范数，是否消失/爆炸，加 clip
6. 模型结构：是否有 bug（维度不匹配、参数未训练）
7. 数值稳定性：log 前加 eps、softmax 防 overflow
8. 过拟合：训练 loss 降但验证不降 → 加正则
```

排查顺序建议：**数据 → loss → lr → 梯度 → 结构**。

---

## 三、大模型方向（当前最热门）

### Q1. LLaMA 结构和标准 Transformer 区别？

| 组件 | 标准 Transformer | LLaMA |
|---|---|---|
| Norm | LayerNorm | **RMSNorm**（去均值中心化，计算更快） |
| 位置编码 | 绝对位置编码（sinusoidal/learned） | **RoPE**（旋转位置编码，相对位置） |
| 激活 | ReLU/GELU | **SwiGLU**（GLU 变体，效果更好） |
| Norm 位置 | Post-Norm | **Pre-Norm**（训练更稳） |
| Attention | 标准 MHA | **GQA / MQA**（LLaMA-2 起，KV 头共享降显存） |

---

### Q2. RoPE 位置编码原理？

**核心思想：** 通过旋转矩阵在 Q、K 上注入相对位置信息。

**公式：** 对 query 向量每两个维度一组，按位置 m 旋转角度 θ·m：

```
q'_2i   = q_2i · cos(mθ_i) - q_2i+1 · sin(mθ_i)
q'_2i+1 = q_2i · sin(mθ_i) + q_2i+1 · cos(mθ_i)
```

**优势：**
- 内积 q·k 自然包含相对位置 (m-n)
- 支持外推（长序列扩展）
- 不引入额外参数
- 比 ALiBi、绝对位置编码对长上下文更友好

---

### Q3. KV Cache 是什么？为什么能加速？显存占用怎么算？

**原理：** Decode 阶段每生成一个 token，前面所有 token 的 K、V 计算结果不变 → 缓存复用，避免重复计算。

**加速效果：** 每步只需算新 token 的 K/V 追加到 cache，时间复杂度从 O(n²) 降到 O(n)。

**显存占用估算：**
```
KV Cache = 2 × num_layers × num_kv_heads × head_dim × seq_len × batch × dtype_bytes
```
例如 LLaMA-7B，batch=1，seq=2048，FP16：
约 2×32×32×128×2048×2 ≈ 1GB（KV Cache 比模型权重还大！）。

**这就是为什么 PagedAttention、GQA/MQA 这么重要。**

---

### Q4. Prefill 和 Decode 两个阶段的区别？

| 维度 | Prefill | Decode |
|---|---|---|
| 输入 | 完整 prompt（长） | 单个新 token（短） |
| 计算量 | 大（一次性算所有 token） | 小（只算新 token） |
| 计算瓶颈 | Compute-bound（矩阵乘法） | Memory-bound（KV Cache 读取） |
| 并行度 | 高（token 间可并行） | 低（自回归逐 token） |
| 耗时分布 | 首字延迟 TTFT 主要来源 | 单 token 延迟 TPOT 主要来源 |

**生产优化重点：** Prefill 优化首 token 延迟，Decode 优化吞吐（连续批处理、GQA、PagedAttention）。

---

### Q5. LoRA 原理？QLoRA 又是什么？

**LoRA（Low-Rank Adaptation）：**
- 冻结原始权重 W，旁路加 ΔW = BA，其中 B∈R^(d×r)、A∈R^(r×k)，r << min(d,k)
- 训练只更新 A、B，参数量从 d×k 降到 (d+k)×r
- 推理时 W' = W + BA 可合并，无额外延迟

**为什么有效：** 预训练大模型的权重更新存在低本征秩，低秩近似即可达到接近全参微调的效果。

**QLoRA：**
- 在 LoRA 基础上，**原始权重用 4-bit 量化存储**（NF4 + 双重量化）
- LoRA 参数仍以 FP16/BF16 训练
- 单卡可微调 65B 模型，效果接近全参微调
- 核心技术：NF4 量化 + 分页优化器 + 双重量化

---

### Q6. RAG 完整链路？召回差怎么优化？

**标准链路：**
```text
用户问题 
  → Query 改写/扩展 
  → Embedding 编码 
  → 向量库召回 Top-K 
  → Rerank 重排序 
  → Prompt 拼接（context + question） 
  → LLM 生成 
  → 答案后处理/引用标注
```

**召回差优化方向：**

| 环节 | 优化手段 |
|---|---|
| 文档处理 | 切块策略（语义切分/标题层级）、metadata 标注、多粒度索引 |
| Query 侧 | Query 改写、HyDE、多路召回（向量+BM25+结构化） |
| Embedding | 换更强模型、领域微调 embedding、加入指令前缀 |
| 召回 | 提高 Top-K、混合检索、父-子文档召回 |
| Rerank | Cross-Encoder 重排（bge-reranker、Cohere） |
| 索引 | HNSW 参数调优、量化索引、多向量字段 |
| 生成 | Context 压缩、LongLLMLingua、分步回答 |

---

### Q7. Agent 工作流：ReAct、Function Call、多轮规划

**ReAct（Reasoning + Acting）：**
```
Thought: 我需要先查天气
Action: search_weather("北京")
Observation: 晴, 25度
Thought: 用户问的是出行建议，再查路况
Action: ...
```
LLM 边推理边调用工具，循环执行直到完成。

**Function Call：** 模型原生支持输出结构化函数调用（OpenAI/Anthropic/Qwen），比 ReAct 解析文本更稳定。

**多轮规划：**
- Plan-and-Execute：先规划任务列表再执行
- ReWOO：分离 planning 和 execution
- Tree of Thoughts：树形搜索多分支
- LangGraph / 自定义状态机：复杂工作流编排

---

### Q8. 幻觉是什么？怎么缓解？

**幻觉（Hallucination）：** 模型生成看似合理但与事实不符的内容。

**原因：**
- 训练数据含错误信息
- 模型本质是概率生成，倾向于"流畅"而非"正确"
- 长尾知识记忆不牢
- 过度泛化

**缓解手段：**
```text
1. RAG：引入外部知识库做依据
2. Prompt：要求"不知道就说不知道"、给出引用、CoT 分步推理
3. Decoding：降低 temperature、top-p、增加 repetition_penalty
4. 微调：领域数据 SFT、DPO/RLHF 对齐
5. 后处理：事实校验、引用校验、规则过滤
6. 多模型交叉验证 / Self-Consistency
```

---

### Q9. 大模型评估怎么做？

**分层评估体系：**

```text
1. 基础能力：MMLU、CMMLU、C-Eval、GSM8K、HumanEval
2. 对齐能力：MT-Bench、AlpacaEval、Arena（人类偏好）
3. 业务指标：
   - 准确率：人工标注 + LLM-as-Judge
   - 召回率：RAG 场景知识命中
   - 拒答率：该答没答 / 不该答乱答
   - 幻觉率：事实错误比例
   - 相关性：答案与问题的匹配度
   - 完整性：是否覆盖要点
4. 工程指标：TTFT、TPOT、吞吐、成本
5. 安全指标：越狱率、有害内容、隐私泄漏
```

**关键原则：** 离线 benchmark ≠ 线上效果，必须有业务自有评测集 + 人工抽检。

---

### Q10. vLLM 的 PagedAttention 解决了什么问题？

**传统问题：**
- 每个请求预分配连续 KV Cache（按 max_seq_len）
- 实际用不满 → 显存碎片严重、利用率低
- 连续批处理难以动态加入/移除请求

**PagedAttention 方案：**
- KV Cache 按固定大小 Block 分页存储（类似 OS 虚拟内存）
- 逻辑连续、物理分散，用 Block Table 映射
- 支持按需分配、共享（Prefix Cache、Beam Search 共享前缀）

**收益：**
- 显存利用率从 ~20% 提升到 ~96%
- 支持更高并发和更长上下文
- 连续批处理真正落地

---

## 四、CV 方向

### Q1. ResNet 为什么有效？

**问题：** 网络加深到一定程度，训练误差反而上升（退化问题，不是过拟合）。

**残差连接：** H(x) = F(x) + x，让网络学习残差 F(x) = H(x) - x。

**为什么有效：**
1. **梯度直连**：恒等映射分支梯度为 1，缓解梯度消失
2. **学习难度降低**：学残差比学恒等映射容易（恒等是 F=0 的特例）
3. **隐式集成**：等价于不同深度子网络的集成
4. **损失平面更平滑**：残差结构让优化更易收敛

---

### Q2. YOLO 系列演进和核心思想？

**核心思想：** 把检测当回归问题，一次前向输出所有框（One-Stage）。

**演进：**
| 版本 | 关键改进 |
|---|---|
| YOLOv1 | 划分 S×S 网格，每格预测 B 个框 |
| YOLOv2 | Anchor、BN、多尺度训练 |
| YOLOv3 | 多尺度预测（FPN）、Darknet53 |
| YOLOv4 | CSPNet、Mosaic 增强、CIoU |
| YOLOv5 | 工程化、Ultralytics 生态 |
| YOLOv6/v7 | RepVGG 重参数化、辅助头 |
| YOLOv8 | Anchor-Free、Decoupled Head、Ultralytics 统一框架 |
| YOLOv9/v10/v11 | PGI、NMS-free、更高效结构 |

**通用优势：** 速度快、端到端、适合实时检测。

---

### Q3. NMS 原理？Soft-NMS 了解吗？

**NMS（非极大值抑制）：**
1. 按置信度降序排序所有框
2. 取最高分框，删除与它 IoU > 阈值（如 0.5）的其他框
3. 重复直到处理完

**Soft-NMS：** 不直接删除重叠框，而是按 IoU 衰减其分数：
```
s_i = s_i * (1 - IoU(M, b_i))   # 线性衰减
# 或 s_i = s_i * exp(-IoU²/σ)   # 高斯衰减
```
适合密集目标场景（人群、车流）。

---

### Q4. mAP 怎么计算？IoU 是什么？

**IoU = 交集面积 / 并集面积**，衡量预测框与真实框的重合度。

**mAP 计算流程：**
1. 所有预测框按置信度排序
2. 逐个判断是否 TP/FP（IoU > 阈值且匹配到 GT 为 TP，否则 FP）
3. 计算 Precision-Recall 曲线
4. **AP = PR 曲线下面积**（VOC 用 11 点插值，COCO 用 101 点插值）
5. **mAP = 各类别 AP 的平均**

**COCO mAP：** 在 IoU 阈值 [0.5:0.05:0.95] 共 10 个阈值上取平均，更严格。

---

### Q5. 图像分割：语义分割 vs 实例分割

| 类型 | 任务 | 例子 |
|---|---|---|
| 语义分割 | 给每个像素打类别标签，**同类不区分实例** | 所有"人"像素都标为"人" |
| 实例分割 | 既要分类又要区分**不同实例** | 人1、人2 分别标不同颜色 |
| 全景分割 | 语义 + 实例合并，背景也分类 | 既有 stuff 又有 thing |

代表模型：U-Net（语义）、Mask R-CNN（实例）、Panoptic FPN（全景）。

---

### Q6. 数据增强策略？小目标检测难在哪？

**常用增强：**
- 几何：随机裁剪、翻转、旋转、缩放
- 颜色：HSV 抖动、ColorJitter
- 混合：Mosaic、MixUp、CutMix
- Copy-Paste：把目标抠到其他图
- 难例挖掘：对漏检样本重点训练

**小目标难点：**
1. 分辨率低 → 特征信息少
2. 经过多次下采样后特征几乎消失
3. Anchor 匹配困难（IoU 难达标）
4. NMS 容易被大目标抑制

**解决：** 高分辨率输入、FPN/PAN 多尺度特征、专门的小目标检测头、SAHI 切图推理。

---

## 五、机器学习基础

### Q1. LR 原理？为什么用 sigmoid？损失函数推导

**逻辑回归：** 线性回归 wᵀx + b，过 sigmoid 映射到 [0,1] 作为概率。

**为什么用 sigmoid：**
1. 输出在 [0,1] 可解释为概率
2. 与伯努利分布的极大似然推导一致
3. 处处可导、单调
4. 与交叉熵损失配合，梯度为 (ŷ - y)·x，形式优美

**损失函数推导：**
- 似然：L = Π p(y|x) = Π ŷ^y (1-ŷ)^(1-y)
- 对数似然取负：L = -Σ[y·logŷ + (1-y)·log(1-ŷ)]
- 对 w 求导：∂L/∂w = Σ(ŷ - y)·x

---

### Q2. 决策树 / XGBoost / LightGBM 原理对比

| 模型 | 分裂准则 | 树生成方式 | 关键特性 |
|---|---|---|---|
| 决策树 | 信息增益 / Gini | 贪心，一次性生成 | 简单可解释 |
| GBDT | 负梯度拟合 | 串行加法模型 | 提升法，拟合残差 |
| XGBoost | 二阶泰勒近似增益 | 预排序 + 列块并行 | 正则化、近似分裂、缺失值处理 |
| LightGBM | Leaf-wise 增益 | **直方图算法** + Leaf-wise 生长 | 训练更快、内存省、类别特征原生支持 |

**LightGBM 核心优化：**
- Histogram：连续值分桶，分裂复杂度 O(n) → O(bins)
- Leaf-wise：选增益最大的叶子分裂（比 Level-wise 更深但更准）
- GOSS：保留大梯度样本 + 随机小梯度
- EFB：合并互斥特征降维

---

### Q3. SVM 对偶问题和核技巧

**对偶问题：** 原 1/2||w||² 约束 yᵢ(wᵀxᵢ+b)≥1 → 拉格朗日对偶 → max α 1/2 Σαᵢαⱼyᵢyⱼxᵢᵀxⱼ - Σαᵢ

**优势：** 只依赖内积 → 引入核技巧，w = Σαᵢyᵢxᵢ 只需支持向量。

**核技巧：** K(x,z) = φ(x)ᵀφ(z)，不需显式计算高维映射。常见核：
- 线性：K = xᵀz
- 多项式：(xᵀz + 1)^d
- RBF：exp(-γ||x-z||²)

---

### Q4. 类别不平衡怎么处理？

```text
数据侧：
- 过采样少数类（SMOTE、ADASYN）
- 欠采样多数类（EasyEnsemble）
- 数据合成（mixup）

算法侧：
- class_weight（惩罚错分少数类）
- Focal Loss（降低易分样本权重）
- 修改阈值（precision-recall 平衡）

评估侧：
- 不看 Accuracy，看 F1、AUC、PR-AUC
- 分层采样保证训练/验证分布一致
```

---

### Q5. AUC 含义？和 PR 曲线的区别？

**AUC：** ROC 曲线下面积，等价于"随机正样本得分高于随机负样本的概率"。

- AUC=0.5 随机，=1 完美
- 优点：对类别不平衡不敏感，对阈值不敏感

**ROC vs PR：**
| 指标 | 横轴 | 纵轴 | 适用场景 |
|---|---|---|---|
| ROC | FPR=FP/(FP+TN) | TPR=Recall | 类别均衡 |
| PR | Recall | Precision | **类别极不平衡时更敏感** |

当负样本远多于正样本（如点击率 0.1%），PR 曲线更能反映实际效果。

---

### Q6. 特征工程怎么做？特征穿越怎么发现？

**特征工程：**
```text
数值：归一化、标准化、对数变换、分箱
类别：One-Hot、Target Encoding、Embedding
时间：周期、窗口聚合、滑动统计
交叉：特征组合、统计交互
```

**特征穿越（Data Leakage）：** 训练时用了未来才有的信息。

**排查方法：**
- 检查每个特征的时间戳是否 ≤ 样本时间
- 检查是否用了包含 label 的统计量（如全量均值）
- 时间序列严格按时间切分训练/验证
- 检查"看似合理但含未来"的特征（如 7 日均销量，当日本身被算进去）

---

## 六、手撕代码（算法题）

### LeetCode 高频

- 数组双指针：两数之和、三数之和、接雨水
- 链表：反转、合并有序、环检测
- 二叉树：层序遍历、最近公共祖先
- 动态规划：最长子序列、编辑距离
- 字符串：滑动窗口

### 手撕 ML 算法参考实现

#### NMS 实现

```python
def nms(boxes, scores, iou_threshold=0.5):
    # boxes: [N, 4] (x1, y1, x2, y2)
    keep = []
    order = scores.argsort()[::-1]
    while order.size > 0:
        i = order[0]
        keep.append(i)
        if order.size == 1:
            break
        ious = iou(boxes[i], boxes[order[1:]])
        order = order[1:][ious < iou_threshold]
    return keep

def iou(box, boxes):
    # box: [4], boxes: [M, 4]
    x1 = np.maximum(box[0], boxes[:, 0])
    y1 = np.maximum(box[1], boxes[:, 1])
    x2 = np.minimum(box[2], boxes[:, 2])
    y2 = np.minimum(box[3], boxes[:, 3])
    inter = np.maximum(0, x2 - x1) * np.maximum(0, y2 - y1)
    area1 = (box[2] - box[0]) * (box[3] - box[1])
    area2 = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    return inter / (area1 + area2 - inter + 1e-6)
```

#### Softmax（带数值稳定）

```python
def softmax(x, axis=-1):
    x = x - np.max(x, axis=axis, keepdims=True)  # 防 overflow
    e = np.exp(x)
    return e / np.sum(e, axis=axis, keepdims=True)
```

#### CrossEntropy

```python
def cross_entropy(pred, target):
    # pred: [N, C] (logits), target: [N]
    pred = softmax(pred)
    return -np.mean(np.log(pred[np.arange(len(target)), target] + 1e-9))
```

#### Scaled Dot-Product Attention

```python
def attention(Q, K, V, mask=None):
    # Q: [B, H, N, d], K: [B, H, M, d], V: [B, H, M, d]
    d = Q.shape[-1]
    scores = Q @ K.transpose(-2, -1) / np.sqrt(d)  # [B, H, N, M]
    if mask is not None:
        scores = scores + mask  # -inf for padding
    weights = softmax(scores, axis=-1)
    return weights @ V  # [B, H, N, d]
```

#### K-Means

```python
def kmeans(X, k, epochs=100):
    n = X.shape[0]
    idx = np.random.choice(n, k, replace=False)
    centers = X[idx]
    for _ in range(epochs):
        # 分配
        dist = np.linalg.norm(X[:, None] - centers[None], axis=2)  # [n, k]
        labels = dist.argmin(axis=1)
        # 更新
        new_centers = np.array([X[labels == j].mean(0) for j in range(k)])
        if np.allclose(centers, new_centers):
            break
        centers = new_centers
    return labels, centers
```

#### BM25

```python
import math
def bm25(query_tokens, doc_tokens, idf, avgdl, k1=1.5, b=0.75):
    score = 0
    dl = len(doc_tokens)
    for q in query_tokens:
        f = doc_tokens.count(q)
        score += idf[q] * f * (k1 + 1) / (f + k1 * (1 - b + b * dl / avgdl))
    return score
```

---

## 七、工程部署问题

### Q1. 模型上线流程完整说一遍？

```text
1. 训练模型 → 保存 checkpoint
2. 导出格式 → ONNX / TensorRT Engine / Safetensors
3. 推理引擎加载 → ONNX Runtime / TensorRT / vLLM
4. 服务化封装 → FastAPI / Triton / vLLM Server
5. 容器化 → Dockerfile + 镜像
6. 部署上线 → 裸机 / K8s，挂 GPU
7. 压测 → latency、QPS、显存、OOM
8. 监控 → Prometheus + Grafana，日志收集
9. 灰度 → 流量切分，逐步放量
10. 数据回流 → 线上 badcase 回流迭代
```

---

### Q2. 训练效果好在线上差，可能原因？

```text
1. 分布不一致：训练数据 ≠ 线上数据分布
2. 预处理不一致：归一化、resize、颜色通道训练/部署不一致
3. 数据泄漏：训练时用了未来信息
4. 标注质量：训练标签噪声大
5. 样本偏差：训练集覆盖不全，线上有新场景
6. 模型过拟合：训练集 memorize 而非 generalize
7. 在线分布漂移：时间演进数据分布变化
8. 评估指标偏差：离线指标与业务目标不一致
```

**排查方法：** 线上样本回流 → 离线复现 → 对比分布 → 检查预处理 pipeline。

---

### Q3. ONNX / TensorRT 的作用和区别？

详见 [ONNX Runtime vs TensorRT Runtime 区别](#)。

| 维度 | ONNX Runtime | TensorRT |
|---|---|---|
| 定位 | 通用推理引擎 | NVIDIA GPU 专用 |
| 跨平台 | 强 | 弱（绑定 GPU/CUDA/TRT 版本） |
| 性能 | 较高 | NVIDIA 上极致 |
| 部署难度 | 低 | 高（需 build engine、配 profile） |
| 适合 | 跨平台、快速上线 | 生产高性能、低延迟 |

折中方案：ONNX Runtime + TensorRT Execution Provider。

---

### Q4. 推理加速手段：量化、剪枝、蒸馏、批处理

| 手段 | 原理 | 收益 | 风险 |
|---|---|---|---|
| 量化 | FP32→INT8/INT4 | 显存↓4-8倍、速度↑2-4倍 | 精度损失，需校准 |
| 剪枝 | 移除冗余权重/通道 | 参数↓、推理↓ | 结构改动、需 fine-tune |
| 蒸馏 | 大模型教小模型 | 小模型接近大模型效果 | 训练成本高 |
| 批处理 | 多请求合并 | GPU 利用率↑、吞吐↑ | 增加单请求延迟 |
| 算子融合 | Conv+BN+ReLU 合并 | Kernel 启动↓、显存读写↓ | 框架自动做 |
| KV Cache 优化 | PagedAttention、GQA | 显存↓、并发↑ | 仅 LLM |

---

### Q5. 服务高并发怎么处理？

```text
1. 动态批处理：短窗口合并请求（Continuous Batching for LLM）
2. 多实例：多 GPU / 多 Pod 水平扩容
3. 限流：令牌桶 / 漏桶，保护服务不雪崩
4. 队列：Kafka / Redis 缓冲突发流量
5. 缓存：相同 prompt 结果缓存（Prefix Cache）
6. 异步：长任务转异步 + 轮询/SSE 返回
7. 量化降显存 → 单卡塞更多并发
8. K8s HPA 自动扩缩容
```

---

### Q6. Docker/K8s 基本使用

**Docker 核心命令：**
```bash
docker build -t my-model:1.0 .
docker run --gpus all -p 8000:8000 my-model:1.0
docker push registry/my-model:1.0
```

**Dockerfile 要点：**
- 多阶段构建（builder + runtime）减小镜像
- 固定 CUDA / cuDNN / 框架版本
- 用 `.dockerignore` 排除大文件

**K8s 核心概念：**
- Deployment：管理 Pod 副本
- Service：网络入口
- HPA：CPU/GPU 利用率自动扩缩容
- ConfigMap / Secret：配置和密钥
- GPU 调度：nodeSelector + nvidia.com/gpu 资源

---

### 边缘部署补充（相机/手机）

| 设备 | 推荐方案 |
|---|---|
| Android 手机 | TFLite、NCNN、MNN |
| iOS 手机 | Core ML、TFLite |
| 安防/工业相机 | TensorRT（Jetson）、RKNN、OpenVINO |

关键点：**INT8 量化 + 轻量骨干 + 专用格式转换 + 真机压测**。

---

## 八、项目环节（最关键）

面试官会顺着你的项目连环追问，常见套路：

```text
项目背景 → 你的贡献 → 技术选型为什么这么选 
→ 效果指标是多少 → 怎么提升的 → badcase 分析
→ 如果重新做你会怎么改进 → 扩展性问题（量级×100怎么办）
```

### 准备建议

- 每个 STAR 写清楚：背景、方案、量化结果（mAP 从 X 提升到 Y）
- 至少准备 1 个能讲透的失败/困难案例
- 熟悉自己项目的每个细节，防止"简历注水被戳穿"
- 准备好"如果重做"和"量级×100"两个延展问题

### 项目描述结构模板

```text
【背景】业务问题是什么，规模多大
【我的角色】负责哪部分
【方案】技术选型 + 为什么这么选（对比过哪些方案）
【过程】数据怎么处理、模型怎么调、问题怎么解决
【结果】量化指标（精度/延迟/吞吐/业务指标）
【反思】如果重做会怎么改
```

---

## 九、HR 面 & 反问

### 高频问题

- 为什么转/选 AI 方向？
- 职业规划？
- 最高兴/最有挫败感的事？
- 离职原因（社招）？
- 期望薪资？

### 反问推荐

- 团队目前的核心业务和技术栈？
- 算法在业务中落地的方式和数据闭环？
- 新人成长路径和 mentor 机制？
- 团队近期最大的挑战是什么？

---

## 十、复习优先级建议（按时间分配）

```text
时间充裕（2周+）：
深度学习基础 30% → LLM/CV方向 30% → 代码题 25% → 项目梳理 15%

时间紧张（3天）：
手撕代码高频题 → Transformer 全家桶 → 自己项目复盘 → 八股扫盲
```

---

## 附录：简历项目描述示例

❌ 差的写法：

> 使用 YOLO 完成目标检测。

✅ 好的写法：

> 构建某类目标检测系统，完成数据清洗、标注规范、YOLO 训练和 ONNX/TensorRT 部署；
> 通过数据增强和难例挖掘将 mAP 从 72% 提升到 81%，
> TensorRT 推理延迟从 45ms 降低到 18ms。

体现能力：数据能力 + 算法能力 + 工程能力 + 性能优化 + 结果意识。

---

## 附录：高频公式速查

### Transformer Attention
```
Attention(Q,K,V) = softmax(QKᵀ/√d_k) V
```

### LayerNorm
```
LN(x) = γ · (x - μ) / √(σ² + ε) + β
```

### RMSNorm（LLaMA）
```
RMSNorm(x) = x · γ / √(mean(x²) + ε)
```

### 交叉熵
```
L = -Σ y · log(ŷ)
```

### LoRA
```
h = Wx + ΔWx = Wx + BAx,  B∈R^(d×r), A∈R^(r×k), r << min(d,k)
```

### IoU
```
IoU = |A ∩ B| / |A ∪ B|
```

### KV Cache 显存
```
2 × layers × kv_heads × head_dim × seq_len × batch × dtype_bytes
```

### Focal Loss
```
FL(p_t) = -α_t (1 - p_t)^γ log(p_t)
```
