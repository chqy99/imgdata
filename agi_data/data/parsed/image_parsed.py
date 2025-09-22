from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from agi_data.common.obj_ref import ObjUID
from agi_data.common.spatial import BBox
from agi_data.common.storage import StorageInfo

@dataclass
class ImageUnit:
    uid: Optional[str] = None
    image_ref: ObjUID
    bbox: BBox
    mask: Optional[Any] = None
    type: Optional[str] = None
    text: Optional[str] = None
    score: Optional[float] = None
    storage: Optional[StorageInfo] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ImageResult:
    uid: Optional[str] = None
    image_ref: ObjUID
    units: List[ImageUnit] = field(default_factory=list)
    summary_text: Optional[str] = None
    visualized_image: Optional[StorageInfo] = None
    storage: Optional[StorageInfo] = None
    metadata: Dict[str, Any] = field(default_factory=dict)