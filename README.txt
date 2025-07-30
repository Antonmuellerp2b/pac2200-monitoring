PAC2200 Monitoring
This project is a monitoring tool for the PAC2200 device. It periodically fetches measurement data from the PAC2200 and writes it to an InfluxDB time-series database for further analysis and visualization (e.g., with Grafana).

Features
- Reads configuration (URLs, tokens, intervals) from environment variables.
- Defines several endpoints (e.g., INST, AVG1, COUNTER), each with its own polling interval.
- Fetches JSON data from the PAC2200, extracts relevant measurement fields (voltages, currents, power, energy counters, etc.), and timestamps.
- Formats the extracted data in the InfluxDB line protocol and sends it to the InfluxDB database.
- Runs in an infinite loop, polling each endpoint at its defined interval.
- Logs errors during data fetching or writing, but continues running.

Typical Use Case
- Automated collection and storage of measurement data from a PAC2200 device into a time-series database for later analysis and visualization.

# BEFORE STARTING FOR THE FIRST TIME

	# Rename default.env to .env (Will be ignored by git afterwards due to .gitignore)
	# for e-mail alerts, set e-mail + password in .env file and set GF_SMTP_ENABLED=true

# to start in Windows: powershell -ExecutionPolicy Bypass -File .\up.ps1 -d
# to start in Mac: ./up.sh -d
# to start in Linux: ./linux_up.sh -d

# to stop docker just run "docker-compose down" in directory of docker-compose.yml