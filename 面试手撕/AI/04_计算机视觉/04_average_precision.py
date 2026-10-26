"""单类别目标检测 Average Precision (AP) 计算实现。"""

from __future__ import annotations

from collections.abc import Hashable, Mapping, Sequence

import math
import numpy as np


def _as_valid_box(box: Sequence[float], field_name: str) -> np.ndarray:
    """验证并返回连续坐标系中的 xyxy 框。"""
    values = np.asarray(box, dtype=np.float64)
    if values.shape != (4,) or not np.all(np.isfinite(values)):
        raise ValueError(f"{field_name} 必须是包含 4 个有限数值的 xyxy 框。")
    if values[2] < values[0] or values[3] < values[1]:
        raise ValueError(f"{field_name} 的右下坐标不能小于左上坐标。")
    return values


def _iou(box_a: np.ndarray, box_b: np.ndarray) -> float:
    top_left = np.maximum(box_a[:2], box_b[:2])
    bottom_right = np.minimum(box_a[2:], box_b[2:])
    wh = np.maximum(bottom_right - top_left, 0.0)
    intersection = wh[0] * wh[1]
    area_a = (box_a[2] - box_a[0]) * (box_a[3] - box_a[1])
    area_b = (box_b[2] - box_b[0]) * (box_b[3] - box_b[1])
    union = area_a + area_b - intersection
    return float(intersection / union) if union > 0 else 0.0


def average_precision(
    predictions: Sequence[tuple[Hashable, float, Sequence[float]]],
    ground_truths: Mapping[Hashable, Sequence[Sequence[float]]],
    iou_threshold: float = 0.5,
) -> float:
    """计算单类别 AP。

    同置信度预测采用 ``image_id + xyxy`` 的确定性次级排序，保证输入列表顺序
    改变不会导致 AP 改变。坐标使用连续 ``xyxy`` 约定。
    """
    if not math.isfinite(iou_threshold) or not 0.0 <= iou_threshold <= 1.0:
        raise ValueError("iou_threshold 必须是 [0, 1] 范围内的有限数值。")

    normalized_ground_truths = {
        image_id: [_as_valid_box(box, f"ground_truths[{image_id!r}]") for box in boxes]
        for image_id, boxes in ground_truths.items()
    }
    total_ground_truths = sum(len(boxes) for boxes in normalized_ground_truths.values())
    if total_ground_truths == 0:
        raise ValueError("至少需要一个真实框。")

    normalized_predictions: list[tuple[Hashable, float, np.ndarray]] = []
    for image_id, confidence, box in predictions:
        score = float(confidence)
        if not math.isfinite(score):
            raise ValueError("预测置信度必须是有限数值。")
        normalized_predictions.append((image_id, score, _as_valid_box(box, "prediction")))

    matched = {image_id: np.zeros(len(boxes), dtype=bool) for image_id, boxes in normalized_ground_truths.items()}
    ordered_predictions = sorted(
        normalized_predictions,
        key=lambda item: (-item[1], repr(item[0]), tuple(item[2].tolist())),
    )
    true_positive = np.zeros(len(ordered_predictions))
    false_positive = np.zeros(len(ordered_predictions))

    for index, (image_id, _, candidate) in enumerate(ordered_predictions):
        gt_boxes = normalized_ground_truths.get(image_id, [])
        if not gt_boxes:
            false_positive[index] = 1
            continue
        ious = np.array([_iou(candidate, gt_box) for gt_box in gt_boxes])
        best_index = int(ious.argmax())
        if ious[best_index] >= iou_threshold and not matched[image_id][best_index]:
            true_positive[index] = 1
            matched[image_id][best_index] = True
        else:
            false_positive[index] = 1

    cumulative_tp = np.cumsum(true_positive)
    cumulative_fp = np.cumsum(false_positive)
    recall = cumulative_tp / total_ground_truths
    precision = cumulative_tp / np.maximum(cumulative_tp + cumulative_fp, 1e-12)
    recall = np.concatenate(([0.0], recall, [1.0]))
    precision = np.concatenate(([1.0], precision, [0.0]))
    precision = np.maximum.accumulate(precision[::-1])[::-1]
    return float(np.sum((recall[1:] - recall[:-1]) * precision[1:]))


if __name__ == "__main__":
    gt = {"image_1": [[0, 0, 2, 2]], "image_2": [[1, 1, 3, 3]]}
    preds = [
        ("image_1", 0.95, [0, 0, 2, 2]),
        ("image_2", 0.90, [0, 0, 1, 1]),
        ("image_2", 0.80, [1, 1, 3, 3]),
    ]
    print("AP:", average_precision(preds, gt))
