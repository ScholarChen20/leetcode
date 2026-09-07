"""二值图像 4 邻域连通域搜索实现。"""

from __future__ import annotations

from collections import deque

import numpy as np


def connected_components(binary_image: np.ndarray) -> list[list[tuple[int, int]]]:
    """返回所有值为真/非零像素组成的 4 邻域连通域坐标列表。"""
    image = np.asarray(binary_image, dtype=bool)
    if image.ndim != 2:
        raise ValueError("binary_image 必须是二维数组。")

    height, width = image.shape
    visited = np.zeros_like(image, dtype=bool)
    components: list[list[tuple[int, int]]] = []
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))

    for row in range(height):
        for col in range(width):
            if not image[row, col] or visited[row, col]:
                continue
            queue: deque[tuple[int, int]] = deque([(row, col)])
            visited[row, col] = True
            component: list[tuple[int, int]] = []
            while queue:
                current_row, current_col = queue.popleft()
                component.append((current_row, current_col))
                for row_offset, col_offset in directions:
                    next_row = current_row + row_offset
                    next_col = current_col + col_offset
                    if (
                        0 <= next_row < height
                        and 0 <= next_col < width
                        and image[next_row, next_col]
                        and not visited[next_row, next_col]
                    ):
                        visited[next_row, next_col] = True
                        queue.append((next_row, next_col))
            components.append(component)
    return components


if __name__ == "__main__":
    mask = np.array([[1, 1, 0, 0], [0, 1, 0, 1], [0, 0, 0, 1], [1, 0, 0, 0]])
    print("连通域:", connected_components(mask))
