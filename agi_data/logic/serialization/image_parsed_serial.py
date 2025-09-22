import numpy as np
from agi_data.logic.image_logic import np_to_base64, base64_to_np

def image_unit_to_dict(unit, image_filter=None):
    if image_filter is None:
        image_filter = ["mask"]
    d = {
        "uid": unit.uid,
        "bbox": unit.bbox.to_dict(),
        "source_module": unit.source_module,
        "score": unit.score,
        "type": unit.type,
        "text": unit.text,
        "label": unit.label,
        "metadata": unit.metadata,
    }
    if "bbox_image" in image_filter:
        d["bbox_image"] = (
            np_to_base64(unit.bbox_image)
            if getattr(unit, "bbox_image", None) is not None
            else None
        )
    if "mask_image" in image_filter:
        d["mask_image"] = (
            np_to_base64(unit.mask_image)
            if getattr(unit, "mask_image", None) is not None
            else None
        )
    if "mask" in image_filter:
        d["mask"] = (
            np_to_base64(unit.mask.astype(np.uint8))
            if getattr(unit, "mask", None) is not None
            else None
        )
    if "image" in image_filter:
        d["image"] = np_to_base64(unit.image) if getattr(unit, "image", None) is not None else None
    return d

def image_unit_from_dict(cls, data, image_filter=None):
    if image_filter is None:
        image_filter = ["mask"]
    obj = cls(
        bbox=cls.BBox.from_dict(data["bbox"]),
        source_module=data["source_module"],
        score=data.get("score"),
        type=data.get("type"),
        text=data.get("text"),
        label=data.get("label"),
        metadata=data.get("metadata", {}),
        uid=data.get("uid"),
    )
    if "bbox_image" in image_filter and data.get("bbox_image") is not None:
        obj._bbox_image = base64_to_np(data["bbox_image"])
    if "mask_image" in image_filter and data.get("mask_image") is not None:
        obj._mask_image = base64_to_np(data["mask_image"])
    if "mask" in image_filter and data.get("mask") is not None:
        obj.mask = base64_to_np(data["mask"])
    if "image" in image_filter and data.get("image") is not None:
        obj.image = base64_to_np(data["image"])
    return obj

def image_result_to_dict(result, image_filter=None, unit_image_filter=None):
    if image_filter is None:
        image_filter = ["image"]
    if unit_image_filter is None:
        unit_image_filter = ["mask"]
    d = {
        "uid": result.uid,
        "summary_text": result.summary_text,
        "metadata": result.metadata,
        "units": [image_unit_to_dict(u, image_filter=unit_image_filter) for u in result.units],
    }
    if "image" in image_filter and getattr(result, "image", None) is not None:
        d["image"] = np_to_base64(result.image)
    if "bboxs_image" in image_filter and getattr(result, "bboxs_image", None) is not None:
        d["bboxs_image"] = np_to_base64(result.bboxs_image)
    if "masks" in image_filter and getattr(result, "masks", None) is not None:
        d["masks"] = np_to_base64(result.masks)
    if "masks_image" in image_filter and getattr(result, "masks_image", None) is not None:
        d["masks_image"] = np_to_base64(result.masks_image)
    return d

def image_result_from_dict(cls, data, image_filter=None, unit_image_filter=None):
    if image_filter is None:
        image_filter = ["image"]
    if unit_image_filter is None:
        unit_image_filter = ["mask"]
    image = (
        base64_to_np(data["image"])
        if "image" in image_filter and data.get("image") is not None
        else None
    )
    obj = cls(
        image=image,
        uid=data.get("uid"),
        summary_text=data.get("summary_text"),
        metadata=data.get("metadata", {}),
        units=[
            image_unit_from_dict(cls.ImageParseUnit, u, image_filter=unit_image_filter)
            for u in data.get("units", [])
        ],
    )
    if "bboxs_image" in image_filter and data.get("bboxs_image") is not None:
        obj._bboxs_image = base64_to_np(data["bboxs_image"])
    if "masks" in image_filter and data.get("masks") is not None:
        obj._masks = base64_to_np(data["masks"])
    if "masks_image" in image_filter and data.get("masks_image") is not None:
        obj._masks_image = base64_to_np(data["masks_image"])
    return obj
