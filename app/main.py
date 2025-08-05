import os
import time
import requests
from datetime import datetime

print('STARTING MAIN.py') 

# Environment variables
try:
    influx_url = os.environ["INFLUX_URL"]
    influx_token = os.environ["INFLUX_TOKEN"]
    bucket = os.environ["INFLUX_BUCKET"]
    org = os.environ["INFLUX_ORG"]
    poll_interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", 5))
    base_url = os.environ["PAC2200_URL"]

    print(f"PAC2200 base URL: {base_url}")
    print(f"POLL_INTERVAL_SECONDS: {poll_interval_seconds}")
except KeyError as e:
    print(f"❌ Environment variable missing: {e}")
    exit(1)


print(f"PAC2200 base URL: {base_url}")

# Abfrageintervalle in Sekunden
ENDPOINTS = {
    "INST": {"url": f"{base_url}INST", "interval": 5},
    "AVG1": {"url": f"{base_url}AVG1", "interval": 10},
    "AVG2": {"url": f"{base_url}AVG2", "interval": 900},
    "COUNTER": {"url": f"{base_url}COUNTER", "interval": 5},
    "EXTREME": {"url": f"{base_url}EXTREME", "interval": 900}
}

FIELDS = [
    # Spannungen
    "V_L1", "V_L2", "V_L3",
    "V_L12", "V_L23", "V_L31",

    # Ströme
    "I_L1", "I_L2", "I_L3",

    # Wirkleistung
    "P_L1", "P_L2", "P_L3", "P_SUM",

    # Scheinleistung
    "VA_L1", "VA_L2", "VA_L3", "VA_SUM",

    # Blindleistung
    "VARQ1_L1", "VARQ1_L2", "VARQ1_L3", "VARQ1_SUM",

    # Leistungsfaktor
    "PF_L1", "PF_L2", "PF_L3", "PF_SUM",

    # Frequenz
    "FREQ"
]

COUNTER_FIELDS = [
    "ACT_ENERGY_IMPORT_T1_L1", 
    "ACT_ENERGY_IMPORT_T1_L2", 
    "ACT_ENERGY_IMPORT_T1_L3",
    "ACT_ENERGY_IMPORT_T1_TOTAL"
]

# Hilfsfunktion für Zeitumwandlung
def parse_ts_string(ts_str):
    dt = datetime.fromisoformat(ts_str)
    return int(dt.timestamp())

# JSON-Daten parsen & Werte + Zeitstempel extrahieren
def extract_fields(source, json_data):
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

    # Felder extrahieren
    field_data = {
        key: values[key]["value"]
        for key in FIELDS + COUNTER_FIELDS
        if key in values and isinstance(values[key], dict) and "value" in values[key]
    }

    ts = parse_ts_string(ts_str) if ts_str else None

    print("source", source, "ts_str", ts_str, "ts", ts)

    return field_data, ts

# Werte nach InfluxDB schreiben
def write_to_influx(source, field_data, ts=None):
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
            f"{influx_url}/api/v2/write?bucket={bucket}&org={org}&precision=s",
            headers={
                "Authorization": f"Token {influx_token}",
                "Content-Type": "text/plain"
            },
            data=line,
            timeout=10
        )
        print(f"[{source}] InfluxDB write status: {r.status_code} – {line}")
    except Exception as e:
        print(f"[{source}] Error writing to InfluxDB: {e}")

# Letzte Abfragezeit pro Quelle speichern
last_run = {source: 0 for source in ENDPOINTS}

# Hauptloop
while True:
    now = time.time()
    for source, info in ENDPOINTS.items():
        interval = info["interval"]
        if now - last_run[source] >= interval:
            print(f"[{source}] Starting data fetch from {info['url']}")
            try:
                r = requests.get(info["url"], timeout=10)
                r.raise_for_status()
                json_data = r.json()
                print(f"[{source}] Data fetched successfully (size: {len(r.content)} bytes)")

                field_data, ts = extract_fields(source, json_data)



                if field_data:
                    print(f"[{source}] Extracted {len(field_data)} fields, writing to InfluxDB")
                    write_to_influx(source, field_data, ts=ts)
                    print(f"[{source}] Write complete")
                else:
                    print(f"[{source}] No matching fields found in data")

            except Exception as e:
                print(f"[{source}] Error during fetch or processing: {e}")

            finally:
                last_run[source] = now
                print(f"[{source}] Next fetch earliest after {interval} seconds")

    time.sleep(poll_interval_seconds)
