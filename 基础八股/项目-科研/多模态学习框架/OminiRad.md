# OmniRad 面试复盘手册（代码事实版）

> 本文所有结论都来自仓库源码，标注了文件与行号，可直接在面试中"指哪打哪"。
> 核心文件：`minigpt4/models/omnirad.py`(1700 行)、`minigpt4/models/minigpt_v2.py`、`minigpt4/models/minigpt_base.py`、`minigpt4/datasets/datasets/unified_us_dataset.py`、`tools/dataset_utils.py`、`eval_scripts/model_evaluation.py`。

---

## 0. 30 秒版本（开场自述骨架）

> OmniRad 是一个**以 LLaMA-3-8B 为唯一推理中枢**的统一医学多模态框架。它不改 LLM 的生成范式和输出空间，而是**把"结构化预测"降维成"生成一个特殊 token"**：模型在自回归过程中吐出 `<SEG>` / `<BOX_S/M/L>` / `<LOC>`，训练时取这些 token 位置的最后一层隐状态，分别接一个 SAM 掩码解码器和几个轻量回归头，从而在**同一个 token 流里**同时产出报告文本和像素级/框级结果。
>
> 视觉侧是**双分支非对称**的：EVA-ViT-G 的特征 4 合 1 后投影成 256 个 token 进入 LLM 序列（参与语义推理）；SAM ViT-H 的密集特征**不进 LLM**，只作为 mask decoder 的"图像条件"被按需调用。这种设计让 8B 模型的上下文不被 64×64 的密集网格撑爆，同时保住分割的空间精度。
>
> 创新点落在两个"不固定"上：**病灶数量不固定** → 用变长 `<SEG>` 序列 + 每个 token 一路 mask query；**框尺度差异大** → 按 GT 面积比分 S/M/L 三档，三套独立回归头（权重 2.0/1.2/1.0）。另外用 mask↔box 几何一致性做跨任务正则。

---

## 1. 必须背下来的数字（面试官最爱抽查）

| 项 | 值 | 出处 |
|---|---|---|
| 图像分辨率 | 448×448，patch 14 → **32×32=1024 patch** | `blip_processors.py:118-126` |
| 视觉 token 数 | 去 CLS 后 1024 → **4 合 1 = 256 个**，每 token 5632 维 | `minigpt_v2.py:89-91` |
| 投影层 | `Linear(5632 → 4096)` | `minigpt_v2.py:67` |
| LLM | LLaMA-3-8B，hidden 4096，上下文 7800 | `omnirad_llama3.yaml:14-23` |
| LoRA | r=64, α=16（scale=0.25），只挂 `q_proj`/`v_proj`，dropout 0.05 | `train_configs/...yaml:38-42` |
| 特殊 token | 5 个：`<SEG> <BOX_S> <BOX_M> <BOX_L> <LOC>` | `omnirad.py:415-417` |
| SAM 输入 | **512×512**（不是 1024，为省显存把 pos_embed 从 64×64 双三次插值到 32×32） | `omnirad.py:102-112` |
| SAM 输出 | `(B,256,32,32)` → 上采样到 `(B,256,64,64)` → decoder 4× 上采样 → 256×256 logits | `omnirad.py:566-569` |
| SEG 投影 | `4096 → 512 → 256`（对齐 SAM prompt 维度） | `omnirad.py:455-459` |
| 回归头 | `Linear(4096,512)+GELU+Linear(512,4)`；box 头多一个 `Linear(512,64)` 类别支路 | `omnirad.py:270-307` |
| 损失权重 | text 1.0 / det 1.0 / loc 1.0 / seg_bce 1.0 / seg_dice 0.5 / cardinality 0.5 / cons_mb 0.1 / 尺度 2.0:1.2:1.0 | `omnirad.py:330-345` + `finetune.yaml:74-89` |
| 训练超参 | lr 2e-5，warmup 2000 step，wd 0.05，grad clip 1.0，AMP fp16，100 epoch，3×3090，bs 2/卡=6 | `finetune.yaml:202-238` |
| 数据混合 | indiana 25 / kvasir 23 / group_us 17 / slake_vqa 10 / grounding 10 / radvqa 8（合计 93） | `finetune.yaml:111-190` |
| 尺度分档阈值 | 面积比 <1% → S；1~10% → M；>10% → L | `tools/dataset_utils.py:92-103` |
| 推理开销 | **两段前向**（generate + 带 hidden_states 的重算），约 2× prefill | `omnirad.py:571-967` |
| 可训练参数 | LoRA≈34M + heads/投影≈10M + **embedding+lm_head≈1.05B**（resize 后被强制设为可训） | `omnirad.py:543-557` |

---

## 2. 架构：多模态特征到底怎么"交互"

### 2.1 关键事实：只有一条视觉流进入 LLM

很多人（包括面试官）会默认"双塔特征都进 LLM 做 cross-attention"。**这里不是**：

```
图像 ──┬─ EVA-ViT-G(冻结) ─ 4合1 ─ Linear5632→4096 ─┐
       │                                            ├─ 拼进 LLaMA 序列(前缀)
       │                                            │
       └─ SAM ViT-H(冻结) ── 256×64×64 密集特征 ──┐ │
                                                  ↓ │
                              <SEG> 隐状态 ── SEG投影 ──→ SAM MaskDecoder ──→ 掩码
```

- **交互点一（语义级）**：视觉 token 与文本 token 在 LLaMA 的**同一个因果注意力序列**里，靠 prompt 里的 `<Img><ImageHere></Img>` 占位符决定插入位置（`minigpt_base.py:144-158` `get_context_emb` / `prompt_wrap`）。这是"early fusion + prefix"范式，交互深度 = 32 层 self-attention，没有额外的 cross-attention 模块。
- **交互点二（几何级）**：LLM 在 `<SEG>` 位置的隐状态被当作 **SAM 的 sparse prompt**（等价于"点/框提示"的 256 维 embedding），与 SAM 的密集图像特征在 mask decoder 里做**双向 cross-attention**（SAM 原生的 two-way transformer，2 层）。所以"语言→像素"的通道是 `hidden_state → prompt`，不是 `hidden_state → 逐像素 logits`。这正是 LISA 的 embedding-as-mask 思路。
- **交互点三（尺度级）**：`<BOX_*>` / `<LOC>` 的隐状态直接过 MLP 回归 4 维归一化坐标，**完全不看** SAM 特征。所以框的精度上限由 LLM 的视觉 token（256 个、每个覆盖 28×28 像素）决定——这是后面"框精度不如分割"的根因，也是面试可以主动承认的 trade-off。

