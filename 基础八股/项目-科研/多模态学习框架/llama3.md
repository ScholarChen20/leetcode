# OmniRad 面试讲解笔记

## 项目定位

**一句话介绍：**OmniRad 在 MiniGPT-Med 的视觉语言主干上，增加由特殊 token 驱动的结构化预测头，使同一个模型能根据任务指令输出报告、VQA 答案、检测框、定位框和分割掩码。项目默认训练配置使用 **LLaMA-2-7B + LoRA**；仓库另有 LLaMA-3 配置，介绍具体实验时应说明采用了哪一个配置。

它要解决的是医学视觉语言模型擅长生成文字，却难以直接给出病灶位置和像素边界的问题。核心思路可记成：**一个语言主干、两条视觉路径、五个特殊输出 token、按 token 路由到结构化预测头。**

## 面试时的 90 秒表述

> 这个项目希望用一个医学多模态模型处理报告生成、问答以及病灶的检测、定位和分割。我们以 MiniGPT-Med 为基础：EVA-ViT 提取语义特征，投影到 LLaMA 的输入空间；另用 MedSAM 提取稠密空间特征供分割解码器使用。
>
> 输入侧用 `[report]`、`[vqa]`、`[detection]`、`[segmentation]` 等任务标签指定任务。输出侧扩展了 `<SEG>`、`<BOX_S/M/L>`、`<LOC>` 五个 token。语言模型生成普通文字时直接输出文本；生成特殊 token 时，我们取该位置的隐藏状态交给相应的掩码或框预测头。因此语言模型既决定任务输出形式，也决定病灶实例的数量。
>
> 重点设计有三个：一是重复输出 `<SEG>`，使一张图可以产生零个、一个或多个掩码，并加入像素级不确定性分支；二是按病灶相对面积划分小、中、大三个检测尺度，分别回归并提高小目标的损失权重；三是设计掩码与检测框的几何一致性损失，约束不同输出指向同一位置。目前前两项的主要代码路径已经写出，一致性训练和解剖先验仍需补齐与验证。效果要以实际实验指标和消融结果为准。

## 总体结构与代码入口

```text
医学图像 + 任务指令
    ├── EVA-ViT-G → 4-patch 合并 → 线性投影 → LLaMA + LoRA
    │                                        ├── 普通词 → 报告 / VQA / 识别
    │                                        ├── <BOX_S/M/L> → 三个检测框头
    │                                        ├── <LOC> → 定位框头
    │                                        └── <SEG> → 分割提示向量
    └── MedSAM 图像编码器 → 稠密特征 ───────────────┘
                                               ↓
                                        SAM mask decoder → 掩码
```

- EVA-ViT 的特征进入 LLaMA：`minigpt4/models/minigpt_v2.py` 的 `encode_img()`。
- MedSAM 编码器、mask decoder、框头和定位头：`minigpt4/models/omnirad.py`。
- 任务提示、答案 token 和结构化标注：`minigpt4/datasets/datasets/unified_us_dataset.py` 与 `kvasir_dataset.py`。
- 默认配置：`train_configs/omnirad_finetune.yaml`。

## 创新点 1：特殊 token 路由，把文字与几何输出接在一个主干上

**动机：**报告与 VQA 是文字，检测与定位是坐标，分割是掩码。单靠语言模型输出坐标字符串，难以直接优化连续的几何结果。

**代码路径：**

1. `OmniRad._expand_output_vocabulary()` 将 `<SEG>`、`<BOX_S>`、`<BOX_M>`、`<BOX_L>`、`<LOC>` 加入 tokenizer，扩展 LLaMA 的输入 embedding 和输出层，并保存 token ID。配置在 `train_configs/omnirad_finetune.yaml` 的 `expand_vocab`。
2. 训练时，`OmniRad.forward()`以 `output_hidden_states=True` 跑 LLaMA。普通答案和特殊 token 都接受语言模型交叉熵监督。
3. `_extract_special_token_hidden_states()`扫描目标答案里的特殊 token，记录 `(batch_idx, hidden_state)`；保留样本索引和出现顺序，避免多病灶样本在 batch 中配错标注。
4. `compute_auxiliary_losses()`按 token 类型调用检测、定位和分割损失。
5. 推理时 `generate()`先自回归生成答案；`_run_second_pass()`把生成 token 与提示重新送入 LLaMA，取得各特殊 token 的隐藏状态；`_decode_dense_outputs_from_generation()`再调用对应预测头。**当前是生成后共用一次二次前向，不是逐 token 实时解码。**

**面试说法：**“这里的路由由任务标签、生成的特殊 token 以及对应的预测头共同实现；代码里没有单独的可学习门控网络。”

## 创新点 2：AMU-Seg，可变数量分割与不确定性

### 2.1 可变数量的 `<SEG>` 查询

超声数据转换器用连通域把合并掩码拆成实例掩码，再从实例掩码生成框，标注 `K = len(boxes)`，见 `tools/dataset_utils.py` 的 `split_instances()`、`masks_to_boxes()`和 `tools/converters/group_us.py`。数据集抽到分割任务时，答案会写成 `2 lesions should be segmented. <SEG> <SEG>`；`K=0` 时答案不含 `<SEG>`，见 `UnifiedUSDataset._segmentation_answer()`。

