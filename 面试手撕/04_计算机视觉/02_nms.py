"""检测框 Non-Maximum Suppression 实现。"""

from __future__ import annotations

import math

import numpy as np


def _validate_boxes(boxes: np.ndarray) -> np.ndarray:
    """验证连续 xyxy 检测框。"""
    candidate_boxes = np.asarray(boxes, dtype=np.float64)
    if candidate_boxes.ndim != 2 or candidate_boxes.shape[1] != 4 or not np.all(np.isfinite(candidate_boxes)):
        raise ValueError("boxes 必须是仅含有限数值的 [N, 4] xyxy 数组。")
    if np.any(candidate_boxes[:, 2] < candidate_boxes[:, 0]) or np.any(candidate_boxes[:, 3] < candidate_boxes[:, 1]):
        raise ValueError("检测框的右下坐标不能小于左上坐标。")
    return candidate_boxes


def _iou_one_to_many(box: np.ndarray, boxes: np.ndarray) -> np.ndarray:
    top_left = np.maximum(box[:2], boxes[:, :2])
    bottom_right = np.minimum(box[2:], boxes[:, 2:])
    intersection_wh = np.maximum(bottom_right - top_left, 0.0)
    intersection = intersection_wh[:, 0] * intersection_wh[:, 1]
    area_box = (box[2] - box[0]) * (box[3] - box[1])
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    union = area_box + areas - intersection
    return np.divide(intersection, union, out=np.zeros_like(intersection), where=union > 0)


def non_maximum_suppression(
    boxes: np.ndarray,
    scores: np.ndarray,
    iou_threshold: float = 0.5,
) -> np.ndarray:
    """按分数从高到低保留非重叠框，同分框按原始下标稳定处理。"""
    candidate_boxes = _validate_boxes(boxes)
    candidate_scores = np.asarray(scores, dtype=np.float64)
    if candidate_scores.shape != (candidate_boxes.shape[0],) or not np.all(np.isfinite(candidate_scores)):
        raise ValueError("scores 必须与 boxes 数量一致且仅含有限数值。")
    if not math.isfinite(float(iou_threshold)) or not 0.0 <= iou_threshold <= 1.0:
        raise ValueError("iou_threshold 必须是 [0, 1] 范围内的有限数值。")

    order = np.lexsort((np.arange(len(candidate_scores)), -candidate_scores))
    kept: list[int] = []
    while len(order) > 0:
        current_index = int(order[0])
        kept.append(current_index)
        if len(order) == 1:
            break
        remaining = order[1:]
        ious = _iou_one_to_many(candidate_boxes[current_index], candidate_boxes[remaining])
        order = remaining[ious <= iou_threshold]
    return np.asarray(kept, dtype=np.int64)


if __name__ == "__main__":
    sample_boxes = np.array([[0, 0, 2, 2], [0.2, 0.2, 2.2, 2.2], [5, 5, 7, 7]], dtype=float)
    sample_scores = np.array([0.9, 0.8, 0.7])
    print("保留下标:", non_maximum_suppression(sample_boxes, sample_scores, 0.5))