> **一句话回答"多模态怎么交互"**：文本和视觉在 LLM 内做 early-fusion 全序列注意力；结构化输出则反向用 LLM 的隐状态去"提示"冻结的 SAM，形成 language-to-pixel 的解码通道。两路视觉特征按"需要语义"还是"需要几何"分工。

### 2.2 视觉 token 化为什么是 4 合 1

`image_embeds[:, 1:, :]` 丢掉 CLS，然后 `view(bs, pn/4, hs*4)`——把**相邻 4 个 patch 的特征在通道维拼接**（不是平均池化）。所以：

- token 数 1024 → 256，序列长度降 4 倍（对 8B 模型是救命操作，KV cache 与 attention 都是平方级）；
- 但**信息没丢**，只是从"空间分辨率"换成"通道宽度"（5632 维），再由 `llama_proj` 压回 4096。这是 MiniGPT-v2 的原设计，等价于 patch merging（Swin 的做法）。
- 代价：单 token 感受野 28×28 像素，**小病灶在 token 化后可能只剩 1~2 个 token 的响应**，这也解释了为什么要靠 SAM 分支补几何、为什么要按尺度分三档头。

### 2.3 Token 级路由：一张表讲清

| 生成的特殊 token | 走哪个头 | 输出 | 训练监督 | 代码 |
|---|---|---|---|---|
| 普通文本 token | LM head | 报告/VQA 文本 | 自回归 CE | `omnirad.py:1516-1548` |
| `<SEG>`（可 K 个） | `seg_projector` → SAM `mask_decoder` | 256×256 掩码 logits | BCE(2.0) + Dice(0.5) + 异方差不确定性(0.1) | `1355-1472` |
| `<BOX_S/M/L>` | `box_heads[scale]` | 4 维归一化框 | 按尺度加权的 L1（2.0/1.2/1.0） | `1221-1295` |
| `<LOC>` | `loc_head` | 4 维框 (+30 类解剖 logits) | L1（解剖 CE 未实现，见 §11） | `1297-1353` |

**路由是"硬路由 + 软训练"**：
- 路由决策由 LLM 的 next-token 概率决定（**硬**，不可微地选择头）；
- 但"该不该吐这个 token"由 CE 监督（**软**，梯度通过 token 概率回传）；
- 所以路由能力本质是**语言模型的格式遵循能力**，不是 MoE 的门控网络。没有 load balance、没有 gating、没有 expert capacity——被问到"和 MoE 的区别"要能立刻答这句。

### 2.4 训练期与推理期的隐状态对齐（最容易被追问的细节）

- **训练**：一次 forward，`output_hidden_states=True`，用 `targets == token_id` 找到特殊 token 的位置，取 `hidden_states[-1][b, pos]`（`1027-1061`）。注意这是**已经消费了该 token 之后**的隐状态（因果 LM 的语义），不是"预测该 token 的那个状态"。
- **推理**：`generate` 结束后，把**生成的 token 重新 embed**，与 prompt embedding 拼接，**再跑一遍 forward**，同样取该位置的隐状态（`930-967`）。
- **一致性**：两条路径取的都是"该 token 所在位置的最后一层隐状态"，因此**训练/推理口径一致**，这是这套设计能 work 的前提。代价是推理多一次 prefill。
- **为什么不用 KV cache 只算新增部分**：理论上可以（generate 时把 hidden_states 存下来），但 `transformers.generate` 不暴露每步 hidden state，作者选择了"重算一遍"的工程妥协。**这是最容易被问的优化点**（见 §10）。

### 2.5 冻结策略与显存账

| 模块 | 状态 | 说明 |
|---|---|---|
| EVA-ViT-G | 冻结 | 但配置里开了 `use_grad_checkpoint: True`（对冻结塔无意义，纯开销） |
| SAM image encoder | 冻结 + `no_grad` | 每个 step 仍要 forward 一次（batch 内只算一次，复用给所有 `<SEG>`） |
| SAM prompt_encoder + mask_decoder | **可训练** | 约 4M，这是"分割能迁移到超声/内镜"的关键 |
| LoRA (q,v) | 可训练 | ≈34M |
| llama_proj / seg_projector / 各头 | 可训练 | ≈10M |
| embed_tokens + lm_head | **强制可训练** | `_set_output_embeddings_trainable`，vocab 128k×4096 → **≈1.05B** |

> 显存瓶颈的真正来源不是 SAM，是**词表两端的 1.05B 可训练参数**（fp32 主权重 + Adam 状态 ≈ 12GB 起）。面试可以主动说："后续优化会冻结 lm_head、只训新增的 5 行 embedding（用 hook 把梯度 mask 掉），能省 10GB+ 显存，允许把 batch 从 2 提到 6。"

---

## 3. 预处理管线（有 3 个隐藏坑，务必自己先知道）

**训练侧**（`blip_processors.py:71-110`）：
```python
RandomResizedCrop(448, scale=(0.5, 1.0), bicubic) → ToTensor → ImageNet mean/std
```
**评估侧**（`:113-135`）：`Resize((448,448))` —— 直接**拉伸**，不保持长宽比、不 padding。

**掩码与框**（`unified_us_dataset.py:98-116`）：单独从磁盘读原图尺寸的 PNG，**不做任何几何变换**；框是**原图像素坐标**。

### 坑 1：训练/评估预处理不一致（最经典的掉点原因）
`RandomResizedCrop(scale 0.5~1.0)` 会**随机裁剪 + 缩放**，而 GT 掩码/框对应的是**完整原图**。于是：
- 视觉塔看到的是"局部放大的一块"，监督信号说的是"整张图的第 3 个病灶" → **dense 任务的输入-标签几何不对齐**；
- 评估时换成 Resize（无裁剪），输入分布与训练不同 → 推理端"看起来更模糊/更完整"，模型没见过。