模型对每个 `<SEG>` 位置的隐藏状态独立处理：`seg_projector` 将 LLaMA 隐藏状态投影到 256 维，作为 SAM 的 sparse prompt；MedSAM 图像编码器提供 dense image embedding；SAM mask decoder 设置 `multimask_output=False`，所以一次 `<SEG>` 对应一张掩码。相关实现位于 `SamDenseEncoder`、`SamMaskDecoder` 和 `_compute_seg_loss()`。

训练时，预测掩码与同一样本的实例 GT 按出现顺序配对，计算 BCE + Dice。推理时每遇到一个 `<SEG>` 就解码一张掩码，并返回 `seg_count` 与 `masks` 列表。

**注意：**`_compute_seg_loss()`里还有 `|生成的 <SEG> 数量 - K|` 形式的 cardinality 项，但数量经 `.item()` 变为普通数值，它本身不能把梯度传回 token 数量决策。数量学习主要依赖目标答案中 `<SEG>` 的语言模型交叉熵。当前超声与 Kvasir 转换器还会跳过一部分无病灶样本，所以不能仅凭代码声称已验证 `K=0` 的拒检效果。Kvasir 多框样本也可能只有一张掩码路径，多实例分割监督尚需核实。

### 2.2 像素级不确定性

`SamMaskDecoder` 在掩码 logits 后增加两层卷积的 `uncertainty_head`，输出逐像素的 `log_variance`。`_compute_seg_loss()`把它截断到 `[-4, 4]`，换算方差，再将加权 BCE 与方差正则项以 `0.1` 的系数加入分割损失。

**面试说法：**“我们接入了像素级不确定性分支，训练目标允许模糊边界获得不同权重。”当前推理输出只返回掩码，没有向外返回不确定性图，也没有阈值拒判或撤回 `<SEG>` 的闭环，因此“自动拒判”属于设计目标。

## 创新点 3：SAR-Loc，尺度感知检测与解剖定位

### 3.1 S/M/L 三尺度检测

`tools/dataset_utils.py` 的 `bbox_scale()`按框面积占图像面积的比例分桶：小于 1% 为 S，1% 到不足 10% 为 M，至少 10% 为 L。数据集据此在检测答案中放入 `<BOX_S/M/L>`，例如 `lesion 1 <BOX_S>; lesion 2 <BOX_L>`。

`OmniRad` 建立三个独立的 `BoxRegressionHead`。每个头以隐藏状态为输入，经 `Linear → GELU → 4 维框输出`。`_compute_det_loss()`按 **样本索引 + 尺度桶**配对 token 与 GT，框输出经 sigmoid 归一化后算 L1。默认尺度权重为 S=3.0、M=1.5、L=1.0。推理时按 token 类型选头，将 `[0,1]` 坐标乘 `img_size` 得到像素框。

**注意：**代码预留了 `class_head`，推理可读出 `class_id`，但当前检测损失没有类别 CE；设计文档中的 GIoU 也未进入当前 `_compute_det_loss()`。因此讲“尺度加权框回归”准确，讲“完成框类别联合训练或 GIoU 优化”不准确。

### 3.2 `<LOC>` 与解剖区域

超声数据转换器从报告提取 `anatomy_region`，数据集的 referring 答案会包含自然语言区域描述和 `<LOC>`。`LocalizationHead` 共享一层 MLP，分出 4 维像素框分支和解剖区域 logits 分支。

目前 `_compute_loc_loss()`只对框计算 L1；解剖类别监督处还是 `pass`。推理也只解出框，未返回解剖分类结果。解剖图谱一致性与“报告 ↔ 区域”双向绑定写在设计文档中，尚未形成完整代码路径。

**面试说法：**“定位头已预留像素坐标与解剖类别双输出，当前真正训练的是像素框；解剖分支和双向绑定是后续完善方向。”

## 创新点 4：掩码与框的跨任务一致性

`_compute_cons_loss()`要求同一样本的目标答案同时包含 `<SEG>` 和 `<BOX_*>`。它用 `<SEG>` 解码预测掩码，估计掩码外接框，与检测头预测的框做 L1，目标是让两个结构化输出指向相近区域。

当前实现有三个限制，面试应主动说明：

1. 超声与 Kvasir 的 `__getitem__()`通常一次随机抽**一个任务**，答案只含一种结构化 token，因而这项损失在正常采样下可能经常为零。
2. 一致性函数对所有尺度的框都调用 `box_m` 头，没有按 `<BOX_S/M/L>` 保留原尺度。
3. 掩码边界提取包含阈值比较与 `argmax`，不能称为完整可微的 soft 外接框。报告与检测、grounding 与分割的另外两项一致性损失尚未实现。

**面试说法：**“我们写出了 mask–box 几何一致性损失的代码雏形；当前还需改造联合任务样本、尺度头匹配和边界提取方式，再通过消融验证其收益。”

## 训练目标、推理输出与验证

训练总损失由文本 CE、检测 L1、定位 L1、分割 BCE/Dice/不确定性项，以及条件触发的 mask–box 一致性项组成，见 `OmniRad.forward()`。训练答案里的特殊 token 同时受到文本 CE 监督，其隐藏状态还接受对应几何监督。

