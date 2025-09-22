from dataclasses import dataclass

@dataclass
class ObjUID:
    target_uid: str
    target_type: str

    def __post_init__(self):
        if not (self.target_uid and self.target_type):
            raise ValueError("target_uid和target_type不能为空")
        if self.target_type not in [
            "raw_image", "parsed_image_unit", "parsed_image_result"
        ]:
            raise ValueError(f"不支持的target_type：{self.target_type}")