这在分类任务里只是正则，在**分割/检测里是标签噪声**。正确做法：dense 数据集改用 `Resize + pad`（保持长宽比）+ 同步变换 mask/box，或至少把 `min_scale` 提到 0.9。

### 坑 2：框归一化用的常量是 448，而不是图像真实宽高
`_compute_det_loss` 里 `gt_bbox / self.img_size`（`1283`），`self.img_size=448`（固定常量）。但 GT 框是**原图像素坐标**。以 Kvasir 一张 800×600 的图为例，`x2=700 → 700/448 = 1.56 → clamp(0,1) → 1.0`：**右侧的框全部被压到右边界**，模型学到的是"框贴边"，推理时 `pred*448` 又变回 448，IoU 直接崩。
> 这是我认为**代码里最值得改的一处**，也是"推理阶段效果不好"的头号可疑点。修法：用 `samples["image_size"]` 逐样本归一化（数据集已经把真实宽高传进来了 `unified_us_dataset.py:87`），并在 generate 时用同尺寸反归一化。

### 坑 3：一个标量同时归一化 x 和 y
非方形图像上，用同一个 448 除 x 与 y 会让"归一化后的面积比"失去物理意义，与 S/M/L 的分档阈值（面积比 1%/10%）口径不一致，尺度桶标签会抖。

---

## 4. 损失函数全景

```
L = 1.0·L_text
  + 1.0·L_det   (按尺度加权 L1: S×2.0, M×1.2, L×1.0)
  + 1.0·L_loc   (L1)
  + 1.0·L_seg   (内部已含 1.0·BCE + 0.5·Dice + 0.1·L_unc)
  + 0.1·L_cons  (mask 紧致框 vs 预测框 的 L1)
  + 0.5·CardinalityPenalty   ← 标量常数，无梯度，见下
```

工程细节（这些都是加分项，面试官问"训练稳定吗"就答这些）：
1. **CE 在 fp32 手算**，且 `logits.nan_to_num(posinf=1e4, neginf=-1e4)`（`1516-1518`）——fp16 AMP 下 logits 溢出会让 loss 变 NaN 并污染梯度。
2. **非法 label id 清洗**：`labels >= vocab_size` 或负数非 -100 → 一律改 -100（`1525-1537`），防止 CUDA gather 越界产生 NaN。这是新增特殊 token + resize embedding 时最容易踩的坑。
3. **空 answer 保护**：全 -100 时返回 0 loss 而非 NaN（`1539-1548`）；`preparing_embedding` 里空答案替换成 `"."`（`minigpt_base.py:343-354`）。
4. **aux loss 逐个 NaN 检查**并置零（`1108-1119`）；总损失 `>50` 时 clamp（`1609-1612`）；text_loss 为 NaN 时返回 NaN 让外层 GradScaler 捕获并 skip step（`1569-1596`，注释解释了为什么不能返回 0）。
5. **不确定性损失的实际形式**（`1433-1445`）：
   `log_var.clamp(-4,4)` → `σ² ∈ [0.018, 54.6]` → `inv = 1/(2σ²+1) ∈ [0.009, 0.53]` → `weighted_bce = (bce*inv).mean() + 0.5*log_var.mean()`。
   **注意：这里是对整个 batch 的标量 BCE 做加权，而不是逐像素**（`bce_loss` 是 `binary_cross_entropy_with_logits` 的 mean 标量），所以"逐像素不确定度"实际上退化成了"整图置信度缩放"。这是一个**实现与叙事不完全一致**的地方，被深挖时要能承认。</br>
   另外 uncertainty head 的输入是 `masks`（logits，未 sigmoid），单通道 1→128→1 卷积，感受野 3×3，**几乎无空间上下文**。

---

## 5. 训练链路

```
JSON(unified schema) 
  → Dataset.__getitem__: 每帧随机抽 1 个任务（report/seg/det/refer/identify/vqa）
  → 拼 prompt: "[INST] <Img><ImageHere></Img> {task_prompt} [/INST]"
         （LLaMA-3 下由 _to_chat_format 改写成 header 格式，minigpt_base.py:106-142）
  → collater: 框按 batch 内 max K 右侧零填充 + box_padding_mask
  → preparing_embedding: prompt_wrap 把 256 个视觉 token 插到 <ImageHere> 处
  → forward: labels 只在 answer 段有值（-100 屏蔽 prompt）
  → 抽特殊 token 隐状态 → 4 个辅助损失 → 反向
```

要点：
- **"多任务"其实靠数据侧的任务随机采样**（`unified_us_dataset.py:173` `random.choice(available_tasks)`），不是多任务头；同一帧在不同 epoch 会被当成不同任务，天然做了数据增广。
- **数据集混合用 `sample_ratio` 相对权重**（`runner_base.py:594-600` MultiIterLoader）。README 说"temperature-2 采样"，但代码里是**直接用 ratio 作为迭代权重**，没有温度参数——这是个可以主动澄清的小口径差异。
- **验证集选模型用 `cardinality_acc`**（`omnirad_task.py:86-106`）：即 `pred_seg_count == GT_K` 的比例。**问题**：它和 Dice/IoU 弱相关，可能选出"数量对但掩码烂"的最优 ckpt。建议改成任务指标加权（Dice + IoU + BERT-Sim）。
- **课程学习是死代码**：`finetune.yaml` 有 `curriculum_epochs: 8`，`runner_base.py:374-392` 会 `getattr(model,'curriculum_epochs',0)`，但 `OmniRad.__init__`/`from_config` 从未接收该参数，也没有 `set_curriculum_phase` 方法 → **永远不生效**。

---

## 6. 推理链路（两段前向）

