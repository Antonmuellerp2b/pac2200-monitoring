# pac2200_client.py

from typing import Any, Dict, Optional, Tuple  
from datetime import datetime
from config import FIELDS, COUNTER_FIELDS

def parse_ts_string(ts_str: str) -> int:
    """Convert ISO timestamp string to Unix timestamp (seconds)."""
    dt = datetime.fromisoformat(ts_str)
    return int(dt.timestamp())

# Parse JSON data and extract values + timestamp
def extract_fields(source: str, json_data: Dict[str, Any]) -> Tuple[Dict[str, Any], Optional[int]]:
    """
    Parse JSON data from PAC2200 endpoint and extract relevant fields and timestamp.

    Args:
        source (str): The endpoint/source name (e.g., 'INST', 'AVG1').
        json_data (dict): The JSON data returned from the endpoint.

    Returns:
        tuple: (field_data: dict, ts: int or None)
    """
    values: Dict[str, Any] = {}
    ts_str: Optional[str] = None

    if source == "INST":
        values = json_data.get("INST_VALUES", {})
        ts_str = values.get("LOCAL_TIME")

    elif source in ["AVG1", "AVG2"]:
        stage_key = "STAGE1" if source == "AVG1" else "STAGE2"
        stage = json_data.get("AVERAGE_VALUES", {}).get(stage_key, {})
        values = stage
        ts_str = stage.get("TS")

    elif source == "COUNTER":
        counter_data = json_data.get("COUNTER", {})
        ts_str = counter_data.get("LOCAL_TIME")
        t1_data = counter_data.get("ACTIVE_ENERGY", {}).get("IMPORT", {}).get("T1", {})

        mapping = {
            "ACT_ENERGY_IMPORT_T1_L1": "L1",
            "ACT_ENERGY_IMPORT_T1_L2": "L2",
            "ACT_ENERGY_IMPORT_T1_L3": "L3",
            "ACT_ENERGY_IMPORT_T1_TOTAL": "total"
        }

        for field, key in mapping.items():
            val = t1_data.get(key)
            if val is not None:
                values[field] = {"value": val}

    # Extract fields
    field_data: Dict[str, Any] = {}
    for key in FIELDS + COUNTER_FIELDS:
        if key in values and isinstance(values[key], dict) and "value" in values[key]:
            field_data[key] = values[key]["value"]
    ts = parse_ts_string(ts_str) if ts_str else None
    return field_data, ts

