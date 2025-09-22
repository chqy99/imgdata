# AGI 通用结构化数据（Python）白皮书

对象定义、格式转化、对象桥接、序列化与反序列化、文件式存储

## 一、背景与价值：从“原始数据”到“结构化体系”的必要性
在AGI（通用人工智能）研发中，“原始媒体数据”与“解析结果”的管理混乱是核心痛点：
- 未解析的原始数据（如一张图片、一段音频）缺乏统一结构化描述，导致多格式（np.ndarray、PIL.Image、base64）管理混乱；
- 解析结果（如图像中的物体框、音频中的语音片段）直接依赖原始数据的“裸格式”，易造成内存冗余（如多个解析单元重复加载同一张图片）；
- 原始数据与解析结果耦合，导致未解析数据无法纳入AGI系统的结构化流转（如仅存储原始图片却无元数据描述）。

AGI通用结构化数据的核心目标是建立“**原始媒体结构化→解析结果关联化→逻辑与数据分离化**”的完整体系：
1. 为每种原始媒体（图像、音频、视频等）单独定义结构化载体，支持多数据格式，自带唯一标识（uid）；
2. 解析结果通过弱引用（ObjUID）关联原始媒体，避免重复加载，降低内存占用；
3. 用`dataclass`纯定义数据字段，业务逻辑（如格式转换、缓存管理）独立存放，确保体系可维护、可扩展。


## 二、核心设计原则：构建分层解耦的结构化体系
遵循“四层解耦”原则，确保原始媒体、基础组件、解析结果、业务逻辑各自独立，同时相互协同：

| 设计原则 | 核心逻辑 | 实现方式 |
|----------|----------|----------|
| 原始与解析分离 | 原始媒体单独结构化，解析结果不存储原始数据，仅通过引用关联 | 原始媒体类（如RawImage）管理原始数据+uid；解析类（如ImageUnit）通过ObjUID引用原始媒体 |
| 数据与逻辑分离 | `dataclass`仅定义字段，业务逻辑（格式转换、缓存）独立存放 | 所有数据类（RawImage、ImageUnit等）用`@dataclass`纯定义字段；逻辑放在`logic/`目录下 |
| 多格式适配 | 原始媒体类原生支持多种数据格式，无需额外转换层 | RawImage支持np.ndarray、PIL.Image、base64；RawAudio支持np.ndarray、wav字节流 |
| 增量标识 | 解析结果的uid基于原始媒体uid生成增量后缀，确保关联可追溯 | 原始媒体uid：`img_20241001_abc123`；解析单元uid：`img_20241001_abc123_unit_001` |


## 三、目录结构：物理分层支撑逻辑解耦
通过目录结构强制区分“原始媒体”“基础组件”“解析结果”“业务逻辑”，确保每个模块职责清晰，新增媒体类型时无需重构现有结构：

```
agi_data/                  # 根包：对外暴露核心接口，隐藏内部实现
├── __init__.py
│
# -------------------------- 1. 基础组件：跨模态通用的结构化“原子” --------------------------
├── common/                # 所有模块共用的基础数据结构（纯dataclass）
│   ├── __init__.py        # 导出基础组件
│   ├── obj_ref.py         # 弱引用标识：ObjUID（关联原始媒体/解析结果的唯一锚点）
│   ├── spatial.py         # 空间信息：BBox（图像/视频的2D区域）
│   ├── temporal.py        # 时间信息：TimeRange（音频/视频的时间区间）
│   ├── text.py            # 文本信息：TextSpan（文本片段的索引与内容）
│   └── storage.py         # 存储信息：StorageInfo（本地路径/云端URL/base64标识）
│
# -------------------------- 2. 原始媒体：每种媒体单独定义的结构化“源头” --------------------------
├── data/
│   ├── __init__.py
│   │
│   ├── raw/               # 原始媒体目录：每种原始媒体单独建文件
│   │   ├── __init__.py    # 导出所有原始媒体类
│   │   ├── image_raw.py   # 图像原始数据：RawImage（支持np/PIL/base64）
│   │   ├── audio_raw.py   # 音频原始数据：RawAudio（支持np/wav/base64）
│   │   ├── video_raw.py   # 视频原始数据：RawVideo（支持帧序列/文件路径）
│   │   └── text_raw.py    # 文本原始数据：RawText（支持纯文本/文件路径）
│   │
│   ├── parsed/            # 解析结果目录：与原始媒体一一对应
│   │   ├── __init__.py    # 导出所有解析结果类
│   │   ├── image_parsed.py# 图像解析结果：ImageUnit（单区域）、ImageResult（多区域聚合）
│   │   ├── audio_parsed.py# 音频解析结果：AudioUnit、AudioResult
│   │   ├── video_parsed.py# 视频解析结果：VideoUnit、VideoResult
│   │   └── text_parsed.py # 文本解析结果：TextUnit、TextResult
│
# -------------------------- 3. 业务逻辑：与dataclass完全分离的“工具层” --------------------------
├── logic/                 # 所有业务逻辑（无dataclass定义，仅含函数/工具类）
│   ├── __init__.py
│   ├── ref_manager.py     # 弱引用管理：ObjUID的缓存、对象获取（关联原始媒体）
│   ├── image_logic.py     # 图像逻辑：RawImage的格式转换（np→PIL→base64）、裁剪
│   ├── audio_logic.py     # 音频逻辑：RawAudio的格式转换、片段提取
│   └── serialization.py   # 通用序列化：所有数据类的to_dict/from_dict（含原始媒体/解析结果）
│
# -------------------------- 4. 类型与常量：跨模块复用的“基础定义” --------------------------
└── types.py               # 类型别名（如NDArray= np.ndarray）、常量（如媒体格式枚举）
```