```
① encode_img(image)               → 256 视觉 token        [EVA，1 次]
② get_context_emb(prompt, img)    → 拼接 prompt embedding
③ llama.generate(inputs_embeds)   → 生成 token 序列（含特殊 token）
④ 若序列中出现任一特殊 token：
     encode_dense_image(image)    → SAM 密集特征 [1 次，batch 内共享]
     gen_embeds = embed(outputs)
     llama(inputs_embeds=[prompt; gen], output_hidden_states=True)  → 第二段
     对每个特殊 token 位置调对应头
⑤ raw_text 中把 <BOX>/<LOC> 替换成 <LOC>{<x1><y1><x2><y2>}（像素坐标），供评估正则解析
```

坑（都在 §10 展开）：
- `stopping_criteria` **构造了但没传给 `generate`**（`622-624` 构造，`644-655` 调用时没传）→ 停止完全依赖 `generation_config.eos_token_id`。LLaMA-3 训练用的结束符是 `<|eot_id|>`(128009)，若 config 里只有 `<|end_of_text|>`(128001)，模型会**一直生成到 max_new_tokens=200**。
- `seg_count` 是在**整条输出序列上数 token**（`732`），**包含 EOS 之后的垃圾 token** → 结合上一条，会产生"幻影 `<SEG>`"和多余掩码。修法：先按第一个 EOS 截断 `outputs` 再做一切统计。
- batch 推理时 prompt 是**左填充**（`640`），`position_ids` 在部分 transformers 版本下由 `cache_position` 推出而非 attention_mask 累积 → 填充样本的位置编码可能偏移。**验证方法：bs=1 与 bs=8 对同一张图跑，比 BERT-Sim/IoU 差异。**

---

## 7. 评估链路与指标口径（防守重点）

| 任务 | 实现 | 口径细节 |
|---|---|---|
| 报告生成 BERT-Sim | `metrics.py:44-48` | **`paraphrase-MiniLM-L6-v2` 的余弦相似度**，不是临床 BERT；好处是与 MiniGPT-Med 基线同口径可比 |
| BLEU-4 / ROUGE-L | `metrics.py:489-606` | 纯 Python 实现（n-gram 精度 + BP；LCS） |
| CheXbert-F1 | regex 标签器 + 否定检测 | 14 类胸片标签，超声上意义有限（README 已注明） |
| 检测/指代 IoU | `model_evaluation.py:503-568` | **对每个 GT 框取与所有预测框的最大 IoU，再帧内平均** → 多预测不受惩罚（只被 cardinality 间接惩罚） |
| 分割 Dice | `metrics.py:309-383` | 预测与 GT 各自**取并集**后算 Dice（规避实例顺序问题）；预测缺失记 0；双空记 1 |
| Identify Acc | `metrics.py:390+` | 类别字符串精确匹配 |

**三个必须主动交代的口径问题**（不讲会被抓）：
1. IoU 用"贪心 best-match"，没有 FP 惩罚 → 多吐几个框不掉分，Dice 用并集同理。所以指标对"过分割/过检测"是**宽容**的。
2. `average_dice` 把预测掩码按 GT 尺寸 NEAREST 缩放；而预测掩码本身是 256×256（SAM 输出），**上采样到原图分辨率**会带入边界误差，尤其小病灶（面积占比小时 Dice 对边界极敏感）。
3. identify 任务的答案里**包含 prompt 给出的 bbox token**，模型只需学会"复制 + 吐类别词"，而类别在数据集里近乎常量（`polyp`/`lesion`）→ 该指标接近饱和，**不能作为核心卖点**。

---

## 8. 简历三条 claim 的逐条拆解与话术

### 8.1 "设计多任务路由机制，将隐状态映射到分割解码器、检测头和定位头"

**代码事实**：`expand_vocab` 扩 5 个特殊 token → resize embedding → 训练后这些 token 有了独立 embedding；生成阶段按 token id 分发到 `seg_projector+mask_decoder` / `box_heads[S/M/L]` / `loc_head`。

**怎么讲（3 句）**：
1. 我们把"任务"从**模型结构层面**下移到**词表层面**：新增 5 个结构性 token，任务切换变成"模型决定下一个词是不是结构性 token"。
2. 路由的粒度是**token 级而非样本级**——同一段输出里可以混排"文本 + 3 个 `<SEG>` + 2 个 `<BOX_M>`"，天然支持"报告里夹带定位"这种临床表达。
3. 好处是**零结构改动即可扩展新任务**（加一个 token + 一个头），且共享同一套语言先验；代价是路由是硬选择、不可微，正确性完全依赖 LLM 的格式遵循能力。



**可能追问**：
- Q: 这不就是 prompt 里加特殊符号吗，凭什么叫"路由机制"？
  A: 差别在于**输出去向被 token 决定了**。普通特殊符号只影响输入分布；这里 token 隐状态会**绕过词表**进入另一个参数子空间（SAM decoder / 回归头），是一个真正的 dispatch。同时我们做了三件事让它 work：(a) 新 token embedding 随机初始化、必须放开 embed/lm_head 才学得动；(b) 每个头有独立监督，梯度只从对应位置回流，避免任务互扰；(c) 用尺度分档把"回归难度"分治。
- Q: 路由错了（该吐 `<SEG>` 吐成文本）怎么办？
  A: 训练侧靠 CE 拉概率；推理侧可以加 **logits processor 做语法约束**（比如 `[segmentation]` 任务下强制前 N 个 token 为 `<SEG>`），或改成"结构化 token 前置"的输出顺序，让结构先于文本，文本再依赖结构（见 §10）。
- Q: 为什么不像 MoE 那样学一个 gate？
  A: MoE 的 gate 在**每个 token 每层**做软加权，参数和通信开销大且需要 load balance；我们的"专家"是**输出侧的异构解码器**（SAM / MLP），输入维度都不同，无法做软加权。用语言模型自己当 gate，等于免费复用 8B 的语义判断，且可解释（人能读出它选了哪个 token）。

### 8.2 "自适应多查询分割……解决病灶数量不固定"

**代码事实**：
- K 由答案里的 `<SEG>` 个数决定，K=0 时答案是 `"No lesion is visible."`（`unified_us_dataset.py:217-222`）——**这是"自适应"的核心：模型输出一段自然语言拒绝，而不是输出一个空掩码**；
- 每个 `<SEG>` 独立走一次 mask decoder（`multimask_output=False`，`omnirad.py:214`），K 个 query 共享同一份 SAM 密集特征；
- "自适应"的监督：`L_cardinality = |n_emitted - K_gt| / max(K_gt,1)`，权重 0.5。

