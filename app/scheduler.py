# scheduler.py  

from config import ENDPOINTS
import time
import logging
import requests
from config import POLL_INTERVAL_SECONDS
from pac2200_client import extract_fields
from state import last_run

def polling_loop() -> None:
    """
    Main polling loop for periodic data collection.
    Periodically fetches data from each endpoint according to its interval,
    writes results to InfluxDB, and handles errors and graceful shutdown.
    """
    from influx_writer import write_to_influx
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



