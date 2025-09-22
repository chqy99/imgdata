# logic/ref_manager.py

import weakref
from typing import Dict, Any, Optional, Union
from agi_data.common.obj_ref import ObjUID
from agi_data.data.raw.image_raw import RawImage

_RAW_MEDIA_CACHE: Dict[str, weakref.ref[Any]] = {}

def register_raw_media(raw_media: RawImage):
    if not hasattr(raw_media, "uid"):
        raise ValueError("原始媒体必须包含uid字段")
    _RAW_MEDIA_CACHE[raw_media.uid] = weakref.ref(raw_media)

def get_raw_media(obj_ref: ObjUID) -> Optional[RawImage]:
    if obj_ref.target_type != "raw_image":
        raise ValueError(f"不支持的target_type：{obj_ref.target_type}")
    ref = _RAW_MEDIA_CACHE.get(obj_ref.target_uid)
    return ref() if ref else None

def unregister_raw_media(raw_media_uid: str):
    if raw_media_uid in _RAW_MEDIA_CACHE:
        del _RAW_MEDIA_CACHE[raw_media_uid]