我们把实例数从结构超参数变成生成内容：答案里写几个 <SEG> 就有几个实例，K=0 时答案直接是一句“未见病灶”。每个 <SEG> 的隐状态投影成 256 维 query，共享同一份 SAM 密集特征，各自解出一张掩码。这样天然支持变长、支持拒绝，而且输出顺序带语义（先描述大的）
**可能追问**：
- Q: K 的上限？会不会无限吐 `<SEG>`？
  A: 训练数据里 K 最大是数据集本身的实例数（个位数），`max_new_tokens=200` 兜底；没有显式上限约束，理论上会重复吐。改进：约束解码 + 训练时加"K 超过 GT 就截断"的负样本。
- Q: 多个 query 会给出重复掩码怎么办？
  A: 当前没有 NMS/去重，评估用并集所以不惩罚重复（见 §7）。要做的话：query 之间加 diversity loss（掩码两两 IoU 惩罚）或用 Hungarian matching 做一对一监督。
- Q: 为什么不用 Mask2Former 那种 object query？
  A: 那是**固定 query 数 + 匈牙利匹配**，输出顺序无意义、不支持 K=0 的自然拒绝，也不能和文本生成耦合。我们用 LLM 的自回归决定 query 数量与**语义顺序**（先大病灶后小病灶），并且 K=0 能用一句话解释原因——这在临床上比"输出 0 个 query"更有用。

### 8.3 "解剖学感知定位机制，解决定位表达不符合临床习惯"

**代码事实（这里必须诚实）**：
- `loc_head` 有 `anatomy_head`（30 类），但**训练时是 `pass`**（`omnirad.py:1344-1347`，注释写着 "proper anatomy label mapping will be added later"）→ **这个分支从未被训练**。
- 真正的"解剖感知"发生在**文本侧**：`_refer_answer` 生成的答案是 `"The lesion is located in {region} <LOC>."`（`unified_us_dataset.py:236-242`）——模型必须同时吐出**解剖区域词**和 `<LOC>` token，所以"解剖"是通过语言建模学到的，不是通过那个 30 类头。
- 另外 `report ⇌ region` 的双向链接：报告文本与 `anatomy_region` 共现，属于**隐式**的多任务正则。

定位拆成符号和连续两部分：按 GT 面积比把框分成 S/M/L 三档，三档各一个回归头、小目标加权 2 倍，缓解大小目标共用一个回归器时的方差冲突；同时让模型在答案里说出解剖区域词，和 <LOC> 坐标形成一致表达。尺度 token 是写在答案里的监督信号，所以模型必须学会主动判断大小。定位拆成符号和连续两部分：按 GT 面积比把框分成 S/M/L 三档，三档各一个回归头、小目标加权 2 倍，缓解大小目标共用一个回归器时的方差冲突；同时让模型在答案里说出解剖区域词，和 <LOC> 坐标形成一致表达。尺度 token 是写在答案里的监督信号，所以模型必须学会主动判断大小。

**怎么讲（改写成可信版本）**：
> 定位不是纯回归：我们把"位置"拆成**符号化的解剖区域**（可读、可核对，如 `right_breast`）和**连续的像素框**（`<LOC>`）两部分，同一句回答里同时给出。这样模型被迫在"说清在哪个器官"和"指出具体坐标"之间建立一致的表征；对临床来说，"右下象限"比"IoU=0.6 的框"更符合描述习惯。此外按 GT 面积比分 S/M/L 三档、每档一个独立回归头，缓解小目标与大目标共用一个回归器时的方差冲突。

**可能追问**：
- Q: 30 类解剖标签哪来的？怎么评估的？
  A: 来自数据集 schema 的 `anatomy_region` 字段（如 `right_breast`、`colon`），由标注/转换器写入；**目前没有单独评估 anatomy 分类准确率**，它是通过 refer 任务的文本指标间接体现的。→ 这是你可以顺势说"下一步工作：把 anatomy_head 接上 CE 监督，并报告解剖分类 Acc"。
- Q: 解剖感知对 IoU 有贡献吗？
  A: 直接的机制是"分尺度头 + 文本里的区域约束"。严格证明需要消融（去掉 region 词看 IoU），**这个消融我们还没跑完**——如果被追问，就说"论文里的 +0.1370 是整包（多查询分割 + 分尺度头 + 解剖描述）的联合收益，单项归因的消融在补"。

### 8.4 三个指标提升怎么讲（可比性防守）

| 指标 | 值 | 必须补的一句话 |
|---|---|---|
| IU-XRay 报告 BERT-Sim | +0.0589 | 口径是 `paraphrase-MiniLM-L6-v2` 余弦相似度，**与 MiniGPT-Med 基线同脚本同权重**；BLEU-4/ROUGE-L 一并报，避免"只挑语义相似度"的质疑 |
| VQA-RAD | +0.0745 | VQA-RAD 测试集仅 452 题，**置信区间较宽**（±0.02 量级），建议补 SLAKE（2094 题）上的同向提升来坐实 |
| BUS 定位 IoU | +0.1370 | 基线 MiniGPT-Med **没有定位能力**（不能吐框），所以这是"从 0 到可用"而非"同能力比较"；同时要说明 IoU 是"每 GT 框取最大匹配再平均"的宽容口径 |

**被问"怎么保证不是调参调出来的"** → 三件事：固定 split 与 seed、基线与本方法用**同一套 eval 脚本与同一份 GT**、所有超参（lr/warmup/epoch）对基线与本方法都做过小网格搜索。**不要**说"baseline 用的官方默认"——那是最容易被 challenge 的回答。

---

## 9. 高频追问题库（按被问概率排序）