推理的实际执行顺序是：**EVA 图像编码 → LLaMA 生成文本及特殊 token → 二次 LLaMA 前向取隐藏状态 → 检测/定位/分割头解码**。输出可包含清理后的文本、保留特殊 token 的 `raw_text`、`seg_count`、`masks` 和 `boxes`。框坐标还会插回 `raw_text`，兼容现有评估脚本的正则解析。

评估思路：报告看 BERT-Sim、BLEU-4、ROUGE-L、临床标签 F1；VQA 看答案匹配；检测和定位看 IoU；分割看 Dice/Mask IoU。仓库 README 的 OmniRad 对比表仍为 `TBD`，面试中只引用自己实际跑出的结果，不声称已有确定增益。

## 面试官追问“代码能否直接跑通”时的回答

这套架构的主链路已经写出，但几何监督仍有需要修正的工程点：

- `blip2_image_train` 对图像做 `RandomResizedCrop`，框和掩码没有同步执行同一几何变换；原始框又直接除以 `img_size`，会造成图像与标注坐标不一致。
- 数据集图像已按 EVA 路径归一化，MedSAM 编码器又使用自己的均值与方差；其输入需要从原始 RGB 单独预处理，不能只靠 `img.max() <= 1` 判断范围。
- 配置中有 `loss_weights.seg`，但总损失目前直接加 `aux_losses['seg']`，没有乘这个总权重。
- 配置中写有 `curriculum_epochs: 8`；runner 读取的是模型属性，而当前 OmniRad 模型没有设置该属性或实现 `set_curriculum_phase()`，不能把它描述成已生效的完整课程训练。

这类问题的面试回答可以收束为：“我把模型设计、实际代码路径和已验证效果分开讲。下一步优先修正图像与标注的几何对齐，再补齐解剖监督与联合任务采样，最后做消融实验。”

## 与 MiniGPT-Med / LISA 的关系

| 维度 | MiniGPT-Med | LISA | OmniRad 当前代码 |
| --- | --- | --- | --- |
| 主要任务 | 医学报告、VQA 等文本任务 | 语言驱动分割 | 文本任务 + 框/掩码的结构化预测路径 |
| 视觉路径 | EVA-ViT 语义特征 | 视觉语言特征 + SAM 空间特征 | EVA-ViT + MedSAM |
| 结构化 token | 有文本坐标输出 | `<SEG>` | `<SEG>`、`<BOX_S/M/L>`、`<LOC>` |
| 多实例分割 | 不支持 | 主要是单查询分割 | 可重复 `<SEG>`，每次解码一张掩码 |
| 检测尺度 | 未采用本项目三档方案 | 不涉及 | S/M/L 三个框头与加权 L1 |
| 不确定性 | 未采用本项目分支 | 未采用本项目分支 | 已有像素级分支及训练项，尚无推理拒判 |
| 跨任务一致性 | 未采用本项目方案 | 未采用本项目方案 | mask–box 损失雏形，尚需联合样本验证 |

## 一句话总结

**我们把 MiniGPT-Med 的语言生成主干扩展为结构化输出控制器：任务标签决定问题类型，特殊 token 决定输出头和实例数量；MedSAM 提供像素级分割，尺度分桶提高检测对小目标的关注。当前应把完整一致性与临床拒判表述为后续待验证的设计。**

## 一、基础差异：Llama 3 与 Qwen 3

| 维度 | Llama 3 系列 | Qwen 3 系列 |
| --- | --- | --- |
| 出品方 | Meta | 阿里通义千问 |
| 发布时间 | 2024.4（3 / 3.1 / 3.2 / 3.3） | 2025.4 |
| 架构 | 纯 Dense（decoder-only） | Dense + MoE 双系列 |
| 规模 | 8B / 70B / 405B | 0.6B~32B（Dense）+ 30B-A3B / 235B-A22B（MoE） |
| 中文能力 | 较弱 | 显著更强（原生优化） |
| 语言支持 | 以英文为主 | 119+ 语言 |
| 特殊机制 | — | 混合推理（thinking / non-thinking 快慢思考） |
| 开源许可 | Llama Community License（有商业限制，非 OSI） | Apache 2.0（完全宽松） |

## 二、面试问答

### 1. 多任务路由机制的实现逻辑是什么？

> 输入 prompt 用 `[report]`、`[vqa]`、`[segmentation]` 等标签指定任务；输出时 LLaMA 通过语言模型头决定是否生成 `<SEG>`、`<BOX_S/M/L>` 或 `<LOC>`。训练阶段扫描目标答案中这些 token 的隐藏状态，送给相应的 mask、box 或 loc 头计算辅助损失；推理阶段生成结束后再做一次 LLaMA 前向，恢复特殊 token 隐藏状态并解码结构化结果。**它是 token 条件路由，没有独立门控网络。**

### 2. 自适应多查询分割为什么能处理多个病灶？

> 数据集按实例数 `K` 在答案里放 `K` 个 `<SEG>`。虽然词表里只有一个 `<SEG>`，但每次出现的位置不同，隐藏状态也不同；每个隐藏状态经 `seg_projector` 作为一次 SAM 提示，解码一张掩码。推理时由语言模型决定实际生成几次 `<SEG>`。其可变数量能力是结构设计，`K=0` 与多实例效果仍需针对性实验验证。

### 3. 尺度感知检测如何实现？