## 四、核心数据结构：纯dataclass定义（无业务逻辑）
所有数据类均用`@dataclass`定义，仅包含“字段描述”和“基础校验”，不涉及任何业务逻辑（如格式转换、缓存）。


### 4.1 基础组件（common/）：跨模态通用的“原子结构”
#### 4.1.1 obj_ref.py：弱引用标识（ObjUID）
作为原始媒体与解析结果的“关联桥梁”，仅存储目标对象的uid，不持有强引用：
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ObjUID:
    """
    弱引用唯一标识：关联原始媒体或解析结果，避免强引用导致的内存冗余
    字段说明：
    - target_uid: 目标对象的uid（如RawImage的uid、ImageResult的uid）
    - target_type: 目标对象类型（如"raw_image"、"parsed_image_result"，用于类型校验）
    """
    target_uid: str
    target_type: str

    def __post_init__(self):
        # 基础校验：无业务逻辑
        if not (self.target_uid and self.target_type):
            raise ValueError("target_uid和target_type不能为空")
        if self.target_type not in ["raw_image", "raw_audio", "raw_video", "raw_text",
                                    "parsed_image_unit", "parsed_image_result",
                                    "parsed_audio_unit", "parsed_audio_result"]:
            raise ValueError(f"不支持的target_type：{self.target_type}")
```


#### 4.1.2 其他基础组件（示例）
```python
# spatial.py：BBox（2D空间边界框）
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


# storage.py：StorageInfo（存储信息）
from dataclasses import dataclass
from typing import Literal, Optional
from agi_data.types import Timestamp  # 类型别名：Timestamp = int

@dataclass
class StorageInfo:
    """
    存储信息：描述数据的持久化位置（本地/云端/base64）
    字段说明：
    - storage_type: 存储类型
    - path: 本地路径/云端URL（storage_type为base64时，path存储base64字符串）
    - expire_time: 过期时间戳（0表示永久）
    """
    storage_type: Literal["local", "cloud", "base64"]
    path: str
    expire_time: Timestamp = 0
    extra: Optional[dict] = None  # 额外存储配置（如云端AK/SK）
```


### 4.2 原始媒体（data/raw/）：每种媒体单独定义的“源头载体”
每种原始媒体类均支持多数据格式，自带uid，可独立存在（无需关联解析结果）。

#### 4.2.1 image_raw.py：图像原始数据（RawImage）
支持np.ndarray、PIL.Image、base64三种核心格式，通过`data_format`标识当前格式：
```python
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Any
from agi_data.types import NDArray, PILImage  # 类型别名：PILImage = PIL.Image.Image
from agi_data.common import StorageInfo

