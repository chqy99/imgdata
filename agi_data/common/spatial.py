from dataclasses import dataclass
from typing import Union

@dataclass
class BBox:
    x1: Union[int, float]  # 左边界（水平坐标）
    y1: Union[int, float]  # 上边界（垂直坐标）
    x2: Union[int, float]  # 右边界（水平坐标）
    y2: Union[int, float]  # 下边界（垂直坐标）

    def __post_init__(self):
        if self.x1 >= self.x2 or self.y1 >= self.y2:
            raise ValueError("BBox无效：x1 >= x2 或 y1 >= y2")