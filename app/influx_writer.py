# influx_writer.py

import logging
import time
from typing import Any, Dict, Optional
import requests
from config import (INFLUX_BUCKET, INFLUX_ORG, INFLUX_TOKEN, INFLUX_URL, ENDPOINTS)
from state import last_run
from pac2200_client import extract_fields

def write_multiple_to_influx(measurements: list[tuple[str, dict, int]]) -> None:
    """
    Write multiple measurements to InfluxDB in a single request.
    measurements: List of (source, field_data, ts)
    """
    lines = []
    ingest_time = int(time.time())
    for source, field_data, ts in measurements:
        tag = f"source={source}"
        all_fields = field_data.copy()
        all_fields["ingest_time"] = ingest_time
        fields = ",".join(f"{k}={v}" for k, v in all_fields.items())
        line = f"pac2200-monitoring,{tag} {fields} {ts or ingest_time}"
        lines.append(line)
    data = "\n".join(lines)
    try:
        response = requests.post(
            f"{INFLUX_URL}/api/v2/write?bucket={INFLUX_BUCKET}&org={INFLUX_ORG}&precision=s",
            headers={
                "Authorization": f"Token {INFLUX_TOKEN}",
                "Content-Type": "text/plain"
            },
            data=data,
            timeout=10
        )
        logging.info(f"InfluxDB batch write status: {response.status_code} – {len(lines)} lines")
    except Exception as exc:
        logging.error(f"Error writing batch to InfluxDB: {exc}")


def initial_fetch_all_sources() -> None:
    """
    Perform initial one-time fetch for all sources at startup.
    Fetches data from all endpoints and writes to InfluxDB.
    Updates last_run timestamps to avoid immediate re-polling.
    """
    measurements = []
    for source, info in ENDPOINTS.items():
        try:
            logging.info(f"[{source}] Initial fetch from {info['url']}")
            response = requests.get(info["url"], timeout=10)
            response.raise_for_status()
            json_data = response.json()
            logging.info(f"[{source}] Data fetched successfully (size: {len(response.content)} bytes)")

            field_data, ts = extract_fields(source, json_data)

            if field_data:
                logging.info(f"[{source}] Extracted {len(field_data)} fields, added to initial batch")
                measurements.append((source, field_data, ts))
            else:
                logging.warning(f"[{source}] No matching fields found in data")

        except Exception as exc:
            logging.error(f"[{source}] Error during initial fetch or processing: {exc}")
        finally:
            # Also set the timestamp here, so the next poll does not happen immediately
            last_run[source] = time.time()
    if measurements:
        write_multiple_to_influx(measurements)
        logging.info(f"Initial batch write complete: {len(measurements)} sources written.")
