# config.py
import logging
import os
from typing import Any, Tuple


def configure_logging(level: int = logging.INFO) -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=level,
        format='%(asctime)s %(levelname)s %(message)s',
    )

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

# --- Configuration section ---
# List of fields to extract from the PAC2200
FIELDS: list[str] = [
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
COUNTER_FIELDS: list[str] = [
    "ACT_ENERGY_IMPORT_T1_L1",
    "ACT_ENERGY_IMPORT_T1_L2",
    "ACT_ENERGY_IMPORT_T1_L3",
    "ACT_ENERGY_IMPORT_T1_TOTAL"
]

INFLUX_URL, INFLUX_TOKEN, INFLUX_BUCKET, INFLUX_ORG, POLL_INTERVAL_SECONDS, PAC2200_URL = load_env_vars()

# --- Query intervals in seconds ---
ENDPOINTS: dict[str, dict[str, object]] = {
    "INST": {"url": f"{PAC2200_URL}INST", "interval": 5},
    "AVG1": {"url": f"{PAC2200_URL}AVG1", "interval": 10},
    "AVG2": {"url": f"{PAC2200_URL}AVG2", "interval": 900},
    "COUNTER": {"url": f"{PAC2200_URL}COUNTER", "interval": 5}
}

