
import logging
from typing import Dict, Any, Tuple


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def get_env_vars() -> Dict[str, Any]:
    """Read and validate required environment variables."""
    try:
        influx_url = os.environ["INFLUX_URL"]
        influx_token = os.environ["INFLUX_TOKEN"]
        bucket = os.environ["INFLUX_BUCKET"]
        org = os.environ["INFLUX_ORG"]
        poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", 5))
        base_url = os.environ["PAC2200_URL"]
        return {
            "influx_url": influx_url,
            "influx_token": influx_token,
            "bucket": bucket,
            "org": org,
            "poll_interval_seconds": poll_interval_seconds,
            "base_url": base_url
        }
    except KeyError as e:
        logging.error(f"Environment variable missing: {e}")
        exit(1)


def get_endpoints(base_url: str) -> Dict[str, Dict[str, Any]]:
    """Return endpoint configuration."""
    return {
        "INST": {"url": f"{base_url}INST", "interval": 5},
        "AVG1": {"url": f"{base_url}AVG1", "interval": 10},
        "AVG2": {"url": f"{base_url}AVG2", "interval": 900},
        "COUNTER": {"url": f"{base_url}COUNTER", "interval": 5},
        "EXTREME": {"url": f"{base_url}EXTREME", "interval": 900}
    }


FIELDS = [
    "V_L1", "V_L2", "V_L3",
    "V_L12", "V_L23", "V_L31",
    "I_L1", "I_L2", "I_L3",
    "P_L1", "P_L2", "P_L3", "P_SUM",
    "VA_L1", "VA_L2", "VA_L3", "VA_SUM",
    "VARQ1_L1", "VARQ1_L2", "VARQ1_L3", "VARQ1_SUM",
    "PF_L1", "PF_L2", "PF_L3", "PF_SUM",
    "FREQ"
]

COUNTER_FIELDS = [
    "ACT_ENERGY_IMPORT_T1_L1",
    "ACT_ENERGY_IMPORT_T1_L2",
    "ACT_ENERGY_IMPORT_T1_L3",
    "ACT_ENERGY_IMPORT_T1_TOTAL"
]

def parse_ts_string(ts_str: str) -> int:
    """Convert ISO timestamp string to Unix timestamp (seconds)."""
    dt = datetime.fromisoformat(ts_str)
    return int(dt.timestamp())


def extract_fields(source: str, json_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Extract relevant fields and timestamp from JSON data."""
    values = {}
    ts_str = None

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

    field_data = {
        key: values[key]["value"]
        for key in FIELDS + COUNTER_FIELDS
        if key in values and isinstance(values[key], dict) and "value" in values[key]
    }
    ts = parse_ts_string(ts_str) if ts_str else None
    logging.debug(f"Extracted fields for {source}: {field_data}, ts: {ts}")
    return field_data, ts


def write_to_influx(env: Dict[str, Any], source: str, field_data: Dict[str, Any], ts: int = None) -> None:
    """Write data to InfluxDB using line protocol."""
    ingest_time = int(time.time())
    if not ts:
        ts = ingest_time
    tag = f"source={source}"
    all_fields = field_data.copy()
    all_fields["ingest_time"] = ingest_time
    fields = ",".join([f"{k}={v}" for k, v in all_fields.items()])
    line = f"pac2200-monitoring,{tag} {fields} {ts}"
    try:
        r = requests.post(
            f"{env['influx_url']}/api/v2/write?bucket={env['bucket']}&org={env['org']}&precision=s",
            headers={
                "Authorization": f"Token {env['influx_token']}",
                "Content-Type": "text/plain"
            },
            data=line,
            timeout=10
        )
        logging.info(f"[{source}] InfluxDB write status: {r.status_code} – {line}")
    except Exception as e:
        logging.error(f"[{source}] Error writing to InfluxDB: {e}")


def fetch_and_process_source(env: Dict[str, Any], source: str, info: Dict[str, Any]) -> Tuple[bool, float]:
    """Fetch data from a source, process and write to InfluxDB."""
    try:
        logging.info(f"[{source}] Fetching data from {info['url']}")
        r = requests.get(info["url"], timeout=10)
        r.raise_for_status()
        json_data = r.json()
        logging.info(f"[{source}] Data fetched successfully (size: {len(r.content)} bytes)")
        field_data, ts = extract_fields(source, json_data)
        if field_data:
            logging.info(f"[{source}] Extracted {len(field_data)} fields, writing to InfluxDB")
            write_to_influx(env, source, field_data, ts=ts)
            logging.info(f"[{source}] Write complete")
        else:
            logging.warning(f"[{source}] No matching fields found in data")
        return True, time.time()
    except Exception as e:
        logging.error(f"[{source}] Error during fetch or processing: {e}")
        return False, time.time()


def main():
    setup_logging()
    logging.info("Starting PAC2200 Monitoring")
    env = get_env_vars()
    endpoints = get_endpoints(env["base_url"])
    last_run = {source: 0 for source in endpoints}

    # Initial fetch for all sources
    for source, info in endpoints.items():
        _, last_run[source] = fetch_and_process_source(env, source, info)

    # Main polling loop
    while True:
        now = time.time()
        for source, info in endpoints.items():
            interval = info["interval"]
            if now - last_run[source] >= interval:
                _, last_run[source] = fetch_and_process_source(env, source, info)
                logging.info(f"[{source}] Next fetch earliest after {interval} seconds")
        time.sleep(env["poll_interval_seconds"])


if __name__ == "__main__":
    main()