> 数据转换时按目标框面积比例分 S/M/L；检测答案中出现对应的 `<BOX_S/M/L>`；模型为三个 token 配三个框回归头，并在损失中给小目标更高的权重。这样数据标注、token 选择、预测头和损失函数处在一条完整路径上。

### 4. 解剖先验和一致性约束做到哪一步？

> `<LOC>` 的定位头已经有像素框和解剖分类两个分支，但当前只训练像素框。mask–box 一致性损失已有函数，正常训练样本却通常一次只抽一个任务，所以还不能声称它稳定产生了协同收益。解剖 CE、图谱对齐以及其余跨任务一致性是后续工作。

### 5. 指标怎样选？

> 报告生成可用 BERT-Sim 看语义相似度，BLEU-4 看短语重合，ROUGE-L 看序列覆盖，临床标签 F1 看疾病结论是否一致；VQA 看答案匹配；框定位用 IoU，分割用 Dice 和 Mask IoU。指标解释要结合各任务输出，最终只报告实际运行得到的数值。

---

# 三、OmniRad 全流程八股：数据来源 → 预处理 → 训练 → 推理 → 评估

> **阅读口径：**以下以仓库当前的 `train_configs/omnirad_finetune.yaml` 和 `eval_configs/omnirad_evaluation.yaml` 为主，区分“代码执行路径”“设计目标”“尚未验证的效果”。项目名虽写 Radiology，实际数据还包含超声和内镜；不要把 Kvasir 说成放射影像。数据量是 2026-10-21 工作区现存 JSON 的记录数，重新转换数据后可能变化。

## 0. 一张图说清端到端链路

```text
原始图像、报告、问答、框、掩码
        ↓ 离线转换与患者级/样本级切分
data/annotations/*.json + 原始图像路径
        ↓ Dataset 取图、选任务、生成 instruction/answer、读取结构化 GT
image tensor + task prompt + answer + boxes/masks/K
        ↓ EVA-ViT 语义编码 + MedSAM 空间编码
LLaMA-2-7B + LoRA 生成文本/特殊 token；预测头生成框/掩码
        ↓ 文本 CE + 检测/定位/分割辅助损失
checkpoint
        ↓ 按任务提示推理，二次前向恢复特殊 token 的 hidden state
文本、框、掩码
        ↓ 与独立 test 标注比较
BERT-Sim / BLEU-4 / ROUGE-L / 临床标签 F1 / IoU / Dice 等
```

**一分钟总述：**“我先将不同来源的医学图像和标注整理成统一 JSON，按患者或图像划分 train、val、test。训练时，Dataset 为每张图抽取一个任务，构造图像加任务指令和对应答案，同时保留框、掩码、实例数等 GT。EVA-ViT 的语义特征经投影送入 LLaMA，MedSAM 提供分割所需的空间特征。语言模型的普通 token 用 CE 训练，`<SEG>`、`<BOX_S/M/L>`、`<LOC>` 的隐藏状态再进入各自的预测头，计算结构化损失。推理先生成文本与特殊 token，再统一做一次 LLaMA 前向解码框和掩码。评估按任务选指标，并以未参与训练的 test 文件为准。”

## 1. 数据来源：为什么要混合这些数据

| 数据集与来源 | 图像与标签 | 在当前方案中的主要用途 | 当前 JSON 数量 train / val / test |
| --- | --- | --- | --- |
| **Indiana CXR / NIH Open-i** | 胸片，`indiana_reports.csv` 与 `indiana_projections.csv`；报告含 findings、impression | 报告生成；保持语言和医学描述能力 | 5635 / 293 / 1498 |
| **VQA-RAD** | X-ray/CT/MRI 医学图像和问答 | 医学视觉问答 | 1706 / 90 / 452 |
| **SLAKE VQA** | 混合医学图像和问答 | 视觉问答、器官与疾病语义 | 7757 / 408 / 2094 |
| **SLAKE Grounding** | 图像和含区域信息的描述 | 文字区域关联 / grounded caption | 440 / 23 / 116 |
| **Group-Breast US，内部数据** | 乳腺超声帧、像素掩码、同一检查的报告 | 分割、检测、报告、指代定位、识别；由报告和框派生 VQA | 3896 / 485 / 494 |
| **Kvasir-SEG** | 结肠镜图像、息肉掩码、原始 bbox JSON | 分割、检测、指代定位、识别及模板 VQA；属于内镜模态 | 1594 / 199 / 199 |
| **RSNA pneumonia** | 胸片和肺炎框 | 当前默认训练配置中**未列入**，作为检测测试集使用 | 9077 / 478 / 244 文件存在，但不等于已用于训练 |

**容易被问：为什么不只用一个数据集？** 单个数据集通常只覆盖一种任务。Indiana 保留报告能力，VQA-RAD/SLAKE 提供问答，超声和 Kvasir 提供像素掩码与框，RSNA用于额外的胸片检测评估。统一模型的价值在于共享视觉语言表示，同时接入连续几何输出。

**数据来源与代码：**入口是 `tools/build_unified_dataset.py`；Indiana 转换见 `tools/converters/indiana.py`，公开数据转换见 `tools/converters/public.py`，超声见 `tools/converters/group_us.py`，Kvasir 见 `tools/converters/kvasir.py`。运行时各 builder 实际加载的是 `minigpt4/configs/datasets/*/*.yaml` 中指定的标注 JSON；不要只看 README 中的列表。

