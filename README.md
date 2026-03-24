# AIVP – AI Visual Production

> Screenshot wird ergänzt sobald die UI fertig ist.

<img width="1037" height="583" alt="Bildschirmfoto 2026-03-23 um 23 32 54" src="https://github.com/user-attachments/assets/b3554ef8-8582-4bae-9138-e36fa12df840" />


---

This project is intended to:

- Practice the complete process from **application requirements analysis to implementation**
- Apply advanced **Python** concepts in a browser-based application (NiceGUI)
- Demonstrate **data validation**, a clean architecture (presentation / application logic / persistence), and **database access via ORM**
- Produce clean, well-structured, and documented code (incl. tests)
- Prepare students for **teamwork and professional documentation**

---

## 📝 Application Requirements

---

### Problem

In AI content production with ComfyUI, configuring each run requires manually editing JSON files, selecting compatible LoRA models, and setting sampler parameters by hand. For a team with mixed technical backgrounds, this process takes up to 20 minutes per run and is highly error-prone — especially when switching between personas, platforms, or formats.

---

### Scenario

AIVP solves this by providing a browser-based configuration interface. The operator selects 8 parameters (Person, Content-Type, Platform, Format, Scenery, Outfit, Lighting, Perspective), each backed by a JSON config file. On clicking **Run**, the app merges all configs into a complete ComfyUI workflow and sends it directly to the ComfyUI API. Every run is logged with timestamp, settings, and customer info.

---

### User Stories

1. As a new user, I want to register with my email and password so I can access the application and have my data saved for future use.
2. As a returning user, I want to log in with my email and password so I can access my previous configurations and run history.
3. As an operator, I want to select a persona and content parameters from dropdowns so I can configure a run without editing JSON manually.
4. As an operator, I want to click Run and have the workflow sent to ComfyUI automatically.
5. As an operator, I want to choose the output format of the generated image (e.g. resolution, aspect ratio) so the result fits the target platform requirements.
6. As an operator, I want to download the generated output directly to my device or save it to cloud storage so I can use it in my workflow.
7. As an operator, I want to save a parameter combination as a Combo Template so I can reuse it for repeat customers.
8. As an operator, I want to see a history of all past runs with their settings and timestamps so I can track and reproduce previous productions.
9. As an admin, I want to add a new LoRA model to the library so operators have access to the latest models.
10. As an admin, I want to edit an existing LoRA model entry so I can correct or update its metadata.
11. As an admin, I want to delete a LoRA model from the library so outdated or unused models no longer appear in the selection.

---

### Use Cases

<!-- ![UML Use Case Diagram](docs/architecture-diagrams/uml_use_case_diagram.png) -->
> Diagram wird ergänzt.

**Use Cases**
- Configure Run (Operator) — select 8 parameters and trigger workflow
- Save Combo Template (Operator) — store a named parameter set
- Load Combo Template (Operator) — apply a saved set to the form
- View Run History (Operator) — browse past runs
- Manage LoRA Library (Admin) — CRUD on LoRA model entries

**Actors**
- Operator (configures and triggers runs)
- Admin (manages model library)

---

### Wireframes / Mockups

<!-- ![Wireframe – Main](docs/ui-images/wireframe_main.png) -->
> Wireframes werden ergänzt.

---

## 🏛️ Architecture

---

### Software Architecture

<!-- ![UML Class Diagram](docs/architecture-diagrams/uml_class_architecture.png) -->
> Diagramm wird ergänzt.

**Layers / Components:**
- **UI** (NiceGUI pages and components — browser as thin client)
- **Services** (business logic: JSON builder, file transfer, combo/lora/history services)
- **Persistence** (SQLite + SQLAlchemy ORM entities)

**Design Decisions:**
- Three-layer separation: Presentation → Services → Persistence
- UI never accesses the DB directly — always via service layer
- Business rules (JSON merge, validation) are testable without starting the UI
- ComfyUI API call is isolated in `file_transfer.py` (Adapter pattern)

