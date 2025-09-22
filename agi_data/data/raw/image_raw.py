from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Any, Literal
from agi_data.types import NDArray, PILImage
from agi_data.common.storage import StorageInfo

@dataclass
class RawImage:
    uid: Optional[str] = None
    data_format: Literal["np.ndarray", "PIL.Image", "base64"]
    data: Union[NDArray, PILImage, str]
    width: Optional[int] = None
    height: Optional[int] = None
    storage: Optional[StorageInfo] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.uid:
            from agi_data.logic.id_generator import generate_raw_uid
            self.uid = generate_raw_uid(media_type="image")
        if self.data_format == "np.ndarray" and hasattr(self.data, "ndim") and self.data.ndim == 3:
            self.height, self.width = self.data.shape[:2]
        elif self.data_format == "PIL.Image":
            self.width, self.height = self.data.size
        elif self.data_format == "base64":
            if not self.data.startswith("data:image/"):
                raise ValueError("base64格式无效：需带data:image/前缀")
        if not (self.width and self.height):
            raise ValueError("无法提取图像尺寸，请检查data格式")