## 2. 离线预处理：从原始数据到统一标注

### 2.1 各数据集怎样转成训练材料

1. **Indiana：**按 `uid` 连接报告表和投照图表；清理 Open-i 的 `XXXX` 脱敏占位符，合并 findings 与 impression，过滤几乎为空的报告。按 `uid` 将同一检查的不同视角放入同一拆分，转换器生成约 76%/4%/20% 的 train/val/test。这避免同一报告的正侧位图跨集合泄漏。
2. **超声：**原始目录按患者/检查/帧存图像与合并掩码，报告以检查为单位。转换器将二值掩码做连通域分离，保存实例掩码；逐实例取最小外接框，并计算框面积比例；从报告提取 `anatomy_region`；记录报告、派生问答、框、掩码路径和 `K`。按患者 ID 分 train/val/test。**同一检查的多个帧可能共享同一份报告**，因此“每帧有独立人工报告”不准确。
3. **Kvasir：**从原始 bbox JSON 读取框、尺寸和类别，根据面积分 S/M/L；记录同名掩码路径，并根据目标数量、大小与位置生成模板问答。转换器按 `patient_id` 字段拆分，而该字段当前设为 `image_id`，实际效果是**图像级拆分**，不能称为真实患者级拆分。
4. **VQA-RAD / SLAKE / RSNA：**`public.py` 提供将继承的 MiniGPT-Med 格式映射到统一 schema 的转换器。注意此转换入口的默认输出名与训练配置使用的旧式文件名不完全一致；复现实验要逐一检查 `ann_path` 与文件是否一致。

统一记录的核心字段是 `image_id`、`image_path`、`modality`、`anatomy`、`image_size`、`tasks`。`tasks` 可包含 `report`、`vqa`、`grounded_caption`、`boxes`、`masks`、`K`；框记录含坐标、类别、尺度和可选解剖区域。**JSON 只存路径和元数据，图像/掩码在 Dataset 运行时加载。**

### 2.2 数据切分与防泄漏如何回答

- Indiana 使用 `uid` 分组；超声使用患者 ID 分组；两者都要防止同一人的图像或同一份报告跨 train/test。
- Kvasir 当前没有真实患者 ID，因此这里只能说按图像 ID 拆分。
- VQA-RAD、SLAKE 的 val 文件由 `tools/split_val.py`从原训练标注划出；公开数据的拆分方式需结合原始来源文件核对。
- test 只用于最终评估；训练中的 checkpoint 选择应只用 val。**但当前多数据集 val 加载逻辑有冲突，见第 7 节。**
- 病例数量、图像数量、问答对数量是不同统计口径；上述表格给的是 JSON 记录数，不能直接当患者数。

### 2.3 在线读取一条样本时发生什么

Dataset 返回 `image`、`instruction_input`、`answer`、`image_id`，结构化数据集还返回 `boxes`、`box_scales`、`anatomy_regions`、`masks`、`K` 与 `has_structured_supervision`。超声和 Kvasir 从可用任务中随机抽取一个任务；有病灶时才开放 refer/identify，VQA 仅在有有效问答时开放。比如同一帧本次抽到 `[segmentation]`，下次可抽到 `[detection]`，而**一次取样通常只监督一个任务答案**。

提示词的基本结构是 `[INST] <Img><ImageHere></Img> [任务标签] 问题 [/INST]`。`<ImageHere>` 在模型内被视觉 embedding 替换。报告/VQA/识别主要是文字答案；分割答案重复 `K` 次 `<SEG>`；检测答案对每个框给一个 `<BOX_S/M/L>`；指代定位答案包含 `<LOC>`。传统文本数据通过 `add_default_structured_fields()`补空框/空掩码等字段，以便混合 batch 保持 schema 一致。

### 2.4 图像和标注预处理细节

- Indiana 胸片及超声灰度图先转为 RGB 三通道；Kvasir 原本为彩色 RGB。训练 `blip2_image_train` 采用 `RandomResizedCrop(448)`、`ToTensor()`及 CLIP 风格 Normalize。默认独立评估脚本通过 `init_model()`取第一个数据集配置的 **train processor**，所以评估时也可能采用随机裁剪，需固定为确定性的 eval resize 才能稳定比较。
- 掩码读取时阈值化为 0/1 张量；框读取为 `[x1,y1,x2,y2]` 浮点张量。batch 内数量不同时，collater 对框补零并附 `box_padding_mask`；模型提取结构化目标时剔除补零框。掩码保留每样本一个列表。
- MedSAM 分支把图像插值到 512，图像编码后若特征不是 64×64，再插值成 64×64，以适配当前 mask decoder 的固定空间尺寸。EVA 路径与 MedSAM 路径共用输入图像张量的做法存在归一化问题，见第 7 节。

**高频问答：为什么要统一 schema？**“因为文字数据和结构化数据来源不同；统一字段可让训练入口用同一套 Dataset/模型 forward，缺失的几何标签用空值标记，结构化损失只在有标注的样本上启动。”

## 3. 训练：初始化、采样、前向、损失、优化

### 3.1 模型如何初始化

