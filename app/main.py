
import os
import logging
import time
import requests
from datetime import datetime
from typing import Tuple, Dict, Any, Optional

# --- Read and check environment variables ---
def parse_poll_interval(raw: Any) -> int:
    """Parse and validate the polling interval from environment variable."""
    if isinstance(raw, str) and raw.strip() == "":
        raw = 5
    try:
        interval = int(raw)
        if interval <= 0:
            raise ValueError
    except (ValueError, TypeError):
        logging.error("POLL_INTERVAL_SECONDS must be a positive integer.")
        exit(1)
    return interval

def load_env_vars() -> Tuple[str, str, str, str, int, str]:
    """Load and validate required environment variables."""
    required_vars = [
        "INFLUX_URL",
        "INFLUX_TOKEN",
        "INFLUX_BUCKET",
        "INFLUX_ORG",
        "PAC2200_URL"
    ]
    missing = [var for var in required_vars if var not in os.environ]
    if missing:
        logging.error(f"Missing required environment variables: {', '.join(missing)}")
        exit(1)

    influx_url = os.environ["INFLUX_URL"]
    influx_token = os.environ["INFLUX_TOKEN"]
    influx_bucket = os.environ["INFLUX_BUCKET"]
    influx_org = os.environ["INFLUX_ORG"]
    pac2200_url = os.environ["PAC2200_URL"]

    poll_interval_raw = os.environ.get("POLL_INTERVAL_SECONDS", 5)
    poll_interval_seconds = parse_poll_interval(poll_interval_raw)

    return influx_url, influx_token, influx_bucket, influx_org, poll_interval_seconds, pac2200_url


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)

# --- Configuration section ---
# List of fields to extract from the PAC2200
FIELDS = [
    # Voltages
    "V_L1", "V_L2", "V_L3",
    "V_L12", "V_L23", "V_L31",
    # Currents
    "I_L1", "I_L2", "I_L3",
    # Active power
    "P_L1", "P_L2", "P_L3", "P_SUM",
    # Apparent power
    "VA_L1", "VA_L2", "VA_L3", "VA_SUM",
    # Reactive power
    "VARQ1_L1", "VARQ1_L2", "VARQ1_L3", "VARQ1_SUM",
    # Power factor
    "PF_L1", "PF_L2", "PF_L3", "PF_SUM",
    # Frequency
    "FREQ"
]
# List of counter fields
COUNTER_FIELDS = [
    "ACT_ENERGY_IMPORT_T1_L1",
    "ACT_ENERGY_IMPORT_T1_L2",
    "ACT_ENERGY_IMPORT_T1_L3",
    "ACT_ENERGY_IMPORT_T1_TOTAL"
]

INFLUX_URL, INFLUX_TOKEN, INFLUX_BUCKET, INFLUX_ORG, POLL_INTERVAL_SECONDS, PAC2200_URL = load_env_vars()
# --- Query intervals in seconds ---
ENDPOINTS = {
    "INST": {"url": f"{PAC2200_URL}INST", "interval": 5},
    "AVG1": {"url": f"{PAC2200_URL}AVG1", "interval": 10},
    "AVG2": {"url": f"{PAC2200_URL}AVG2", "interval": 900},
    "COUNTER": {"url": f"{PAC2200_URL}COUNTER", "interval": 5},
    "EXTREME": {"url": f"{PAC2200_URL}EXTREME", "interval": 900}
}

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

    # Extract fields
    field_data = {}
    for key in FIELDS + COUNTER_FIELDS:
        if key in values and isinstance(values[key], dict) and "value" in values[key]:
            field_data[key] = values[key]["value"]
    ts = parse_ts_string(ts_str) if ts_str else None
    return field_data, ts