@dataclass
class RawImage:
    """
    图像原始数据：结构化管理未解析的图像，支持多格式
    字段说明：
    - uid: 唯一标识（自动生成，格式：img_日期_8位uuid，如img_20241001_abc12345）
    - data_format: 当前数据格式（np.ndarray/PIL.Image/base64）
    - data: 核心数据（对应data_format的具体值）
    - width/height: 图像尺寸（自动从data提取，无需手动传入）
    - storage: 存储信息（可选，如本地路径、云端URL）
    - metadata: 扩展元数据（如拍摄时间、设备型号、分辨率）
    """
    uid: Optional[str] = None
    data_format: Literal["np.ndarray", "PIL.Image", "base64"]
    data: Union[NDArray, PILImage, str]  # str对应base64字符串
    width: Optional[int] = None
    height: Optional[int] = None
    storage: Optional[StorageInfo] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # 基础校验+自动提取尺寸（无业务逻辑，仅数据处理）
        if not self.uid:
            # 自动生成uid（原始媒体专用格式，便于追溯）
            from agi_data.logic.id_generator import generate_raw_uid  # 仅导入，无逻辑实现
            self.uid = generate_raw_uid(media_type="image")
        # 从data自动提取width/height（避免手动传入错误）
        if self.data_format == "np.ndarray" and self.data.ndim == 3:
            self.height, self.width = self.data.shape[:2]
        elif self.data_format == "PIL.Image":
            self.width, self.height = self.data.size
        elif self.data_format == "base64":
            # 仅做格式校验，不解析base64（解析逻辑放在logic/image_logic.py）
            if not self.data.startswith("data:image/"):
                raise ValueError("base64格式无效：需带data:image/前缀")
        if not (self.width and self.height):
            raise ValueError("无法提取图像尺寸，请检查data格式")
```


#### 4.2.2 audio_raw.py：音频原始数据（RawAudio）
支持np.ndarray（音频波形）、wav字节流、base64三种格式，关联时间维度信息：
```python
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Any
from agi_data.types import NDArray, WavBytes  # 类型别名：WavBytes = bytes
from agi_data.common import StorageInfo

@dataclass
class RawAudio:
    """
    音频原始数据：结构化管理未解析的音频
    字段说明：
    - uid: 唯一标识（格式：audio_日期_8位uuid，如audio_20241001_def67890）
    - data_format: 数据格式（np.ndarray/wav_bytes/base64）
    - data: 核心数据（np.ndarray为波形，wav_bytes为wav文件字节流，str为base64）
    - sample_rate: 采样率（Hz，如16000）
    - duration: 音频时长（秒，自动提取）
    - storage: 存储信息（可选）
    - metadata: 扩展元数据（如录制设备、声道数）
    """
    uid: Optional[str] = None
    data_format: Literal["np.ndarray", "wav_bytes", "base64"]
    data: Union[NDArray, WavBytes, str]
    sample_rate: int  # 音频核心参数，必须传入
    duration: Optional[float] = None
    storage: Optional[StorageInfo] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.uid:
            from agi_data.logic.id_generator import generate_raw_uid
            self.uid = generate_raw_uid(media_type="audio")
        # 基础校验：采样率范围
        if self.sample_rate not in [8000, 16000, 44100, 48000]:
            raise ValueError("不支持的采样率：仅支持8000/16000/44100/48000 Hz")
        # 自动提取时长（无业务逻辑，仅基础计算）
        if self.data_format == "np.ndarray":
            self.duration = self.data.shape[0] / self.sample_rate
        elif self.data_format == "wav_bytes":
            # 仅标记需解析，具体解析逻辑放在logic/audio_logic.py
            self.duration = None  # 占位，由逻辑层填充
```


#### 4.2.3 其他原始媒体类（示例）
```python
# video_raw.py：RawVideo（视频原始数据）
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Any
from agi_data.types import NDArrayList, VideoPath  # NDArrayList=List[np.ndarray]（帧序列）
from agi_data.common import StorageInfo

@dataclass
class RawVideo:
    uid: Optional[str] = None
    data_format: Literal["frame_sequence", "video_path", "base64"]
    data: Union[NDArrayList, VideoPath, str]  # VideoPath为本地/云端视频路径
    fps: float  # 帧率
    duration: Optional[float] = None  # 时长（秒）
    width: Optional[int] = None
    height: Optional[int] = None
    storage: Optional[StorageInfo] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.uid:
            from agi_data.logic.id_generator import generate_raw_uid
            self.uid = generate_raw_uid(media_type="video")


# text_raw.py：RawText（文本原始数据）
from dataclasses import dataclass, field
from typing import Optional, Union, Dict, Any
from agi_data.common import StorageInfo