`train.py`读取配置、初始化分布式环境与随机种子，然后通过 registry 建数据集、模型和 runner。默认配置使用 EVA-ViT-G、LLaMA-2-7B Chat、LoRA，以及 MedSAM ViT-B 的稠密图像分支；`ckpt` 指向 MiniGPT-Med 权重，用于视觉语言部分的初始化。EVA 和 MedSAM 图像编码器按配置冻结；新增 token embedding、语言输出层、视觉投影、LoRA 和结构化预测头是主要可训练部分。LLaMA-3 另有独立配置，不能直接复用 LLaMA-2 的 MiniGPT-Med checkpoint。

**别背 README 的旧参数：**当前 LLaMA-2 训练 YAML 是 `batch_size=1/数据集`、`max_epoch=30`、`iters_per_epoch=5000`、`init_lr=5e-6`、`min_lr=5e-7`、`warmup_steps=1000`、`weight_decay=0.05`、`grad_clip=1.0`、`amp=True`、`accum_grad_iters=1`、`max_keep_ckpts=3`。`distributed=True` 表示启用分布式路径，实际 GPU 数取决于启动命令和环境，不应直接说固定三卡。README 的 100 epoch、batch size 2×3 等不是这份 YAML 的实际值。

### 3.2 多数据集与多任务如何采样

默认训练 YAML 列出 **6 个训练数据集**：Indiana、VQA-RAD、SLAKE VQA、SLAKE Grounding、Group-Breast US、Kvasir；RSNA只在 `evaluation_datasets` 中。它们的 `sample_ratio` 分别是 25、8、10、10、17、23。`ImageTextPretrainTask.build_datasets()`把比例挂到各训练数据集上，但当前 `reorg_datasets_by_split()`把多种 map-style 数据集交给 `ConcatDataset`；runner 注释也说明“未提供 train_dataset_ratio 时拼接数据集”。因此不能仅凭 YAML 就声称**实际执行了按这些比例的温度采样**，应先检查数据 loader 的真实类型与取样统计。单个超声/Kvasir样本内部再随机抽一个任务。

### 3.3 一个 batch 的前向与损失

1. EVA-ViT 输出视觉 token，按 4 个 patch 合并，线性投影到 LLaMA 隐藏维度。prompt 的 `<ImageHere>` 插入视觉 embedding，答案在 teacher forcing 下作为目标序列。
2. LLaMA 返回 logits 和最后一层 hidden states。普通词、特殊 token 的**生成决策**都由交叉熵监督；代码将 logits 转 FP32 再算 CE，并忽略 `-100` 的非目标位置。
3. 在目标答案中扫描 `<SEG>`、`<BOX_S/M/L>`、`<LOC>`，保留样本索引与出现顺序。`<BOX_*>` 进入对应尺度框头，与 GT 按样本和尺度配对后做加权 L1；`<LOC>` 进入定位头做框 L1；`<SEG>` 经投影与 MedSAM 特征一起进 mask decoder，做 BCE + Dice + 不确定性项。
4. mask–box 一致性函数仅在**同一样本同时出现 `<SEG>` 与 `<BOX_*>`**时计算；当前单任务采样下通常触发不了。解剖分类、GIoU、检测类别 CE、另两类一致性并未进入当前训练总损失。

用面试可讲的简式表示：`L = λ_text·CE + λ_det·L1_box + λ_loc·L1_loc + L_seg + λ_mb·L_cons`。其中 `L_seg` 内部含 BCE、Dice 和不确定性项。配置有 `loss_weights.seg`，但 `forward()`目前直接加 `L_seg`，没有再乘这个总系数；`cardinality` 的离散计数项也不能直接反传到 token 数量。

### 3.4 反向传播、稳定性与 checkpoint

runner 以 AdamW 只优化 `requires_grad=True` 的参数；矩阵权重用 weight decay，bias/归一化等参数不加衰减。学习率采用 warmup + cosine。`BaseTask` 的训练循环用 AMP `GradScaler`、梯度裁剪，并跳过 NaN/Inf loss 或梯度。每 epoch 保存 checkpoint，若验证指标改善则保存 `checkpoint_best.pth`，并保留最近若干普通 checkpoint。**这说明代码有稳定性保护，不等于已经证明训练不会发散。**

设计文档写了四阶段渐进训练；当前入口是单份联合微调 YAML。`curriculum_epochs: 8` 只是配置字段，模型当前没有把它设置为生效属性，也没有相应的 `set_curriculum_phase()`，不能说八轮冻结课程训练已经执行。

## 4. 推理：从一张图到文本、框和掩码

### 4.1 通用推理路径

1. 选择任务标签及问题，如 `[segmentation] Segment all visible lesions or nodules.`，用图像处理器生成张量，拼成对话格式。
2. `model.generate()`先对 EVA-ViT 特征和文本执行 LLaMA 自回归生成；默认评估使用 `do_sample=False`。没有特殊 token 就返回文本；出现特殊 token 才进入结构化解码。
3. `_run_second_pass()`把生成的 token 重新嵌入并与 prompt 拼接，再跑一次 LLaMA，取各特殊 token 位置的 hidden state。这一步用于恢复预测头输入；推理开销因此包括额外一次 LLaMA 前向。
4. `<SEG>`：一个 token 对应一个 sparse prompt，与 MedSAM 的稠密特征输入 mask decoder，得到一张概率掩码。`<BOX_S/M/L>`：调用对应框头，sigmoid 归一化后乘 `img_size`。`<LOC>`：调用定位框头。`raw_text` 会保留特殊 token，并在框 token 后插入坐标字符串供旧评估器解析。
5. 返回字典含 `text`、`raw_text`、`seg_count`、`box_tokens`、`has_loc`；请求 `return_masks=True` 时返回 `masks`，请求 `return_boxes=True` 时返回结构化 `boxes`。模型即使生成了 `<SEG>`，若未请求 `return_masks=True`，外层结果里也不会附掩码列表。