### A. 架构与多模态交互
1. **为什么视觉 token 只有 256 个？会不会丢细节？** 4 合 1 patch merge，序列从 1024 降到 256；细节靠 SAM 分支补。丢的是空间分辨率，不是信息量（通道维扩到 5632）。
2. **为什么 SAM 特征不进 LLM？** 64×64=4096 个 token 会让 8B 模型的上下文和 attention 成本爆炸（4096² vs 256²，差 256 倍）；而且 LLM 的语义空间不需要这种密集几何。分工：LLM 管"是什么/在哪一类"，SAM 管"精确到像素"。
3. **为什么冻结 SAM/ViT？** 数据量只有万级（vs SAM 的 11M），全量微调会灾难性遗忘 + 显存不够；只训 prompt_encoder/mask_decoder（4M）就够适配新模态。
4. **LoRA 为什么只挂 q/v，r=64？** q/v 是 MiniGPT-Med 的既有配置，便于复用；r=64 + α=16（scale 0.25）是在 8B 上"容量与遗忘"的折中。可以补一句："没做 r∈{16,32,64,128} 的完整消融，这是审稿人会问的点。"
5. **SAM 输入为什么降到 512？** 位置编码是 O(n²) 的相对偏置，显存吃紧；1024→512 后 pos_embed 双三次插值，密集特征 32×32 再上采样到 64×64 与 SAM decoder 对齐。代价是细边界精度，但 RLE 之后差异不大（未量化，诚实说）。
6. **文本和视觉的 attention 是双向还是因果？** 因果（LLaMA decoder-only）。视觉 token 在 prompt 前缀，文本 token 能看视觉，视觉 token 看不到后续文本——这也是为什么 `<SEG>` 的隐状态放在**生成侧**，它"看过"整段指令。
7. **两段前向是不是很浪费？** 是，约 2× prefill。可优化：generate 时用 `return_dict_in_generate` + 自定义 `output_hidden_states`，或改用 `StaticCache` 手工解码循环，把需要的层隐状态存下来，省掉第二段。

### B. 分割 / 定位细节
8. `<SEG>` 的隐状态怎么变成 mask？`Linear(4096→512→256)` → 当作 SAM 的 sparse prompt（形状 `(B,1,256)`）→ 与密集特征 + 位置编码进 two-way transformer → 上采样 4× → 256×256 logits → sigmoid。
9. **一个 `<SEG>` 只出一个 mask，怎么保证和 K 个实例一一对应？** 靠**发射顺序**与 GT 的顺序对齐（`_group_hidden_states_by_batch` 保留 batch 内顺序，`1393-1400` 按顺序配对）。风险：顺序错了监督就错，但数据集按标注顺序生成答案，所以对齐成立。
10. **Dice 和 BCE 都用了，权重怎么定？** 1.0 : 0.5。医学分割里前景占比小，纯 BCE 会被背景淹没，Dice 提供区域级梯度。
11. **框为什么用 L1 而不是 IoU loss？** 因为要交给语言模型"逐坐标回归"，L1 对坐标直接可导且稳定；IoU loss 在框退化（x2<x1）时梯度不友好。**但这是可改进点**：GIoU/DFL 通常能提 2~3 个点，且应加 `x1<x2, y1<y2` 的排序约束或参数化（中心+宽高）。
12. **S/M/L 三档不会互相抢样本吗？** 会，同一 GT 只监督它所属那一档的头；好处是每档方差不混，坏处是小目标样本少（面积<1%）→ 用 `scale_w_s=2.0` 加权补偿。
13. **`box_heads` 里的 64 类分类头用了吗？** 定义了 `class_head` 但**没有 CE 损失**，所以 `class_logits` 是未训练的随机输出（`generate` 里却会把它写进 `boxes[i]["class_id"]`）。→ 主动说："类别信息走文本通道，这个头是预留的，应该在正式版里删掉或接上监督。"
14. **解剖头训练了吗？** 没有（`pass`）。见 §8.3。

### C. 训练与优化
15. **多任务会不会负迁移？怎么处理？** 观察到三个手段：(a) 任务随机采样让梯度交替而非叠加；(b) 结构化损失只作用在对应 token 位置，参数子空间基本不重叠；(c) 总损失 clamp 50 + 梯度裁剪 1.0 防某一任务主导。**没做的**：梯度冲突度量（PCGrad/GradNorm）、任务权重自适应——这是可以主动提的改进方向。
16. **`<SEG>` 的梯度会不会污染语言能力？** 会有一点：`<SEG>` 的 CE 与掩码损失共享同一个隐状态。控制手段是 seg 损失权重（1.0）小于 text（1.0 但 token 数多 100 倍），实际 text loss 仍主导。
17. **为什么 warmup 2000 步、lr 2e-5？** LLaMA-3 的 `llama_proj` 是**随机初始化**（MiniGPT-Med 的 ckpt 是 LLaMA-2 的，不兼容），需要更大 lr 和更长 warmup 做视觉-语言对齐。这是配置注释里明确写的（`finetune.yaml:208-215`）。
18. **fp16 出过什么 problem？** 三类：logits 溢出→NaN（`nan_to_num` + fp32 CE）、非法 label id→CUDA gather 越界（清洗）、空答案→0/0 NaN（替换 + 返回 0）。
19. **怎么判断模型收敛？** 分阶段看：对齐期看 `text_loss` 平台；精调期看 `n_seg_tokens`（是否稳定吐特殊 token）、`cardinality_acc`、seg Dice。这些都在 `forward` 返回值里（`1614-1629`）并打进 wandb。

### D. 数据与评估
20. **数据混合比例怎么定？** 按"任务覆盖度 + 数据量"人工定（indiana 25 给报告生成最大权重，kvasir 23 提供多实例，私有 US 17 提供逐实例掩码）。**没做**温度/不确定性驱动的自动配比。
21. **患者级切分怎么做的？** `patient_level_split` 按 `patient_id` 分组后 shuffle（`dataset_utils.py:212-249`），私有数据 76/4/20。避免同一患者跨 split 泄漏——这点一定要主动说，医学数据集最常见的审稿质疑。
22. **val 只有 243 张，选模可靠吗？** 不可靠，这也是为什么 best-ckpt 用 cardinality_acc 这种粗指标。承认它，并说"正式版会把 5 个任务的指标做加权早停"。
23. **zero-shot RSNA 怎么做的？** RSNA 未进训练集，直接测 `<BOX_*>` → 检验"框回归头"的泛化。这类跨数据集 zero-shot 是审稿人喜欢的点。

