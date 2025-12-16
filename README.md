# Banks ETL Pipeline (Python + Docker)

End-to-end ETL project: **extract → transform → load** for the "Largest Banks" dataset.
The pipeline downloads/parses source data, transforms it (incl. currency conversion), and stores the result locally (CSV + SQLite).

## What this project demonstrates
- ETL pipeline design (modular Python structure)
- Config-driven approach (`config.yaml`)
- Logging to file (`logs/app.log`)
- Local storage (CSV + SQLite)
- Dockerized execution (reproducible runs)

## Tech stack
- Python (pandas, requests/bs4 if used)
- SQLite
- Docker
- YAML config

## Project structure
<img width="380" height="607" alt="image" src="https://github.com/user-attachments/assets/4e41f896-cc3a-4980-a14c-0e807455586b" />

```
banks-etl/
├── data/
│ ├── processed/
│ │ └── largest_banks_data.csv
│ └── raw/
│ └── largest_banks.html
├── warehouse/
│ ├── gfikeep/
│ ├── Banks.db
│ └── exchange_rate.csv
├── logs/
│ └── app.log
├── src/
│ └── etl/
│ ├── init.py
│ ├── extract.py
│ ├── load.py
│ ├── main.py
│ ├── transform.py
│ └── utils.py
├── .gitignore
├── config.yaml
├── Dockerfile
└── requirements.txt
```
---

## How to run locally
```bash
# 1) create venv
python -m venv .venv
source .venv/bin/activate

# 2) install deps
pip install -r requirements.txt

# 3) run
python -m src.etl.main
```

# build
docker build -t banks-etl:latest .

# run (mount data & logs so you keep outputs)
```
docker run --rm \
  -v "$(pwd)/data:/app/data" \
  -v "$(pwd)/logs:/app/logs" \
  banks-etl:latest
```
Outputs

data/processed/Largest_banks_data.csv

data/warehouse/Banks.db

logs/app.log

Configuration

Edit config.yaml to control:

input source

output paths

currency rates file

DB path

Status

🚧 In progress:

add unit tests

add CI (GitHub Actions)

improve data validation & error handling

## Author: Bogdan Khudoidodov (https://www.linkedin.com/in/bogdan-khudoidodov/)