**可举的例子：**“乳腺超声输入 `[segmentation]`。如果模型生成两个 `<SEG>`，二次前向提取两个位置的 hidden state，分别作为 SAM 提示，输出两张掩码；如果生成零个，则 `masks=[]`。换成 `[detection]` 时，若输出 `<BOX_S>`，就由小目标头产生连续框坐标。”这是**机制举例**，不是实际效果证明。

### 4.2 LLaMA-2 与 LLaMA-3 的提示格式

原数据集多用 `[INST]...[/INST]`。`MiniGPTBase._to_chat_format()`在检测到 LLaMA-3 或配置指定时把它改成 LLaMA-3 header 格式；评估脚本也会选择相应 conversation template。面试中不要把“仓库有 LLaMA-3 配置”说成“默认训练就是 LLaMA-3”；实际模型家族、tokenizer、checkpoint 必须一致。

## 5. 评估：训练期验证和独立测试分开讲

### 5.1 训练期间如何选 checkpoint

`OmniRadTask.valid_step()`用 `model.generate()`统计文本、`seg_count`、框 token 等。`after_evaluation()`以预测 `<SEG>` 数等于样本 `K` 的比例作为 `cardinality_acc`，并把它返回为 `agg_metrics`，runner 用它挑选 `checkpoint_best.pth`。这**不是**综合 Dice/IoU/报告质量分数。非分割样本往往 `gt_K=0` 且 `seg_count=0`，会影响该指标的解释；需要在明确的分割验证集上单独统计。

### 5.2 独立测试脚本实际算什么

`eval_scripts/model_evaluation.py`读取 `eval_configs/omnirad_evaluation.yaml`，加载各 test JSON，按任务生成结果并在 `eval_results/omnirad/<dataset>/` 下保存预测和 `results.json`。任务与指标如下：

| 任务 | 测试集 | 当前脚本使用的指标 | 指标含义与注意事项 |
| --- | --- | --- | --- |
| 报告 | Indiana、Group-Breast US | SentenceTransformer 句向量 cosine（代码称 BERT-Sim）、BLEU-4、ROUGE-L、临床标签 micro/macro F1 | 语义相似、词面重合、最长公共子序列覆盖及胸片临床标签一致性；超声报告的胸片标签 F1 临床意义有限 |
| VQA | VQA-RAD、SLAKE VQA、Kvasir VQA | BERT-Sim | 问答语义相似；不能替代严格的诊断正确率或开放/封闭题分层准确率 |
| 检测 / 指代定位 | RSNA、Group-Breast US、Kvasir | 平均 IoU | 预测框与 GT 框交并比；多框时 US/Kvasir 用每个 GT 的最佳预测框再平均，并非一对一匹配 mAP |
| SLAKE Grounding | SLAKE Grounding | IoU | 解析 grounded caption 中的框并与 GT 比较 |
| 分割 | Group-Breast US、Kvasir | 平均 Dice | 预测掩码与 GT 掩码先分别合并成 union 再算 Dice，**不是逐实例 Dice** |
| 识别 | Group-Breast US、Kvasir | `identify_accuracy` | 实现中是 GT 类别字符串出现在预测文本中即算对，属于宽松的文本包含匹配 |

常用公式：`IoU = |B_pred ∩ B_gt| / |B_pred ∪ B_gt|`；`Dice = 2|M_pred ∩ M_gt| / (|M_pred| + |M_gt|)`。分割预测保存 PNG 时以 0.5 阈值二值化。**这份测试脚本的 US/Kvasir 路径主要报告 Dice 和 IoU；README 所列 Mask IoU、GIoU、ReasonSeg gIoU/cIoU、K=0 假阳性率并非都由当前入口实际输出。**

### 5.3 如何设计可信的对比实验

在同一 test split、同一图像预处理和同一任务提示下比较 MiniGPT-Med、OmniRad 及其他基线；报告结果同时写样本量、指标定义、均值和波动。针对创新点做消融：① 去掉 MedSAM/分割头；② 单一 BOX 头对比 S/M/L 三头；③ 关掉不确定性损失；④ 有效接通联合任务采样后比较有无 mask–box 一致性；⑤ 单独测试 K=0、K≥2、小目标。当前仓库 README 结果仍为 TBD，**消融属于建议的验证设计，不能写成已完成实验**。

### 5.4 评估入口的复现注意点

`eval_scripts/metrics.py`在 import 时就加载本地 SentenceTransformer，要求 `BERT_MODEL_PATH` 或 `weights/bert_model/modules.json` 存在，即使只想跑空间指标也会经过该模块。该文件还导入 `eval_scripts.chexbert`，但当前仓库的 `eval_scripts` 目录中未见 `chexbert.py`，所以报告评估入口按现状可能无法直接导入，运行前需补齐依赖或改造导入。评估 YAML 的 checkpoint 是绝对 Linux 路径，在当前工作区运行需要替换为真实权重路径。**不要仅凭脚本存在就说所有指标已成功跑出。**

