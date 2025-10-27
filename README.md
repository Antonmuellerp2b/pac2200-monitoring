# PAC2200 Monitoring

This project is a monitoring tool for the PAC2200 device. It periodically fetches measurement data from the PAC2200 and writes it to an InfluxDB time-series database for further analysis and visualization (e.g., with Grafana).

---

## Features

- Reads configuration (URLs, tokens, intervals) from environment variables (`.env` file)
- Defines several endpoints (e.g., INST, AVG1, COUNTER), each with its own polling interval
- Fetches JSON data from the PAC2200, extracts relevant measurement fields (voltages, currents, power, energy counters, etc.), and timestamps
- Formats the extracted data in the InfluxDB line protocol and sends it to the InfluxDB database
- Runs in an infinite loop, polling each endpoint at its defined interval
- Logs errors during data fetching or writing, but continues running
- All scripts (Python, Bash, PowerShell) are refactored for readability, robustness, and maintainability

---

## Typical Use Case

Automated collection and storage of measurement data from a PAC2200 device into a time-series database for later analysis and visualization.

---

## ⚡️ BEFORE STARTING FOR THE FIRST TIME

- Rename default.env to .env (Will be ignored by git afterwards due to .gitignore)
- For e-mail alerts, set GF_SMTP e-mail + password in .env file and set GF_SMTP_ENABLED=true
- Set ALERT_EMAIL_RECIPIENT
- Set SITE_ID (mandatory for cloud usage and to determine which site the e-mail alert is being fired from)
- Set METER_URL to your local electric meter, e.g. PAC2200
- Change all other login credentials in .env

## ▶️ Starting the project

```bash
# To start in Windows Powershell:
powershell -ExecutionPolicy Bypass -File .\windows_up.ps1 -d

# To start in Mac:
./mac_up.sh -d

# To start in Linux:
./linux_up.sh -d
```

## After starting up the project, open Grafana in browser

```bash
# adress for default port (this is set in .env)
localhost:4300
```


## ⏹️ Stopping the project

```bash
# To stop docker just run:
docker-compose down
# or 
docker compose down
```

## To handle problems pulling updates from the git

sudo chown -R $USER:$USER ~/pac2200-monitoring
rm default.env
git pull