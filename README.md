# AIVP – AI Visual Production

Configure AI video pipelines in your browser. Select LoRA models, save combo templates, export validated JSON to ComfyUI — in under 2 minutes instead of 20.

![Python](https://img.shields.io/badge/python-3.10+-3776AB?logo=python&logoColor=white)
![NiceGUI](https://img.shields.io/badge/UI-NiceGUI-2EA043)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-CC3333)
![SQLite](https://img.shields.io/badge/DB-SQLite-0F80CC)
![pytest](https://img.shields.io/badge/tests-pytest-666666)

---

## Problem

Manual JSON configuration for ComfyUI production pipelines takes ~20 minutes per order. Operators search files by hand, risk selecting incompatible models, and lack any version control or audit trail.

## Solution

AIVP provides a browser-based interface that dynamically builds validated LoRA configurations and transfers them directly to the production pipeline — with full logging and reusable templates.

<!-- Add screenshots once UI is built:
![Main UI](docs/images/main-ui.png)
![Combo Manager](docs/images/combo-manager.png)
![History View](docs/images/history-view.png)
-->

---

## Features

- **Dynamic Layout** — Add/remove LoRA columns with "+" / "−" to match each project
- **LoRA Selector** — Categorized dropdowns, no manual file searches
- **Combo Templates** — Save, load, and rename proven configurations
- **LoRA Library** — Manage all models via UI (CRUD, no file edits)
- **Auto JSON Transfer** — Validated one-click export to ComfyUI
- **Production History** — Every run logged with timestamp, customer, and config

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | [NiceGUI](https://nicegui.io/) (Vue.js / Quasar) |
| Backend | Python 3.10+ with OOP |
| Database | SQLite + [SQLAlchemy](https://www.sqlalchemy.org/) ORM |
| Validation | Pydantic |
| Testing | [pytest](https://pytest.org/) |
| AI Tooling | Claude / GitHub Copilot |

---

## Quickstart

```bash
git clone https://github.com/<your-org>/aivp-configurator.git
cd aivp-configurator

python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
python main.py
```

Open **http://localhost:8080** in your browser.

### Requirements

- Python 3.10+
- Modern browser (Chrome, Firefox, Edge)
- No external DB setup needed (SQLite is embedded)
- ComfyUI working directory path configured in `.env` (see `.env.example`)

---

## Usage

1. Open the app → Set columns with "+" / "−"
2. Select LoRA models from dropdowns per slot
3. *(Optional)* Save the combination as a Combo Template
4. Click **"Go"** → Validates, saves to DB, moves JSON to ComfyUI
5. Production starts automatically

### Example

```
Operator opens AIVP
  → Adds 3 columns
  → Selects: product_v3 + cinematic_style + brand_overlay
  → Saves as "Client-X Standard"
  → Clicks Go → JSON validated, logged, transferred
  → Done in ~90 seconds
```

---

## Architecture

Three-layer separation: Presentation → Application Logic → Persistence.

```
┌──────────────────────────────────────────────┐
│  UI Layer (NiceGUI)                          │
│  Dynamic columns · Dropdowns · Tables        │
├──────────────────────────────────────────────┤
│  Service Layer (Python OOP)                  │
│  JSON Builder · Validation · File Transfer   │
├──────────────────────────────────────────────┤
│  Data Layer (SQLAlchemy → SQLite)            │
│  LoraModel · Combo · ComboItem · RunLog      │
└──────────────────────────────────────────────┘
        ↓ validated JSON
  [ ComfyUI — external ]
```

### Project Structure

```
aivp-configurator/
├── main.py                  # Entry point
├── .env.example             # Config template
├── .gitignore               # Git exclusion file
├── requirements.txt         # Project dependencies
├── ui/                      # NiceGUI screens
│   ├── __init__.py
│   ├── main_page.py
│   ├── lora_selector.py
│   ├── combo_manager.py
│   ├── history_view.py
│   ├── library_view.py
│   └── components/          # Reusable UI elements
├── services/                # Business logic
│   ├── __init__.py
│   ├── configurator.py
│   ├── json_builder.py
│   ├── file_transfer.py
│   ├── combo_service.py
│   ├── lora_service.py
│   └── history_service.py
├── models/                  # ORM entities & DB
│   ├── __init__.py
│   ├── base.py
│   ├── database.py
│   └── entities.py
├── utils/                   # Shared utilities
│   ├── __init__.py
│   ├── helpers.py
│   └── validators.py
├── tests/                   # pytest
│   └── __init__.py
├── docs/                    # Detailed documentation
│   └── development.md
└── requirements.txt
```

---

## Team

| Member | Focus | Responsibilities |
|--------|-------|-----------------|
| **Cédric Neuhaus** | Frontend & UI/UX Logic| Developing interactive NiceGUI components, managing client-state, and implementing user feedback loops. |
| **Samson Hadgu** | Backend & API Integration | Building the JSON processing engine, managing file I/O operations, and integrating the ComfyUI API. |
| **Fabian Eppenberger** | System Architecture & QA | Designing the SQLAlchemy data model (ORM), managing the database schema, and implementing automated testing (pytest). |

Every member works across all layers. Contributions are tracked via GitHub commits.

---

## Documentation

Detailed docs live in [`/docs/`](docs/):

| File | Content |
|------|---------|
| [`user-stories.md`](docs/user-stories.md) | User stories with acceptance criteria |
| [`user-stories.md`](docs/use-cases.md) | Use cases and actor definitions |
| [`user-stories.md`](docs/architecture.md) | Data model, ER diagram, design patterns |
| [`user-stories.md`](docs/milestones.md) | Sprint plan and semester milestones |
---

## Context

Academic project — **Advanced Programming** (BSc BIT, FHNW SS 2026).
Lecturers: Prof. Dr. Phillip Gachnang & Prof. Dr. Rainer Telesko.

---

## License

Academic project — FHNW, Spring Semester 2026.