## 6. 可直接背的流程追问

### Q1：一条超声样本从原始数据到模型输入经历什么？

> 原始帧、掩码和检查报告先离线转换。连通域把合并掩码拆成实例，实例掩码生成 bbox 和 S/M/L 尺度，报告提供文字与可选解剖区域，再按患者分拆分。Dataset 加载图像和掩码、读框与 K，随机选一个任务，构造 `[任务标签] + <ImageHere>` 的 instruction 和相应答案，最后 collater 处理不同实例数。

### Q2：为什么报告/VQA 数据也能混进结构化模型训练？

> 它们仍训练视觉编码到语言模型的语义链路。缺少框和掩码的样本补空结构化字段，`has_structured_supervision=False`，模型只算文本 CE；有结构化标注的样本再启动检测、定位或分割损失。

### Q3：为什么分割要 EVA 和 MedSAM 两条视觉路径？

> EVA 给语言模型语义 token，用来理解问题、决定病灶数量和输出 token；MedSAM 给像素空间特征，供 mask decoder恢复边界。一个主要回答“是什么”，另一个主要支持“在哪里”。

### Q4：训练时 token 与 GT 怎样配对，推理时又怎样配对？

> 训练是 teacher forcing：答案中每个特殊 token 的位置和样本索引是已知的，按同一样本的标注顺序配对。推理先让模型自由生成，再定位实际出现的特殊 token，通过二次前向取隐藏状态送入对应头。生成错误的 token 类型或数量会直接影响后续几何输出。

### Q5：为什么需要二次前向？代价是什么？

> 当前 `generate()`首先拿到生成 token 序列，随后统一恢复这些 token 的隐藏状态用于几何头，而不是在自回归生成过程中逐 token 拿隐藏状态。好处是几种结构化输出共用一次恢复过程；代价是额外一次 LLaMA 前向和相应显存/时延。

### Q6：怎么证明小病灶改进来自尺度感知，而不是数据更多？

> 固定训练数据、主干、训练步数和评估集，只把单 BOX 头替换为三尺度头；按小、中、大目标分组报告 IoU 或召回，并比较总体结果。当前仓库没有足够的正式消融结果，面试中应说清实验设计与待补证据。

### Q7：怎么防止医疗数据泄漏？

> 优先按患者/检查分组，而非随机按图像拆分；同一检查的多帧和报告只能出现在一个 split。公开数据若无患者 ID，要说明拆分粒度和限制。所有模板派生问答应仅基于本 split 的原标注生成，test 不参与训练和调参。

### Q8：最需要先修的复现问题是什么？

> 第一，图像 `RandomResizedCrop` 需要与 bbox、mask 同步几何变换，评估改成确定性预处理；第二，MedSAM 需要独立的原始 RGB 预处理；第三，统一转换器的输出文件名与 builder 读取路径需要对齐；第四，多个 val 数据集与 runner 的“只支持一个 val”逻辑需要协调。完成这些后才能解释 Dice/IoU 和比较创新点收益。

## 7. 当前代码与文档必须区分的边界

1. **训练数据数目：**默认训练 YAML 是 6 个数据集，RSNA 在评估配置中；README 有“7 个训练数据集”的旧描述。
2. **验证集冲突：**多个 builder 配置 `val_ann_path`，但 `concat_datasets()`在非 train split 上断言只能有一个数据集；当前默认配置不能直接等同于已成功完成多数据集训练与 best checkpoint 选择。
3. **转换文件名冲突：**`public.py` 默认生成 `radvqa_train.json`、`slake_train.json`、`rsna_eval.json`，训练/评估配置读取 `vqa_train.json`、`grounding_train_SLAKE.json`、`RSNA_test.json` 等旧文件。现存文件可能已由其他流程准备，复现时必须明确来源。
4. **图像与几何标注未同步增强：**随机裁剪只施加于图像，原始框和掩码未跟着同一变换；结构化指标和损失可能失真。
5. **MedSAM 输入归一化：**目前共用已经为 EVA 归一化的输入，MedSAM 又按自己的均值方差处理，需单独规范其输入范围。
6. **K=0 与多实例：**代码形式上允许 `K=0` 和多个 `<SEG>`，但现有数据转换与 Kvasir 掩码路径不保证足够的零病灶或逐实例监督。
7. **尚未闭环的创新：**不确定性图未作为推理返回/拒判依据；解剖分类未训练；mask–box 一致性在单任务采样中很难触发；其余两类一致性未实现。
8. **评估依赖与权重：**本地 BERT 模型、`eval_scripts.chexbert`、MedSAM/LLaMA 权重和评估 YAML 中的 checkpoint 路径都要实际可用；本仓库的 README 指标占位不能当结果。

**最后的面试收束：**“我能把数据构建、样本级任务选择、双视觉路径、token 路由、联合损失、二次前向解码和按任务评估串成一条可追溯的代码链；同时我会明确哪些是已经接通的实现，哪些还要修复数据对齐并做消融才能证明有效。”

