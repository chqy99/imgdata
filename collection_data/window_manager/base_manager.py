from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class WindowRect:
    left: int
    top: int
    width: int
    height: int

    def to_dict(self):
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height
        }


@dataclass
class WindowInfo:
    id: str  # 在 Windows 上是 hwnd，Linux 是窗口 ID
    title: str
    index: int
    rect: WindowRect


class BaseWindowManager(ABC):
    """跨平台 WindowManager 基类"""

    @abstractmethod
    def list_windows(self) -> List[WindowInfo]:
        """返回所有窗口信息"""
        pass

    @abstractmethod
    def focus_window(self, title: str, index: int = 0):
        """根据窗口标题聚焦窗口"""
        pass

    @abstractmethod
    def get_active_window(self) -> Optional[WindowInfo]:
        """返回当前活动窗口信息"""
        pass

    @abstractmethod
    def resize_window(self, title: str, width: int, height: int, index: int = 0):
        """调整窗口大小"""
        pass

    @abstractmethod
    def move_window(self, title: str, x: int, y: int, index: int = 0):
        """移动窗口"""
        pass

    @abstractmethod
    def capture_window(self, title: str, index: int = 0):
        """给窗口截图"""
        pass