@dataclass
class RawText:
    uid: Optional[str] = None
    data_format: Literal["plain_text", "text_file", "base64"]
    data: Union[str, str, str]  # 分别对应纯文本、文件路径、base64
    length: Optional[int] = None  # 字符长度（自动提取）
    storage: Optional[StorageInfo] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.uid:
            from agi_data.logic.id_generator import generate_raw_uid
            self.uid = generate_raw_uid(media_type="text")
        # 自动提取字符长度
        if self.data_format == "plain_text":
            self.length = len(self.data)
```


### 4.3 解析结果（data/parsed/）：关联原始媒体的“增量结构化”
解析结果不存储原始数据，仅通过`ObjUID`关联对应的原始媒体，uid采用“原始媒体uid+增量后缀”格式，确保可追溯。

#### 4.3.1 image_parsed.py：图像解析结果
```python
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Union
from agi_data.types import NDArray
from agi_data.common import ObjUID, BBox, StorageInfo
from agi_data.data.raw.image_raw import RawImage  # 仅关联类型，不依赖实例

@dataclass
class ImageUnit:
    """
    图像解析单元：描述图像中的一个语义区域（如一个物体、一段文字）
    字段说明：
    - uid: 增量标识（格式：RawImage.uid + _unit_001，如img_20241001_abc12345_unit_001）
    - image_ref: 关联的RawImage（弱引用，target_type="raw_image"）
    - bbox: 区域边界框（必选，对应RawImage中的位置）
    - mask: 区域掩码（可选，描述不规则区域，np.ndarray）
    - type: 区域类型（如"face"、"button"、"text_line"）
    - text: 文本内容（如OCR结果，可选）
    - score: 置信度（如目标检测分数，0-1，可选）
    - storage: 裁剪图存储（可选，如BBox区域的裁剪图路径）
    - metadata: 扩展元数据（如检测模型版本、裁剪图尺寸）
    """
    uid: Optional[str] = None
    image_ref: ObjUID  # 必须关联RawImage的ObjUID
    bbox: BBox
    mask: Optional[NDArray] = None
    type: Optional[str] = None
    text: Optional[str] = None
    score: Optional[float] = None
    storage: Optional[StorageInfo] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # 校验image_ref类型
        if self.image_ref.target_type != "raw_image":
            raise ValueError("image_ref必须关联raw_image类型")
        # 自动生成增量uid（依赖RawImage的uid）
        if not self.uid:
            from agi_data.logic.id_generator import generate_parsed_unit_uid
            self.uid = generate_parsed_unit_uid(raw_uid=self.image_ref.target_uid, media_type="image")


@dataclass
class ImageResult:
    """
    图像解析结果：聚合多个ImageUnit，对应一次完整的图像解析
    字段说明：
    - uid: 唯一标识（格式：parsed_img_日期_8位uuid，如parsed_img_20241001_ghi78901）
    - image_ref: 关联的RawImage（弱引用）
    - units: 解析单元列表（所有Unit均关联同一RawImage）
    - summary_text: 解析摘要（如"图中包含2个人脸、1个按钮"，可选）
    - visualized_image: 可视化结果存储（如叠加BBox的图像路径，可选）
    - storage: 解析结果整体存储（如JSON文件路径，可选）
    - metadata: 扩展元数据（如解析时间、使用的模型组合）
    """
    uid: Optional[str] = None
    image_ref: ObjUID  # 关联RawImage
    units: List[ImageUnit] = field(default_factory=list)
    summary_text: Optional[str] = None
    visualized_image: Optional[StorageInfo] = None  # 仅存储路径，不存图像数据
    storage: Optional[StorageInfo] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.image_ref.target_type != "raw_image":
            raise ValueError("image_ref必须关联raw_image类型")
        # 校验所有Unit的image_ref一致
        for unit in self.units:
            if unit.image_ref.target_uid != self.image_ref.target_uid:
                raise ValueError(f"Unit {unit.uid} 的image_ref与Result不匹配")
        if not self.uid:
            from agi_data.logic.id_generator import generate_parsed_result_uid
            self.uid = generate_parsed_result_uid(media_type="image")
```


#### 4.3.2 其他解析结果类（示例）
```python
# audio_parsed.py：AudioUnit（音频解析单元）
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from agi_data.common import ObjUID, TimeRange, StorageInfo