# Write values to InfluxDB
def write_to_influx(source: str, field_data: Dict[str, Any], ts: Optional[int] = None) -> None:
    """
    Write field data to InfluxDB using line protocol.
    Args:
        source (str): The endpoint/source name.
        field_data (dict): The field data to write.
        ts (int, optional): The timestamp to use. If None, current time is used.
    """
    ingest_time = int(time.time())
    if not ts:
        ts = ingest_time

    tag = f"source={source}"
    all_fields = field_data.copy()
    all_fields["ingest_time"] = ingest_time
    fields = ",".join(f"{k}={v}" for k, v in all_fields.items())
    line = f"pac2200-monitoring,{tag} {fields} {ts}"

    try:
        response = requests.post(
            f"{INFLUX_URL}/api/v2/write?bucket={INFLUX_BUCKET}&org={INFLUX_ORG}&precision=s",
            headers={
                "Authorization": f"Token {INFLUX_TOKEN}",
                "Content-Type": "text/plain"
            },
            data=line,
            timeout=10
        )
        logging.info(f"[{source}] InfluxDB write status: {response.status_code} – {line}")
    except Exception as exc:
        logging.error(f"[{source}] Error writing to InfluxDB: {exc}")


# Store last query time for each source
last_run = {source: 0 for source in ENDPOINTS}



def initial_fetch_all_sources() -> None:
    """
    Perform initial one-time fetch for all sources at startup.
    Fetches data from all endpoints and writes to InfluxDB.
    Updates last_run timestamps to avoid immediate re-polling.
    """
    for source, info in ENDPOINTS.items():
        try:
            logging.info(f"[{source}] Initial fetch from {info['url']}")
            response = requests.get(info["url"], timeout=10)
            response.raise_for_status()
            json_data = response.json()
            logging.info(f"[{source}] Data fetched successfully (size: {len(response.content)} bytes)")

            field_data, ts = extract_fields(source, json_data)

            if field_data:
                logging.info(f"[{source}] Extracted {len(field_data)} fields, writing to InfluxDB")
                write_to_influx(source, field_data, ts=ts)
                logging.info(f"[{source}] Write complete")
            else:
                logging.warning(f"[{source}] No matching fields found in data")

        except Exception as exc:
            logging.error(f"[{source}] Error during initial fetch or processing: {exc}")
        finally:
            # Also set the timestamp here, so the next poll does not happen immediately
            last_run[source] = time.time()

def main() -> None:
    """
    Main entry point for PAC2200 monitoring script.
    Performs initial data fetch and starts the polling loop.
    """
    initial_fetch_all_sources()
    polling_loop()


def polling_loop() -> None:
    """
    Main polling loop for periodic data collection.
    Periodically fetches data from each endpoint according to its interval,
    writes results to InfluxDB, and handles errors and graceful shutdown.
    """
    try:
        while True:
            now = time.time()
            for source, info in ENDPOINTS.items():
                interval = info["interval"]
                if now - last_run[source] >= interval:
                    logging.info(f"[{source}] Starting data fetch from {info['url']}")
                    try:
                        response = requests.get(info["url"], timeout=10)
                        response.raise_for_status()
                        json_data = response.json()
                        logging.info(f"[{source}] Data fetched successfully (size: {len(response.content)} bytes)")

                        field_data, ts = extract_fields(source, json_data)

                        if field_data:
                            logging.info(f"[{source}] Extracted {len(field_data)} fields, writing to InfluxDB")
                            write_to_influx(source, field_data, ts=ts)
                            logging.info(f"[{source}] Write complete")
                        else:
                            logging.warning(f"[{source}] No matching fields found in data")

                    except Exception as exc:
                        logging.error(f"[{source}] Error during fetch or processing: {exc}")

                    finally:
                        last_run[source] = now
                        logging.info(f"[{source}] Next fetch earliest after {interval} seconds")

            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        logging.info("Polling loop interrupted by user. Exiting cleanly.")
    except Exception as exc:
        logging.critical(f"Fatal error in polling loop: {exc}", exc_info=True)


if __name__ == "__main__":
    main()