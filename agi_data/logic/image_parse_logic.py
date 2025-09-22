import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image
import datetime
import uuid

def generate_image_uid(suffix: str = None) -> str:
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    uid = uuid.uuid4().hex[:8]
    parts = ["img", date_str, uid]
    if suffix:
        parts.append(suffix)
    return "_".join(parts)

def bbox_crop(image: np.ndarray, bbox) -> np.ndarray:
    x1, y1, x2, y2 = map(int, [bbox.x1, bbox.y1, bbox.x2, bbox.y2])
    return image[y1:y2, x1:x2]

def bbox_mask_crop(image: np.ndarray, mask: np.ndarray, bbox) -> np.ndarray:
    x1, y1, x2, y2 = map(int, [bbox.x1, bbox.y1, bbox.x2, bbox.y2])
    cropped_img = image[y1:y2, x1:x2]
    cropped_mask = mask[y1:y2, x1:x2].astype(np.uint8)
    return cv2.bitwise_and(cropped_img, cropped_img, mask=cropped_mask)

def mask_to_bbox(mask: np.ndarray):
    rows = np.where(np.any(mask, axis=1))[0]
    cols = np.where(np.any(mask, axis=0))[0]
    if len(rows) == 0 or len(cols) == 0:
        return None
    return dict(x1=float(cols[0]), y1=float(rows[0]), x2=float(cols[-1]), y2=float(rows[-1]))

# ...可继续迁移 enrich_text, enrich_label, to_dict, from_dict 等工具函数...
