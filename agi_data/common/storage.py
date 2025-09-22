from dataclasses import dataclass
from typing import Literal, Optional

Timestamp = int  # 类型别名

@dataclass
class StorageInfo:
    storage_type: Literal["local", "cloud", "base64"]
    path: str
    expire_time: Timestamp = 0
    extra: Optional[dict] = None