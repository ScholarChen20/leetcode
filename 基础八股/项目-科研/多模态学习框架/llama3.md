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
