# E-Health ID Generator

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![wxPython](https://img.shields.io/badge/wxPython-0D7DB0?logo=python&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-000?logo=apple&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white)

![EHealth Logo](./ehealth.png)

## Overview

E-Health ID Generator provides a simple way to produce unique identifiers for cancer data. These identifiers are intended to support research where records will eventually be converted to the [OMOP](https://www.ohdsi.org/data-standardization/the-common-data-model/) common data model. Having a consistent ID format helps link data across studies without exposing personal information.

The application also bundles tools for encrypting/decrypting files using the [Crypt4GH](https://github.com/EGA-archive/crypt4gh) standard and generating compatible key pairs.

## Features

- **Generate IDs** – Create large batches of pseudonymous IDs using a deterministic seed or random values.
- **Encrypt/Decrypt** – Protect files with Crypt4GH. Useful when sharing sensitive datasets.
- **Generate Keys** – Produce public/private key pairs for encryption workflows.

## Installation

### macOS

```bash
brew install python3       # if Python is not installed
python3 -m pip install -r requirements.txt
python3 main.py
```

### Windows

```powershell
# Install Python from https://www.python.org/downloads/
python -m pip install -r requirements.txt
python main.py
```

Executables can be built using PyInstaller. Spec files for both platforms are included in the repository.

## How It Works

<details>
<summary>Code Overview</summary>

- **`model.py`** contains the logic for generating base‑62 IDs and saving them in several formats (CSV, TXT, JSON, XLSX).
- **`view.py`** builds the GUI with `wxPython` and offers screens for ID generation, file encryption/decryption, and key creation.
- **`controller.py`** wires the interface to the model, manages progress dialogs and invokes `crypt4gh` when encrypting or decrypting files.
- **`main.py`** starts the application by creating the model, view and controller.

</details>

## Acknowledgements

This project is part of the **eHealth Hub for Cancer Research** and funded through the **National Science Research Programme (NSRP)**. We acknowledge the contributions of the **Health Ethics Authority (HEA)** for enabling this initiative.

