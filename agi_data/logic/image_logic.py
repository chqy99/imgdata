from typing import Union, Literal
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from agi_data.data.raw.image_raw import RawImage
from agi_data.types import NDArray, PILImage


def np_to_base64(img: np.ndarray, format: str = "PNG") -> str:
    """
    通用工具函数：将 numpy.ndarray 图像编码为 base64 字符串
    """
    pil_img = Image.fromarray(img.astype("uint8"))
    buffer = BytesIO()
    pil_img.save(buffer, format=format)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def base64_to_np(b64_str: str) -> np.ndarray:
    """
    通用工具函数：将 base64 字符串解码为 numpy.ndarray 图像
    """
    buffer = BytesIO(base64.b64decode(b64_str))
    pil_img = Image.open(buffer).convert("RGB")
    return np.array(pil_img)

def raw_image_convert(raw_img: RawImage, target_format: Literal["np.ndarray", "PIL.Image", "base64"]) -> Union[NDArray, PILImage, str]:
    """
    RawImage格式转换：将RawImage的data转换为目标格式
    输入：RawImage实例 + 目标格式
    输出：转换后的data（不修改原始RawImage的data）
    """
    if raw_img.data_format == target_format:
        return raw_img.data

    # 1. 统一先转为np.ndarray（中间格式）
    if raw_img.data_format == "PIL.Image":
        np_data = np.array(raw_img.data.convert("RGB"))
    elif raw_img.data_format == "base64":
        # 解析base64为np.ndarray（业务逻辑，不放在dataclass）
        base64_str = raw_img.data.split(",")[-1]  # 去掉data:image/前缀
        img_bytes = base64.b64decode(base64_str)
        pil_img = Image.open(BytesIO(img_bytes)).convert("RGB")
        np_data = np.array(pil_img)
    else:  # np.ndarray
        np_data = raw_img.data.copy()

    # 2. 转为目标格式
    if target_format == "PIL.Image":
        return Image.fromarray(np_data)
    elif target_format == "base64":
        pil_img = Image.fromarray(np_data)
        buffer = BytesIO()
        pil_img.save(buffer, format="PNG")
        base64_str = f"data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode('utf-8')}"
        return base64_str
    else:  # np.ndarray
        return np_data