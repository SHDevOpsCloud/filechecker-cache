# metrics-exporter

A lightweight FastAPI-based metrics service that exposes system metrics, file integrity data, and diagnostic endpoints for automation and DevOps workflows. Designed for clarity, reliability, and predictable behavior in small-business and internal tooling environments.

---

## Features

- Prometheus‑ready `/metrics` endpoint  
- Background scanning threads  
- File integrity and mismatch reporting  
- Version drift detection  
- System metrics (CPU, memory, timestamps)  
- Config-driven behavior  
- Safe execution wrappers to prevent pipeline crashes  
- Modular design for easy extension  

---

## Why This Exists

Automation pipelines and monitoring systems often fail due to:

- Silent file changes  
- Unexpected version drift  
- Missing or replaced files  
- Lack of visibility into system metrics  
- No unified place to expose diagnostic data  

**metrics-exporter** provides a single, predictable service that exposes both system and file integrity metrics in a clean, observable format.

---

## Architecture

```
metrics-exporter/
│
├── server.py               # FastAPI app and routing
├── file_checker.py         # File classification, validation, mismatch logic
├── metrics_cache.py        # CPU, memory, timestamps, Prometheus metrics
├── system_metrics.py       # System-level metric collection
├── config_loader.py        # Config parsing and validation
├── threads.py              # Background scanning threads
└── requirements.txt
```

Each module is isolated and testable, following a simple, enterprise-style structure.

---

## Endpoints

### `/metrics`
Prometheus-formatted metrics including:
- CPU usage  
- Memory usage  
- Last scan timestamps  
- File integrity counters  

### `/filechecker`
Runs file classification and validation using the FileChecker module.

### `/mismatches`
Returns detected mismatches between expected and actual file states.

### `/versions`
Reports version drift or unexpected changes.

### `/file-report`
Full integrity report including:
- New files  
- Changed files  
- Missing files  
- Unchanged files  

### `/health`
Simple health check for monitoring systems.

---

## How It Works

1. Background threads collect system metrics and scan file structures.  
2. FileChecker classifies and validates files using rule-based logic.  
3. MetricsCache stores system and file metrics.  
4. FastAPI exposes the data through JSON and Prometheus endpoints.  
5. External systems (Prometheus, Grafana, scripts) consume the metrics.

---

## Example Usage

Start the service:

```
uvicorn server:app --host 0.0.0.0 --port 8000
```

Query metrics:

```
curl http://localhost:8000/metrics
```

Get file integrity report:

```
curl http://localhost:8000/file-report
```

---

## Typical Use Cases

- Monitoring file integrity in regulated environments  
- Detecting unexpected file changes  
- Observability for automation pipelines  
- Lightweight system metrics exporter  
- DevOps tooling for small businesses or internal teams  

---

## Future Improvements

- YAML-based configuration  
- Async scanning mode  
- Grafana dashboard templates  
- Alerting thresholds for file drift  
- Logging hooks for audit trails  

---

## License

MIT License
