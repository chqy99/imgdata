from dataclasses import dataclass, field
from typing import Optional, Callable, Literal, List, Dict, Any
import numpy as np

@dataclass
class BBox:
    x1: int
    y1: int
    x2: int
    y2: int

    def to_dict(self) -> dict:
        return {'x1': self.x1, 'y1': self.y1, 'x2': self.x2, 'y2': self.y2}

    @staticmethod
    def from_dict(data: dict) -> "BBox":
        return BBox(**data)

    def crop(self, image: np.ndarray) -> np.ndarray:
        return image[self.y1:self.y2, self.x1:self.x2]

    @classmethod
    def mask_to_bbox(cls, mask: np.ndarray) -> "BBox | None":
        rows = np.where(np.any(mask, axis=1))[0]
        cols = np.where(np.any(mask, axis=0))[0]
        if len(rows) == 0 or len(cols) == 0:
            return None
        return cls(x1=cols[0], y1=rows[0], x2=cols[-1], y2=rows[-1])


@dataclass
class ImageObject:
    id: str
    image: np.ndarray
    mask: Optional[np.ndarray] = None
    mask_image: Optional[np.ndarray] = None
    type: Literal['ocr', 'icon', 'instance', 'region'] = 'region'
    bbox: Optional[BBox] = None
    label: Optional[str] = None
    text: Optional[str] = None
    score: Optional[float] = None
    embedding: Optional[np.ndarray] = None
    source_module: Optional[str] = None
    mask_path: Optional[str] = None
    mask_image_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_ocr(cls, image, bbox, text, score, **kwargs) -> "ImageObject":
        instance = cls(
            image=image,
            type='ocr',
            bbox=bbox,
            text=text,
            score=score,
            **kwargs
        )
        return instance

    @classmethod
    def from_mask(cls, image: np.ndarray, mask: np.ndarray, **kwargs) -> "ImageObject":
        bbox = BBox.mask_to_bbox(mask)
        mask_image = image[bbox.y1: bbox.y2, bbox.x1: bbox.x2] if bbox else None
        instance = cls(
            image=image,
            mask=mask,
            bbox=bbox,
            mask_image=mask_image,
            type='instance',
            **kwargs
        )
        return instance

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.type,
            'bbox': self.bbox.to_dict() if self.bbox else None,
            'label': self.label,
            'text': self.text,
            'score': self.score,
            'embedding': self.embedding.tolist() if self.embedding is not None else None,
            'source_module': self.source_module,
            'mask_path': self.mask_path,
            'mask_image_path': self.mask_image_path,
        }

    @classmethod
    def from_dict(cls, data: dict,
                  full_image: np.ndarray,
                  load_mask: Callable[[str], np.ndarray],
                  load_mask_image: Callable[[str], np.ndarray]) -> "ImageObject":
        return cls(
            id=data['id'],
            image=full_image,
            mask=load_mask(data['mask_path']) if data.get('mask_path') else None,
            mask_image=load_mask_image(data['mask_image_path']) if data.get('mask_image_path') else None,
            type=data['type'],
            bbox=BBox.from_dict(data['bbox']) if data.get('bbox') else None,
            label=data.get('label'),
            text=data.get('text'),
            score=data.get('score'),
            embedding=np.array(data['embedding']) if data.get('embedding') else None,
            source_module=data.get('source_module'),
            mask_path=data.get('mask_path'),
            mask_image_path=data.get('mask_image_path'),
        )


@dataclass
class ImageParseResult:
    image_id: str
    full_image: np.ndarray
    full_embedding: Optional[np.ndarray] = None
    full_image_path: Optional[str] = None
    objects: List[ImageObject] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'image_id': self.image_id,
            'full_embedding': self.full_embedding.tolist() if self.full_embedding is not None else None,
            'full_image_path': self.full_image_path,
            'objects': [obj.to_dict() for obj in self.objects]
        }

    @classmethod
    def from_dict(cls, data: dict,
                  load_full_image: Callable[[str], np.ndarray],
                  load_mask: Callable[[str], np.ndarray],
                  load_mask_image: Callable[[str], np.ndarray]) -> "ImageParseResult":
        full_image = load_full_image(data['full_image_path']) if data.get('full_image_path') else None
        result = cls(
            image_id=data['image_id'],
            full_image=full_image,
            full_embedding=np.array(data['full_embedding']) if data.get('full_embedding') else None,
            full_image_path=data.get('full_image_path')
        )
        for obj_data in data.get('objects', []):
            obj = ImageObject.from_dict(obj_data, full_image, load_mask, load_mask_image)
            result.objects.append(obj)
        return result