@dataclass
class AudioUnit:
    uid: Optional[str] = None
    audio_ref: ObjUID  # 关联RawAudio（target_type="raw_audio"）
    time_range: TimeRange  # 音频片段的时间区间
    type: Optional[str] = None  # 类型（如"speech"、"music"、"noise"）
    asr_text: Optional[str] = None  # 语音转文字结果
    score: Optional[float] = None
    storage: Optional[StorageInfo] = None  # 片段存储路径
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.audio_ref.target_type != "raw_audio":
            raise ValueError("audio_ref必须关联raw_audio类型")
        if not self.uid:
            from agi_data.logic.id_generator import generate_parsed_unit_uid
            self.uid = generate_parsed_unit_uid(raw_uid=self.audio_ref.target_uid, media_type="audio")
```


## 五、数据与逻辑分离的实现：以原始媒体为核心
所有业务逻辑（格式转换、弱引用管理、序列化）均放在`logic/`目录下，不侵入`dataclass`定义，以“RawImage的格式转换”和“弱引用管理”为例说明：


### 5.1 原始媒体的格式转换（logic/image_logic.py）
RawImage支持多格式，但格式转换逻辑独立存放，避免污染`dataclass`：
```python
# logic/image_logic.py
from typing import Union, Optional
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from agi_data.data.raw.image_raw import RawImage
from agi_data.types import NDArray, PILImage

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
```


### 5.2 原始媒体的弱引用管理（logic/ref_manager.py）
通过全局弱引用缓存管理RawImage/RawAudio，解析结果（如ImageUnit）通过ObjUID获取原始媒体，避免重复加载：
```python
# logic/ref_manager.py
import weakref
from typing import Dict, Any, Optional
from agi_data.common import ObjUID
from agi_data.data.raw.image_raw import RawImage
from agi_data.data.raw.audio_raw import RawAudio

# 全局弱引用缓存：key=uid，value=弱引用对象（RawImage/RawAudio等）
_RAW_MEDIA_CACHE: Dict[str, weakref.ref[Any]] = {}

def register_raw_media(raw_media: Union[RawImage, RawAudio]):
    """
    注册原始媒体到弱引用缓存：仅存储弱引用，不阻碍垃圾回收
    输入：RawImage/RawAudio实例
    """
    if not hasattr(raw_media, "uid"):
        raise ValueError("原始媒体必须包含uid字段")
    _RAW_MEDIA_CACHE[raw_media.uid] = weakref.ref(raw_media)

def get_raw_media(obj_ref: ObjUID) -> Optional[Union[RawImage, RawAudio]]:
    """
    通过ObjUID获取原始媒体：若媒体已被回收，返回None
    输入：关联原始媒体的ObjUID
    输出：RawImage/RawAudio实例（或None）
    """
    if obj_ref.target_type not in ["raw_image", "raw_audio", "raw_video", "raw_text"]:
        raise ValueError(f"不支持的target_type：{obj_ref.target_type}")
    # 从缓存获取弱引用并解引用
    ref = _RAW_MEDIA_CACHE.get(obj_ref.target_uid)
    return ref() if ref else None

def unregister_raw_media(raw_media_uid: str):
    """手动移除原始媒体缓存（如主动清理过期数据）"""
    if raw_media_uid in _RAW_MEDIA_CACHE:
        del _RAW_MEDIA_CACHE[raw_media_uid]
```


## 六、总结：构建AGI数据的“结构化基石”
本白皮书定义的AGI通用结构化数据体系，核心价值在于：
1. **原始媒体结构化**：为每种媒体单独定义`dataclass`，支持多格式、自带uid，解决未解析数据的管理混乱；
2. **解析结果关联化**：解析单元通过ObjUID弱引用原始媒体，避免内存冗余，增量uid确保可追溯；
3. **逻辑与数据分离化**：`dataclass`纯定义字段，业务逻辑独立存放，新增媒体类型或迭代逻辑时无需重构核心结构。

后续落地可按以下步骤推进：
1. 实现`common/`基础组件（优先ObjUID、BBox、StorageInfo）；
2. 实现`data/raw/`原始媒体类（优先RawImage、RawAudio），配套`logic/`下的格式转换与缓存逻辑；
3. 实现`data/parsed/`解析结果类，验证“原始媒体→解析结果”的弱引用关联；
4. 扩展到视频、文本等其他媒体类型，复用基础组件与逻辑框架。

这套体系可作为AGI系统的“数据基石”，支撑多模态数据的统一流转、知识沉淀与高效推理。