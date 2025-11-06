import subprocess
import re
from typing import List, Optional
import mss
from PIL import Image
from .base_manager import BaseWindowManager, WindowInfo, WindowRect

def _get_client_geometry(win_id: str) -> WindowRect:
    import re, subprocess, struct, sys

    # 1. 先尝试读 _GTK_FRAME_EXTENTS 或 _KDE_NET_WM_FRAME_STRUT
    try:
        xprop_out = subprocess.check_output(
            ["xprop", "-id", win_id, "_GTK_FRAME_EXTENTS", "_KDE_NET_WM_FRAME_STRUT"]
        ).decode()
    except FileNotFoundError:
        xprop_out = ""

    frame = [0, 0, 0, 0]  # left, right, top, bottom
    for line in xprop_out.splitlines():
        if "_GTK_FRAME_EXTENTS" in line or "_KDE_NET_WM_FRAME_STRUT" in line:
            nums = list(map(int, re.findall(r"\d+", line)))  # 可能有 4 或 8 个值
            if len(nums) >= 4:
                frame = nums[:4]
            break

    # 2. 再拿绝对坐标
    try:
        xwi_out = subprocess.check_output(["xwininfo", "-id", win_id]).decode()
    except FileNotFoundError:
        raise RuntimeError("请先安装 xwininfo (sudo apt install x11-utils)")

    def extract(key: str) -> int:
        return int(re.search(rf"{key}:\s+(\d+)", xwi_out).group(1))

    abs_x = extract("Absolute upper-left X")
    abs_y = extract("Absolute upper-left Y")
    w = extract("Width")
    h = extract("Height")

    # 3. 减去阴影/框架
    left, right, top, bottom = frame
    return WindowRect(
        left=abs_x + left,
        top=abs_y + top,
        width=w - left - right,
        height=h - top - bottom,
    )

class LinuxWindowManager(BaseWindowManager):
    """Linux 平台的 WindowManager 实现（依赖 wmctrl + xdotool + xprop）"""

    def list_windows(self) -> List[WindowInfo]:
        """返回所有窗口信息"""
        try:
            output = subprocess.check_output(["wmctrl", "-lG"]).decode("utf-8")
        except FileNotFoundError:
            raise RuntimeError("请先安装 wmctrl (sudo apt install wmctrl)")

        windows = []
        for line in output.strip().split("\n"):
            parts = line.split(None, 7)
            if len(parts) >= 8:
                win_id, _, _, _, _, _, _, title = parts
                rect = _get_client_geometry(win_id)
                windows.append(WindowInfo(
                    id=win_id,
                    title=title.strip(),
                    index=0,  # 临时，后面会重新计算
                    rect=rect
                ))
        # 给同名窗口添加 index
        title_count = {}
        for w in windows:
            t = w.title
            title_count[t] = title_count.get(t, -1) + 1
            w.index = title_count[t]

        return windows

    def focus_window(self, title: str, index: int = 0):
        """根据窗口标题聚焦窗口（支持同名窗口用 index 区分）"""
        windows = [w for w in self.list_windows() if title in w.title]
        if not windows:
            raise ValueError(f"未找到标题包含 '{title}' 的窗口")
        if index >= len(windows):
            raise ValueError(f"窗口索引超出范围: {index}")
        win_id = windows[index].id
        subprocess.run(["xdotool", "windowmap", win_id], check=False)
        subprocess.run(["xdotool", "windowactivate", win_id], check=False)

    def get_active_window(self) -> Optional[WindowInfo]:
        """返回当前活动窗口信息"""
        try:
            active_id = subprocess.check_output(
                ["xdotool", "getactivewindow"]
            ).decode("utf-8").strip()
        except FileNotFoundError:
            raise RuntimeError("请先安装 xdotool (sudo apt install xdotool)")

        for w in self.list_windows():
            if int(w.id, 16) == int(active_id):
                return w
        return None

    def resize_window(self, title: str, width: int, height: int, index: int = 0):
        """调整窗口大小"""
        windows = [w for w in self.list_windows() if title in w.title]
        if not windows:
            raise ValueError(f"未找到标题包含 '{title}' 的窗口")
        if index >= len(windows):
            raise ValueError(f"窗口索引超出范围: {index}")
        win_id = windows[index].id
        subprocess.run(["wmctrl", "-ir", win_id, "-e", f"0,{windows[index].rect.left},{windows[index].rect.top},{width},{height}"])

    def move_window(self, title: str, x: int, y: int, index: int = 0):
        """移动窗口"""
        windows = [w for w in self.list_windows() if title in w.title]
        if not windows:
            raise ValueError(f"未找到标题包含 '{title}' 的窗口")
        if index >= len(windows):
            raise ValueError(f"窗口索引超出范围: {index}")
        win_id = windows[index].id
        subprocess.run(["wmctrl", "-ir", win_id, "-e", f"0,{x},{y},{windows[index].rect.width},{windows[index].rect.height}"])

    def capture_window(self, title: str, index: int = 0):
        """给窗口截图"""
        windows = [w for w in self.list_windows() if title in w.title]
        if not windows:
            raise ValueError(f"未找到标题包含 '{title}' 的窗口")
        if index >= len(windows):
            raise ValueError(f"窗口索引超出范围: {index}")
        w = windows[index]
        rect = w.rect.to_dict()

        with mss.mss() as sct:
            sct_img = sct.grab(rect)

        # BGRX -> RGB
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        return img
