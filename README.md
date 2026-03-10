AIVP – AI Video Production Configurator
Configure AI video pipelines in your browser. Select LoRA models, save combo templates, export validated JSON to ComfyUI — in under 2 minutes instead of 20.
 Python 3.10+    NiceGUI    SQLAlchemy    SQLite    pytest 

Problem
Manual JSON configuration for ComfyUI production pipelines takes ~20 minutes per order. Operators search files by hand, risk selecting incompatible models, and lack any version control or audit trail.
Solution
AIVP provides a browser-based interface that dynamically builds validated LoRA configurations and transfers them directly to the production pipeline — with full logging and reusable templates.
[ Screenshots: Main UI  |  Combo Manager  |  History View ]
Features
•	Dynamic Layout — Add/remove LoRA columns with “+” / “−” to match each project
•	LoRA Selector — Categorized dropdowns — no manual file searches
•	Combo Templates — Save, load, and rename proven configurations
•	LoRA Library — Manage all models via UI (CRUD, no file edits)
•	Auto JSON Transfer — Validated one-click export to ComfyUI
•	Production History — Every run logged with timestamp, customer, and config

Tech Stack
Component	Technology
Frontend	NiceGUI (Vue.js / Quasar)
Backend	Python 3.10+ with OOP
Database	SQLite + SQLAlchemy ORM
Validation	Pydantic
Testing	pytest
AI Tooling	Claude / GitHub Copilot

Quickstart
git clone https://github.com/<your-org>/aivp-configurator.git
cd aivp-configurator

python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
python main.py

Open http://localhost:8080 in your browser.

Requirements
•	Python 3.10+
•	Modern browser (Chrome, Firefox, Edge)
•	No external DB setup needed (SQLite is embedded)
•	ComfyUI working directory path configured in .env (see .env.example)

Usage
1. Open the app → Set columns with “+” / “−”
2. Select LoRA models from dropdowns per slot
3. (Optional) Save the combination as a Combo Template
4. Click “Go” → Validates, saves to DB, moves JSON to ComfyUI
5. Production starts automatically

Example
Operator opens AIVP
  → Adds 3 columns
  → Selects: product_v3 + cinematic_style + brand_overlay
  → Saves as “Client-X Standard”
  → Clicks Go → JSON validated, logged, transferred
  → Done in ~90 seconds

Architecture
Three-layer separation: Presentation → Application Logic → Persistence.

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

Project Structure
aivp-configurator/
├── main.py                  # Entry point
├── .env.example             # Config template
├── ui/                      # NiceGUI screens
│   ├── main_page.py
│   ├── lora_selector.py
│   ├── combo_manager.py
│   ├── history_view.py
│   └── library_view.py
├── services/                # Business logic
│   ├── configurator.py
│   ├── json_builder.py
│   ├── file_transfer.py
│   ├── combo_service.py
│   ├── lora_service.py
│   └── history_service.py
├── models/                  # ORM entities & DB
├── tests/                   # pytest
├── docs/                    # Detailed documentation
└── requirements.txt

Team
Member	Focus	Responsibilities
Cédric Neuhaus	Product Owner & Frontend	Requirements, NiceGUI screens, coordination
Samson Hadgu	Backend & Integration	JSON builder, file transfer, ComfyUI domain
Fabian Eppenberger	Persistence & Testing	SQLAlchemy ORM, data model, pytest

Documentation
Detailed docs live in /docs/:
File	Content
docs/user-stories.md	User stories with acceptance criteria
docs/use-cases.md	Use cases and actor definitions
docs/architecture.md	Data model, ER diagram, design patterns
docs/milestones.md	Sprint plan and semester milestones

Context
Academic project — Advanced Programming (BSc BIT, FHNW SS 2026). Lecturers: Prof. Dr. Phillip Gachnang & Prof. Dr. Rainer Telesko.
License
Academic project — FHNW, Spring Semester 2026.
<img width="451" height="695" alt="image" src="https://github.com/user-attachments/assets/5dc44785-f41e-49c7-b42c-2b688c0e0a94" />
