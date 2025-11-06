import platform
from .base_manager import BaseWindowManager, WindowInfo, WindowRect

if platform.system() == "Windows":
    from .windows_manager import WindowsWindowManager as WindowManager
else:
    from .linux_manager import LinuxWindowManager as WindowManager

__all__ = ["WindowManager", "BaseWindowManager", "WindowInfo", "WindowRect"]