**Design Patterns:**
- MVC (Model–View–Controller)
- Repository/Service for database access (`*_service.py`)
- Adapter for external ComfyUI API (`file_transfer.py`)

```
┌──────────────────────────────────────────────┐
│  UI Layer (NiceGUI)                          │
│  8 Dropdowns · Run Button · History Table    │
├──────────────────────────────────────────────┤
│  Service Layer (Python OOP)                  │
│  JSON Builder · Validation · API Transfer    │
├──────────────────────────────────────────────┤
│  Data Layer (SQLAlchemy → SQLite)            │
│  LoraModel · Combo · ComboItem · RunLog      │
└──────────────────────────────────────────────┘
        ↓ validated JSON
  [ ComfyUI API — external ]
```

---

### 🗄️ Database and ORM

<!-- ![ER Diagram](docs/architecture-diagrams/er_diagram.png) -->
> ER-Diagramm wird ergänzt.

**Entities:**

- `LoraModel` — represents a single LoRA model with name, category, and file path
- `Combo` — a named template grouping multiple LoRA selections
- `ComboItem` — one slot within a Combo (references a LoraModel + slot index + weight)
- `RunLog` — immutable log entry for each production run (customer, config JSON, timestamp)

`Combo` ↔ `ComboItem` is a one-to-many relationship with cascade delete. `ComboItem` ↔ `LoraModel` is many-to-one.

---

## ✅ Project Requirements

---

### 1. Browser-based App (NiceGUI)

The application runs entirely in the browser via NiceGUI. Users can:

- Select 8 production parameters via dropdowns
- Trigger a ComfyUI workflow with one click
- Save and load Combo Templates
- Browse run history
- Manage the LoRA model library (CRUD)

**Architecture note:** the browser is a thin client; all UI state and business logic run server-side in the NiceGUI app.

---

### 2. Data Validation

All inputs are validated before a run is triggered:
- All 8 parameter dropdowns must have a selection
- Combo names must be unique and non-empty
- LoRA model entries are validated via Pydantic schemas before DB insert

---

### 3. Database Management

All data is managed via SQLAlchemy ORM (SQLite). Entities: `LoraModel`, `Combo`, `ComboItem`, `RunLog`. Database is initialized automatically on startup via `init_db()`.

---

## ⚙️ Implementation

---

### Technology

- Python 3.10+
- NiceGUI (browser-based UI)
- SQLAlchemy (ORM)
- Pydantic (validation)
- pytest (testing)
- python-dotenv (configuration)

---

### 📂 Repository Structure

```text
Ai-Module-Configurator/
├── README.md
├── requirements.txt
├── .env.example               # DATABASE_URL + COMFYUI_OUTPUT_PATH
├── .gitignore
├── main.py                    # Entry point
│
├── docs/
│   ├── ui-images/             # Screenshots and wireframes
│   └── architecture-diagrams/ # UML and ER diagrams
│
├── ui/                        # NiceGUI pages
│   ├── main_page.py
│   ├── lora_selector.py
│   ├── combo_manager.py
│   ├── history_view.py
│   ├── library_view.py
│   └── components/
│
├── services/                  # Business logic
│   ├── configurator.py
│   ├── json_builder.py
│   ├── file_transfer.py
│   ├── combo_service.py
│   ├── lora_service.py
│   └── history_service.py
│
├── models/                    # ORM entities & DB setup
│   ├── base.py
│   ├── database.py
│   └── entities.py
│
├── utils/                     # Validators and helpers
│   ├── validators.py
│   └── helpers.py
│
├── data/                      # SQLite database (gitignored)
└── tests/                     # pytest
```

---

### How to Run

#### 1. Project Setup

```bash
python3 -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows

pip install -r requirements.txt
```

#### 2. Configuration

```bash
cp .env.example .env
```

