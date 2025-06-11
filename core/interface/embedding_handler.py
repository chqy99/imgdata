from abc import ABC, abstractmethod
import numpy as np

class EmbeddingModule(ABC):
    @abstractmethod
    def get_embedding(self, image: np.ndarray) -> np.ndarray:
        """
        根据输入图像计算并返回 embedding 向量
        """
        pass