### E. 工程与局限
24. **显存怎么压进 24G？** 冻结双塔 + `no_grad` 前向、SAM 降到 512、ViT/LLM 双梯度检查点、bs=2、AMP。
25. **推理延迟多少？** 两段前向 + SAM ViT-H 一次；瓶颈在 8B 的 prefill 与 SAM-H（约 600M）。可优化点：SAM 换 ViT-B/MedSAM、视觉 token 用 KV cache 复用、第二段前向省掉。
26. **最大的局限是什么？**（这题一定要有准备好的"三连"）
    1. **暴露偏差**：训练时总是喂 GT 的 `<SEG>` 序列，推理时要自己决定数量；K 一错，掩码全部错配。
    2. **框精度受限于 256 个视觉 token**，小目标上 IoU 天花板明显。
    3. **结构化监督依赖人工/半自动掩码**，跨模态泛化（X 光几乎没有像素级标注）没有真正验证。

---

## 10. 专题：训练没问题、推理掉点，怎么系统性优化？

这是最可能被追问的开放题。**不要一上来就说"加数据"**，要展示排查框架。

### 10.1 第一步：分层归因（按这个顺序查，命中率从高到低）

| # | 检查项 | 怎么测 | 若命中的典型现象 |
|---|---|---|---|
| 1 | **训练/推理预处理不一致** | 用 eval 的 processor 在**训练集**上跑一遍推理，比 loss/指标 | train 指标远高于 test；`RandomResizedCrop` vs `Resize` |
| 2 | **坐标空间/归一化回路** | 把 GT 框走一遍"归一化→反归一化"，看是否还原 | 框系统性偏向某一边；`/448` 常量 vs 真实宽高（§3 坑 2） |
| 3 | **特殊 token 未触发** | 统计 `seg_count` 分布、`<SEG>` 首次出现位置 | 大量 seg_count=0 → Dice=0；文本却看着正常 |
| 4 | **EOS 未生效** | 打印生成长度分布，看是否顶到 200 | 长度全 200；EOS 之后还有 `<SEG>` 被计入（§6） |
| 5 | **batch vs 单条** | 同一图 bs=1 与 bs=8 各跑一次 | bs 大时掉点 → 左填充 / position_ids |
| 6 | **精度** | fp16 vs fp32 推理对比 | fp16 下 mask logits 溢出、坐标 round 误差放大 |
| 7 | **teacher-forcing vs free-running** | 给定 GT 前缀（含正确 K 个 `<SEG>`）再解码掩码 | 给定 GT 前缀后 Dice 大幅回升 → 确诊**暴露偏差** |
| 8 | **后处理阈值** | 阈值 0.3/0.4/0.5/0.6 扫 Dice | 最优阈值远离 0.5 → 训练分布与 sigmoid 校准不匹配 |

> 第 7 项是**最有诊断价值**的一步：它把"模型不会分割"和"模型不会决定数量/格式"彻底分开。面试时把这一步讲出来，立刻区别于只会调参的候选人。

### 10.2 第二步：按性价比排序的解法

**P0（改动小、收益大、必须先做）**
1. **对齐几何预处理**：dense 数据集去掉 `RandomResizedCrop`，改 `Resize(保持长宽比)+pad`，mask/box 用同一组参数变换。这一条通常单独就能救回大半 IoU。
2. **逐样本坐标归一化**：用 `samples["image_size"]` 的 (W,H) 分别归一到 [0,1]，generate 时用同一组 (W,H) 反归一化；框参数化改成 `(cx,cy,w,h)` + sigmoid，天然保证 `w,h>0`、不会退化。
3. **截断 EOS 之后的 token**，再做 `seg_count` / mask / box 解码；并把 `stopping_criteria` 真正传给 `generate`。
4. **选模指标换成任务指标**（Dice/IoU/BERT-Sim 加权），别用 `cardinality_acc`。

**P1（针对暴露偏差，这是本架构的核心病灶）**
5. **结构化 token 前置**：把答案改成 `"<SEG> <SEG> ... {report text}"`，即**先出结构、再出文本**。好处：文本生成条件依赖于结构，结构 token 的隐状态不被长文本"稀释"；同时训练/推理的"结构决策点"更早、更集中。
6. **Special-token dropout / scheduled sampling**：训练时以概率 p 把答案里的部分 `<SEG>` 替换成模型自己采样的 token（或用句子级 scheduled sampling），让模型见过"自己吐错数量"的状态。
7. **加 count head**：在 prompt 末尾的最后一个隐状态上接一个 `0..K_max` 的分类头，用 GT K 做 CE。推理时用它**约束解码**（采样 K 后再生成正好 K 个 `<SEG>`），把"数量"从语言建模问题变成分类问题——**这是收益最确定的一步**。
8. **约束解码（logits processor）**：任务标签为 `[segmentation]` 时，前 K 个位置只允许 `<SEG>` 与 EOS；`[detection]` 时只允许 `<BOX_*>`；禁止标点穿插。工业界落地基本都会加这层。

**P2（精度上限）**
9. **框损失升级**：L1 → `L1 + GIoU`（或 DFL 分布式回归），并加"预测框按 (x1,y1,x2,y2) 排序"的软约束。
10. **更细的视觉特征**：把 256 token 提到 576（patch merge 2×2 或用 2 层特征金字塔），或给框头接一个可变形注意力采样 SAM 特征（让框"看得见"高分辨率）。
11. **mask 后处理**：阈值搜索 + 连通域过滤 + 多 query 去重（两两 IoU>0.7 合并），并对 K=0 的样本设"最大前景概率 < τ 就不输出掩码"的拒识规则。
12. **分割头微调策略**：SAM decoder 全量微调在小数据上容易过拟合，可试 LoRA 或只训 cross-attention 层。

**P3（数据侧）**
13. 难例挖掘：把推理时 IoU<0.3 的样本回流重训（注意要按患者切分，别把 test 漏进 train）。
14. 多实例真标注：Kvasir 只给了合并掩码，若能拿到实例级掩码，多查询能力会有质变。
15. 报告生成的暴露偏差：报告用 `beam search + 长度惩罚` 而非 greedy，并对高频模板做去重（Indiana 报告高度模板化，greedy 容易退化成"正常胸片"套话）。

