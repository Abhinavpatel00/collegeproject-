# MDAAS — Run & Configuration Guide

**MDAAS** (Malware Detection and Analysis as a Service) is a dual-service web application:

| Service | Directory | Port | Purpose |
|---------|-----------|------|---------|
| Static Analysis (VirusTotal) | `Virus_total_based/` | **5000** | Scan files, URLs, and hashes via VirusTotal API |
| ML Detection | `ML_based_detectionn/` | **5001** | Classify `.exe` / `.dll` files with a trained Random Forest model |

---

## Prerequisites

- **Python 3.10+** (3.11 or 3.12 recommended)
- **pip** and **venv**
- A free [VirusTotal API key](https://www.virustotal.com/gui/join-us) (required for static analysis on port 5000)
- The trained model file `ML_based_detectionn/ML_model/malwareclassifier-V2.pkl` (included in a full clone; required for ML detection)

---

## 1. Clone the repository

```bash
git clone https://github.com/0xfke/Malware-Detection-and-Analysis-using-Machine-Learning.git
cd Malware-Detection-and-Analysis-using-Machine-Learning
```

---

## 2. Create a virtual environment

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows
```

---

## 3. Install dependencies

```bash
pip install -r ML_based_detectionn/requirements.txt
```

This installs Flask, scikit-learn, pefile, requests, and other packages used by both services.

---

## 4. Configure VirusTotal API key

The static analysis app needs a VirusTotal API key.

### Option A — Environment variable (recommended)

```bash
export VIRUSTOTAL_API_KEY="your_virustotal_api_key_here"
```

Add the same line to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) to persist it.

### Option B — Edit the source file

Open `Virus_total_based/app.py` and replace the placeholder:

```python
API_KEY = 'your API Key'
```

with your actual key.

---

## 5. Verify the ML model (port 5001)

Ensure this file exists before starting the ML service:

```bash
ls ML_based_detectionn/ML_model/malwareclassifier-V2.pkl
```

If it is missing, train or download the model using the notebook `malware_ditaction_insa_1.ipynb` in the project root.

---

## 6. Run the applications

You need **two terminal sessions** (both with the virtual environment activated).

### Terminal 1 — Static Analysis (landing page, port 5000)

```bash
cd Virus_total_based
python app.py
```

Open: [http://127.0.0.1:5000](http://127.0.0.1:5000)

### Terminal 2 — ML Detection (port 5001)

```bash
cd ML_based_detectionn
python app.py
```

Open: [http://127.0.0.1:5001](http://127.0.0.1:5001)

---

## 7. Quick start (both services from project root)

With the venv active and `VIRUSTOTAL_API_KEY` set:

```bash
# Terminal 1
cd Virus_total_based && python app.py

# Terminal 2
cd ML_based_detectionn && python app.py
```

---

## Usage

### Static Analysis (`http://127.0.0.1:5000`)

Submit **one** of the following on the analysis form:

- **File upload** — any file type supported by VirusTotal
- **URL** — web address to scan
- **Hash** — MD5, SHA-1, or SHA-256 of a known file

Results show detection ratio, engine breakdown, and charts.

### ML Detection (`http://127.0.0.1:5001`)

Upload a Windows executable:

- `.exe`
- `.dll`

The model extracts PE header features and returns **Malware** or **Safe**.

---

## Configuration reference

| Setting | Location | Default |
|---------|----------|---------|
| VirusTotal API key | `VIRUSTOTAL_API_KEY` env var or `Virus_total_based/app.py` | `your API Key` |
| Static analysis port | `Virus_total_based/app.py` → `app.run(...)` | `5000` |
| ML detection port | `ML_based_detectionn/app.py` → `app.run(port=...)` | `5001` |
| ML upload folder | `ML_based_detectionn/uploads/` | auto-created |
| VT temp uploads | `/tmp` | system temp |

### Change ports

**Static analysis** — edit `Virus_total_based/app.py`:

```python
app.run(debug=True, threaded=True, port=5000)
```

**ML detection** — edit `ML_based_detectionn/app.py`:

```python
app.run(port=5001, debug=True)
```

After changing ports, update navigation links in the templates if needed.

### Production notes

- Set `debug=False` before deploying.
- Use a production WSGI server (e.g. Gunicorn):

  ```bash
  pip install gunicorn
  gunicorn -w 2 -b 0.0.0.0:5000 app:app   # from Virus_total_based/
  gunicorn -w 2 -b 0.0.0.0:5001 app:app   # from ML_based_detectionn/
  ```

- Never commit real API keys; use environment variables.

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError` | Activate venv and run `pip install -r ML_based_detectionn/requirements.txt` |
| VirusTotal rate limit / empty results | Wait and retry; free API keys have strict quotas |
| `Not included in Database / Scan in Progress` | File hash not in VT yet; upload the file instead of hash |
| ML app crashes on startup | Confirm `ML_model/malwareclassifier-V2.pkl` exists |
| `Unsupported file type` (ML) | Only `.exe` and `.dll` are supported |
| Port already in use | Stop the other process or change the port in `app.py` |

---

## Project structure

```
Malware-Detection-and-Analysis-using-Machine-Learning/
├── Virus_total_based/          # Static analysis (port 5000) — MDAAS landing page
│   ├── app.py
│   ├── static/
│   └── templates/
├── ML_based_detectionn/        # ML detection (port 5001)
│   ├── app.py
│   ├── feature_extraction.py
│   ├── ML_model/
│   ├── static/
│   └── templates/
├── malware_ditaction_insa_1.ipynb
├── run.md                      # This file
└── README.md
```
