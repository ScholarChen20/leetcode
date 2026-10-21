"""Minimal object-detection metrics demo (axis-aligned XYXY boxes).

Run: python detection_metrics_demo.py

Input predictions should already be decoded and postprocessed (for example,
with NMS when the detector requires it). This implements one-to-one matching
and 101-point interpolated AP. It is intended for learning; official COCO
evaluation also handles crowd/ignore
regions, area ranges, maximum detections, and other details.
"""

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class GroundTruth:
    image_id: str
    class_id: int
    box: tuple[float, float, float, float]  # x1, y1, x2, y2


@dataclass(frozen=True)
class Prediction:
    image_id: str
    class_id: int
    score: float
    box: tuple[float, float, float, float]


def box_iou(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    """Intersection over union of two XYXY boxes."""
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area_a = max(0.0, a[2] - a[0]) * max(0.0, a[3] - a[1])
    area_b = max(0.0, b[2] - b[0]) * max(0.0, b[3] - b[1])
    union = area_a + area_b - intersection
    return intersection / union if union > 0 else 0.0


def match_class(
    predictions: list[Prediction],
    ground_truths: list[GroundTruth],
    class_id: int,
    iou_threshold: float,
) -> tuple[list[tuple[int, int]], int]:
    """Return score-ordered (TP, FP) flags and number of GTs for one class.

    Matching is within the same image and class. Each GT can be used once.
    A duplicate detection therefore becomes an FP.
    """
    gt_by_image: dict[str, list[GroundTruth]] = defaultdict(list)
    for gt in ground_truths:
        if gt.class_id == class_id:
            gt_by_image[gt.image_id].append(gt)

    used_indices: dict[str, set[int]] = defaultdict(set)
    flags: list[tuple[int, int]] = []
    class_predictions = sorted(
        (p for p in predictions if p.class_id == class_id),
        key=lambda p: p.score,
        reverse=True,
    )
    for pred in class_predictions:
        best_iou, best_index = 0.0, -1
        for index, gt in enumerate(gt_by_image[pred.image_id]):
            if index in used_indices[pred.image_id]:
                continue
            overlap = box_iou(pred.box, gt.box)
            if overlap > best_iou:
                best_iou, best_index = overlap, index
        if best_index >= 0 and best_iou >= iou_threshold:
            used_indices[pred.image_id].add(best_index)
            flags.append((1, 0))
        else:
            flags.append((0, 1))

    return flags, sum(map(len, gt_by_image.values()))


def interpolated_ap(flags: list[tuple[int, int]], num_gt: int) -> float:
    """101-point interpolated area under the precision-recall curve."""
    if num_gt == 0:
        raise ValueError("AP is undefined for a class without ground truths")

    precision, recall = [], []
    tp_total = fp_total = 0
    for tp, fp in flags:
        tp_total += tp
        fp_total += fp
        precision.append(tp_total / (tp_total + fp_total))
        recall.append(tp_total / num_gt)

    # At each recall level, take the best precision at that or higher recall.
    return sum(
        max((p for p, r in zip(precision, recall) if r >= k / 100), default=0.0)
        for k in range(101)
    ) / 101


def evaluate(
    predictions: list[Prediction],
    ground_truths: list[GroundTruth],
    confidence_threshold: float = 0.5,
) -> dict:
    """Compute mAP50, mAP50-95, and micro P/R/F1 at a fixed threshold."""
    classes = sorted({gt.class_id for gt in ground_truths})
    if not classes:
        raise ValueError("At least one ground-truth box is required")

    iou_thresholds = [round(0.50 + 0.05 * i, 2) for i in range(10)]
    ap_by_class = {}
    for class_id in classes:
        ap_by_class[class_id] = {}
        for threshold in iou_thresholds:
            flags, num_gt = match_class(
                predictions, ground_truths, class_id, threshold
            )
            ap_by_class[class_id][threshold] = interpolated_ap(flags, num_gt)

    map50 = sum(ap_by_class[c][0.5] for c in classes) / len(classes)
    map50_95 = sum(
        ap_by_class[c][t] for c in classes for t in iou_thresholds
    ) / (len(classes) * len(iou_thresholds))

    selected = [p for p in predictions if p.score >= confidence_threshold]
    tp = fp = fn = 0
    for class_id in classes:
        flags, num_gt = match_class(selected, ground_truths, class_id, 0.5)
        class_tp = sum(item[0] for item in flags)
        tp += class_tp
        fp += sum(item[1] for item in flags)
        fn += num_gt - class_tp
    # Predictions of a class absent from GT are false positives too.
    fp += sum(p.class_id not in classes for p in selected)

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "AP50_by_class": {c: ap_by_class[c][0.5] for c in classes},
        "mAP50": map50,
        "mAP50_95": map50_95,
        "confidence_threshold": confidence_threshold,
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "precision": precision,
        "recall": recall,
        "F1": f1,
    }


if __name__ == "__main__":
    ground_truths = [
        GroundTruth("image_1", 0, (0, 0, 100, 100)),
        GroundTruth("image_2", 0, (20, 20, 80, 80)),
        GroundTruth("image_1", 1, (200, 200, 300, 300)),
    ]
    predictions = [
        Prediction("image_1", 0, 0.95, (0, 0, 100, 100)),  # TP
        Prediction("image_2", 0, 0.92, (150, 150, 180, 180)),  # FP
        Prediction("image_2", 0, 0.85, (20, 20, 80, 80)),  # TP
        Prediction("image_1", 0, 0.60, (0, 0, 100, 100)),  # duplicate FP
        Prediction("image_1", 1, 0.90, (210, 210, 310, 310)),  # IoU ~0.68
    ]
    for key, value in evaluate(predictions, ground_truths).items():
        print(f"{key}: {value}")
