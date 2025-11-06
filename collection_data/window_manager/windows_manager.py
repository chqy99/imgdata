import time
from typing import List, Optional

import pygetwindow as gw
import pyautogui
import mss
from PIL import Image

from .base_manager import BaseWindowManager, WindowInfo, WindowRect


class WindowsWindowManager(BaseWindowManager):
    def __init__(self):
        self._windows_cache: List[WindowInfo] = self.list_windows()

    # --------------------------------------------------
    def list_windows(self) -> List[WindowInfo]:
        """
        用 pygetwindow 枚举所有可见窗口
        与 win32gui 版本返回结构一致
        """
        windows: List[WindowInfo] = []

        # pygetwindow 的返回值就是窗口对象
        for w in gw.getAllWindows():
            if not w.visible:
                continue
            # 计算并构造 WindowRect
            rect = WindowRect(
                left=w.left,
                top=w.top,
                width=w.width,
                height=w.height
            )
            windows.append(WindowInfo(
                id=str(w._hWnd),  # 内部句柄
                title=w.title,
                index=0,  # 临时
                rect=rect
            ))

        # 给同名窗口编号
        title_count = {}
        for w in windows:
            t = w.title
            title_count[t] = title_count.get(t, -1) + 1
            w.index = title_count[t]

        self._windows_cache = windows
        return windows

    # --------------------------------------------------
    def _find_window(self, title: str, index: int = 0) -> Optional[WindowInfo]:
        # 缓存里找
        for w in self._windows_cache:
            if w.title == title and w.index == index:
                return w
        return None

    # --------------------------------------------------
    def focus_window(self, title: str, index: int = 0):
        """
        激活窗口：pygetwindow 自带方法
        """
        win = self._find_window(title, index)
        if not win:
            return

        try:
            w = gw.getWindowsWithTitle(title)[index]
            if w.isMinimized:
                w.restore()
            w.activate()
            time.sleep(0.1)
        except Exception:
            pass

    # --------------------------------------------------
    def get_active_window(self) -> Optional[WindowInfo]:
        try:
            w = gw.getActiveWindow()
            if not w:
                return None
        except Exception:
            return None

        # 计算 index
        index = 0
        title = w.title
        for cached in self._windows_cache:
            if cached.title == title and str(cached.id) == str(w._hWnd):
                index = cached.index
                break

        rect = WindowRect(w.left, w.top, w.width, w.height)
        return WindowInfo(
            id=str(w._hWnd),
            title=title,
            index=index,
            rect=rect
        )

    # --------------------------------------------------
    def resize_window(self, title: str, width: int, height: int, index: int = 0):
        win = self._find_window(title, index)
        if win:
            try:
                w = gw.getWindowsWithTitle(title)[index]
                w.resizeTo(width, height)
            except Exception:
                pass

    # --------------------------------------------------
    def move_window(self, title: str, x: int, y: int, index: int = 0):
        win = self._find_window(title, index)
        if win:
            try:
                w = gw.getWindowsWithTitle(title)[index]
                w.moveTo(x, y)
            except Exception:
                pass

    # --------------------------------------------------
    def capture_window(self, title: str, index: int = 0) -> Optional[Image.Image]:
        """
        用 mss 截窗口，逻辑与原 win32gui 版一致
        """
        win = self._find_window(title, index)
        if not win:
            return None

        rect_dict = win.rect.to_dict()
        with mss.mss() as sct:
            sct_img = sct.grab(rect_dict)

        # BGRX -> RGB
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