### 10.3 分指标对症表

| 掉的指标 | 首要怀疑 | 首选动作 |
|---|---|---|
| BERT-Sim（报告） | 生成退化成模板/截断 | 检查 EOS 与 max_new_tokens；beam=3 + length_penalty；确认 eval 用同一 `end_sym` |
| VQA BERT-Sim | 答案过短/超纲 | 检查 max_new_tokens=200 是否被结构 token 挤占；VQA 数据里混入了结构化 token 训练会不会串味 |
| IoU（检测/定位） | 坐标回路 + 预处理 | §3 坑 1/2 + 框参数化；先做"GT 自环测试" |
| Dice（分割） | seg_count=0 或阈值 | §10.1 第 3/8 项；加 count head + 约束解码 |
| Identify Acc | 类别先验太强 | 该指标本身接近饱和，不要花时间优化 |
| 全任务一起掉 | 推理管线/batch/precision | §10.1 第 1/5/6 项 |

### 10.4 面试时的 30 秒回答模板

> "我会先把'掉点'拆成两类：**格式错**（该吐的 token 没吐、数量不对）和**精度错**（吐了但位置/边界不准）。最快的判别方法是 **teacher-forcing 对照**：给定 GT 的结构前缀再解码，如果 Dice 立刻回到训练水平，说明是暴露偏差——那就上 count head + 约束解码 + scheduled sampling；如果仍然差，说明是几何不一致，我会先查预处理（训练用 RandomResizedCrop、评估用 Resize，掩码和框没跟着变）和坐标归一化（是否用了真实宽高而不是固定 448）。这两类问题在我们代码里都真实存在过，定位之后 IoU/Dice 的恢复是立竿见影的。"

---

## 11. 代码里真实存在的坑（被问住时的诚实回答模板）

> 原则：**主动暴露 + 给出修法 + 说明影响范围**。这比假装完美安全得多，面试官最怕的是"不知道自己代码有问题"。

| # | 问题 | 位置 | 影响 | 修法 |
|---|---|---|---|---|
| 1 | 框归一化用固定 448，非 448 宽的图 → 框被 clamp 到边界 | `omnirad.py:1283` | IoU 系统性偏低（**头号嫌疑**） | 用 `samples["image_size"]` 逐样本归一化 |
| 2 | 训练 `RandomResizedCrop` 与 GT 掩码/框几何不对齐 | `blip_processors.py:78` + `unified_us_dataset.py:98` | dense 任务标签噪声 | Resize+pad，同步变换 mask/box |
| 3 | cardinality 惩罚无梯度 | `omnirad.py:1460-1471` | K 只能靠 CE 学 | count head / REINFORCE |
| 4 | anatomy 分类 `pass` 未实现 | `omnirad.py:1344-1347` | 解剖头未训练 | 接 CE，加 label map |
| 5 | `class_head` 无损失，却输出 `class_id` | `omnirad.py:280` / `890-893` | 下游拿到随机类别 | 接 CE 或删除 |
| 6 | `stopping_criteria` 构造未传入 generate | `omnirad.py:622-655` | 可能生成到 200 token | 显式传参 + 设 `eos_token_id=[128009,128001]` |
| 7 | `seg_count` 统计包含 EOS 之后 token | `omnirad.py:732` | 幻影掩码、数量错 | 先截断到首个 EOS |
| 8 | 课程学习是死代码 | `runner_base.py:374-392` | 无影响，但配置误导 | 实现 `set_curriculum_phase` 或删配置 |
| 9 | `loss_weights["seg"]`、`text_bbox_penalty`、`cons_rd`、`cons_gs`、`align_anat` 均未使用 | `DEFAULT_LOSS_WEIGHTS` | 配置与实现不一致 | 清理或实现（跨任务一致性目前只做了 mask-box） |
| 10 | 不确定性加权实际是"整图标量"而非逐像素 | `omnirad.py:1434-1445` | 叙事 > 实现 | 改逐像素 `F.binary_cross_entropy_with_logits(..., reduction='none')` |
| 11 | `_compute_cons_loss` 固定用 `box_m` 头 | `omnirad.py:1209` | 跨尺度一致性有偏 | 把 token 名一起带进 tuple |
| 12 | `identify` 答案里复制了 prompt 的 bbox | `unified_us_dataset.py:290` | 指标虚高 | 换更硬的问法/遮挡框 |

**万能话术**：
> "这个模块我实现时先跑通了主链路，上面这些是已知的待清理项，优先级按对指标的影响排：坐标回路的 P0，count 监督的 P1，配置清理的 P2。论文版会在 camera-ready 前把 1、2、3、6、7 修掉并补消融。"

---


### 附：一句话记住每个模块

| 模块 | 一句话 |
|---|---|
| EVA 分支 | 把图变成 256 个"词"，让 8B 模型能读图 |
| SAM 分支 | 不进 LLM 的几何字典，按 LLM 的提问查表 |
| `<SEG>` | 一个 token = 一个 mask query，变量 = 自适应实例数 |
| `<BOX_S/M/L>` | 按面积分档的回归专家，缓解小目标方差 |
| `<LOC>` | 临床习惯的"区域词 + 像素框"联合表达 |
| 两段前向 | 用 2× prefill 换"训练推理口径一致" |
| 一致性损失 | 让"掩码的紧致框"与"预测框"互相约束（目前只做了这一个方向） |

###  一个可执行的排查清单(模型微调效果不好，如何排查)
1. 用固定测试集对比基座和微调模型。
2. 检查训练/验证集是否泄漏。
3. 抽查 50 条训练样本，看格式、风格、指令是否一致。
4. 看训练 loss、验证 loss、业务指标曲线。
5. 确认推理 prompt、模板、tokenizer、max_new_tokens 与训练一致。
6. 只改一个超参重跑小实验，观察变化。
7. 如果领域提升但通用退化，尝试 LoRA、混入通用数据或降低训练强度。
8. 记录每次实验的数据版本、超参、指标和典型 bad case。