Edit `.env` and set `COMFYUI_OUTPUT_PATH` to your local ComfyUI input directory.

#### 3. Launch

```bash
python main.py
```

Open the URL shown in the console (default: http://localhost:8080).

#### 4. Usage

Configure a run:
1. Open the app — the main page shows 8 parameter dropdowns.
2. Select values for Person, Content-Type, Platform, Format, Scenery, Outfit, Lighting, Perspective.
3. *(Optional)* Save the selection as a Combo Template for reuse.
4. Click **Run** → config is validated, logged, and sent to ComfyUI.

<!-- ![UI – Main](docs/ui-images/ui_main.png) -->

---

## 🧪 Testing

We test the three core layers of the application: business logic (unit), database persistence (DB), and the end-to-end run pipeline (integration). Each test follows the AAA pattern (Arrange → Act → Assert) and covers both happy paths and edge cases as taught in the course.

**Test mix:**
Overall 15 tests
- 7 Unit tests: e.g. JSON merge with all 8 parameters, missing config file raises FileNotFoundError, valid parameter set passes validation, incomplete parameter set raises ValidationError, user registration with valid email and password, user login with valid credentials, edit LoRA model updates DB entry
- 4 DB tests: e.g. run history returns correct logged entries (US8), LoRA query returns seeded models, saving a Combo persists Combo + ComboItems, empty DB returns empty run history
- 3 Integration tests: e.g. full run with valid params creates RunLog entry, run with missing param is blocked before API call, saving and reloading a Combo Template restores full parameter set

---
**TC_001 — JSON Builder Happy Path**
| Field | Details|
|------|--------------|
| **Test case ID** | TC_001 |
| **Test case title/description** |  JSON builder merges all 8 parameter configs into one valid workflow |
| **Preconditions** | 8 mock JSON config files exist (one per parameter) |
| **Test steps** | 1. **Arrange** — prepare 8 minimal JSON stubs, one per parameter. <br/> 2. **Act** — call `json_builder.build(params)` with all 8 parameters. <br/> 3. **Assert** — verify the returned dict contains all keys from all 8 stubs |
| **Test data** | One minimal JSON stub per parameter (Person, Content-Type, Platform, Format, Scenery, Outfit, Lighting, Perspective) |
| **Expected result** | Returns a single merged dict containing all keys from all 8 configs |
| **Actual result** |  — |
| **Status** | — |
| **Comments** | Happy path — core merge logic; no DB or API required |

---
**TC_002 — JSON Builder Missing Config File**
| Field | Details|
|------|--------------|
| **Test case ID** | TC_002 |
| **Test case title/description** | JSON builder raises `FileNotFoundError` when a parameter config file is missing |
| **Preconditions** | 7 of 8 config files exist; one is intentionally absent |
| **Test steps** | 1. **Arrange** — provide 7 valid stubs, omit one file. <br/> 2. **Act** — call `json_builder.build(params)` inside `pytest.raises(FileNotFoundError)`. <br/> 3. **Assert** — exception is raised and no partial result is returned | 
| **Test data** | 7 valid stubs, 1 missing file path |
| **Expected result** | Raises `FileNotFoundError` — builder fails loudly, not silently |
| **Actual result** |  — |
| **Status** | — |
| **Comments** | Exception edge case — uses `pytest.raises()` to assert the correct exception type |

---

### Libraries Used

- nicegui
- sqlalchemy
- pydantic
- python-dotenv
- pytest

---

## 👥 Team & Contributions

| Name | Contribution |
|------|--------------|
| Cédric Neuhaus | NiceGUI UI, component design, client-state management |
| Samson Hadgu | JSON builder, ComfyUI API integration, file transfer |
| Fabian Eppenberger | SQLAlchemy ORM, database schema, pytest tests |

---

## 📝 License

Academic project — FHNW, Advanced Programming, BSc BIT, Spring Semester 2026.
