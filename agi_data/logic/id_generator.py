import uuid
from datetime import datetime

def generate_raw_uid(media_type: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    uid = uuid.uuid4().hex[:8]
    return f"{media_type}_{date_str}_{uid}"

def generate_parsed_unit_uid(raw_uid: str, media_type: str) -> str:
    unit_id = uuid.uuid4().hex[:3]
    return f"{raw_uid}_unit_{unit_id}"

def generate_parsed_result_uid(media_type: str) -> str:
    date_str = datetime.now().strftime("%Y%m%d")
    uid = uuid.uuid4().hex[:8]
    return f"parsed_{media_type}_{date_str}_{uid}"
