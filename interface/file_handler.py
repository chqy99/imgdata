from abc import ABC, abstractmethod
import numpy as np

class FileHandlerBase(ABC):
    @abstractmethod
    def save_image(self, image: np.ndarray, filename: str) -> str:
        """
        保存图像，返回保存后的文件路径
        """
        pass

    @abstractmethod
    def save_mask(self, mask: np.ndarray, filename: str) -> str:
        """
        保存掩码，返回保存后的文件路径
        """
        pass

    @abstractmethod
    def load_image(self, path: str) -> np.ndarray:
        """
        从文件加载图像
        """
        pass

    @abstractmethod
    def load_mask(self, path: str) -> np.ndarray:
        """
        从文件加载掩码
        """
        pass
