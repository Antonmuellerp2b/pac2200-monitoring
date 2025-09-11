"""
PAC2200 Monitoring Script
Collects data from PAC2200 endpoints and writes to InfluxDB.
"""
from influx_writer import initial_fetch_all_sources
from scheduler import polling_loop
from config import configure_logging

def main() -> None:
    """
    Main entry point for PAC2200 monitoring script.
    Performs initial data fetch and starts the polling loop.
    """
    configure_logging()
    initial_fetch_all_sources()
    polling_loop()

if __name__ == "__main__":
    main()