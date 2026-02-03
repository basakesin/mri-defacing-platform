# 🧠 MRI Defacing Platform

**MRI Defacing Platform** is a unified, web-based interface that brings together multiple state-of-the-art MRI defacing and anonymization tools under a single API and web UI.  
It is designed for **neuroimaging researchers, clinicians, and developers** who need a flexible and reproducible way to anonymize MRI data before sharing or analysis.

---

## ✨ Features

- 🌐 Web-based user interface
- 🔌 REST API for programmatic access
- 🧩 Multiple defacing backends under a unified interface
- 🔍 Automatic availability detection of installed tools
- 🧪 Temporary-file–based processing (no data persistence)
- 🎓 Suitable for research, teaching, and prototyping

---

## 🧰 Supported Defacing Methods

| Method | Backend | Description |
|------|--------|-------------|
| **PyDeface** | FSL-based | Industry-standard MRI defacing tool |
| **Quickshear** | FSL (BET + quickshear) | Fast and high-quality surface removal |
| **DeepDefacer** | FSL + Deep Learning | AI-powered face detection and removal |
| **MRI Deface** | FreeSurfer | Classical FreeSurfer-based approach |

> ⚠️ **Important:**  
> Method availability depends on whether the required system tools are installed and available in your `PATH`.

---

## 📁 Project Structure

```text
mri-defacing-platform/
│
├── app.py                 # Flask application (entry point)
├── requirements.txt       # Python dependencies
├── README.md
├── .gitignore
│
├── defacers/              # Defacer backends (modular design)
│   ├── __init__.py
│   ├── base.py
│   ├── utils.py
│   ├── pydeface.py
│   ├── quickshear.py
│   ├── deepdefacer.py
│   └── mri_deface.py
│
├── templates/
│   └── index.html         # Web UI
│
└── static/
```
**#🐍 Python Requirements**

A clean environment is strongly recommended.

```bash
conda create -n mri-deface python=3.10
conda activate mri-deface

```

## 🧠 Installing FSL (Official Method)

For most users, the easiest and recommended installation is via FSL’s official `getfsl.sh` script.

---

### Step 1 — Open a terminal

- **Linux:** Open *Terminal* from the system menu  
- **macOS:** `Applications → Utilities → Terminal`  
- **Windows:** Open your WSL distribution (e.g., Ubuntu)

---

### Step 2 — Run the installer

```bash

curl -Ls https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/releases/getfsl.sh | sh -s
```
Alternatively, if you downloaded the script manually:
```bash
sh ~/Downloads/getfsl.sh
```

### Step 3 — Restart the terminal

Close and reopen your terminal window after the installation completes.

### Step 4 — Verify installation
```bash
fslmaths -version
```

Activate environment:

```bash
conda activate mri-deface
```

Install Requirements:
```bash
pip install -r requirements.txt
```
Start server:

```bash
python app.py
```
