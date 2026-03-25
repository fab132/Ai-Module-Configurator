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

Diagram wird ergänzt.

**Use Cases**
- Register / Login (User) — create an account with email and password, or log in for returning access
- Configure Run (Operator) — select 8 parameters and trigger workflow
- Select Output Format (Operator) — choose resolution and aspect ratio before triggering a run
- Save / Download Output (Operator) — download generated image to device or save to cloud storage
- Save Combo Template (Operator) — store a named parameter set
- Load Combo Template (Operator) — apply a saved set to the form
- View Run History (Operator) — browse past runs with settings and timestamps
- Add LoRA Model (Admin) — add a new model entry to the library
- Edit LoRA Model (Admin) — update metadata of an existing model entry
- Delete LoRA Model (Admin) — remove an outdated or unused model from the library

**Actors**
- User (registers and logs in)
- Operator (configures and triggers runs, manages output)
- Admin (manages LoRA model library)

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
- **Services** (business logic: auth, JSON builder, file transfer, combo/lora/history/output services)
- **Persistence** (SQLite + SQLAlchemy ORM entities)

**Design Decisions:**
- Three-layer separation: Presentation → Services → Persistence
- UI never accesses the DB directly — always via service layer
- Authentication is handled server-side via auth_service.py; passwords are never stored in plaintext
- Business rules (JSON merge, validation) are testable without starting the UI
- ComfyUI API call is isolated in file_transfer.py (Adapter pattern)
- Output delivery (local download or cloud save) is handled in output_service.py, keeping it separate from the run pipeline

**Design Patterns:**
- MVC (Model–View–Controller)
- Repository/Service for database access (`*_service.py`)
- Adapter for external ComfyUI API (`file_transfer.py`)

```
┌────────────────────────────────────────────────────────┐
│  UI Layer (NiceGUI)                                    │
│  Login · Register · 8 Dropdowns · Run Button           │
│  History Table · Output Download · LoRA Library        │
├────────────────────────────────────────────────────────┤
│  Service Layer (Python OOP)                            │
│  Auth · JSON Builder · Validation · API Transfer       │
│  Output Delivery · Combo · LoRA · History              │
├────────────────────────────────────────────────────────┤
│  Data Layer (SQLAlchemy → SQLite)                      │
│  User · LoraModel · Combo · ComboItem · RunLog         │
└────────────────────────────────────────────────────────┘
        ↓ validated JSON
  [ ComfyUI API — external ]
        ↓ generated output
  [ Local Download  /  Cloud Storage — external ]
```

---

### 🗄️ Database and ORM

<!-- ![ER Diagram](docs/architecture-diagrams/er_diagram.png) -->
> ER-Diagramm wird ergänzt.

**Entities:**

`User` — registered user with email and hashed password; anchors all run history and combo templates to an account <br/>
`LoraModel` — represents a single LoRA model with name, category, and file path <br/>
`Combo` — a named template grouping multiple LoRA selections; owned by a User <br/>
`ComboItem` — one slot within a Combo (references a LoraModel + slot index + weight) <br/>
`RunLog` — immutable log entry for each production run (user, config JSON, output format, timestamp)

`User` ↔ `RunLog` is one-to-many (each run belongs to a user). `User` ↔ `Combo` is one-to-many. `Combo` ↔ `ComboItem` is one-to-many with cascade delete. `ComboItem` ↔ `LoraModel` is many-to-one.

---

## ✅ Project Requirements

---

### 1. Browser-based App (NiceGUI)

The application runs entirely in the browser via NiceGUI. Users can:

- Register a new account with email and password
- Log in to access their personal run history and Combo Templates
- Select 8 production parameters via dropdowns
- Choose output format (resolution and aspect ratio) before triggering a run
- Trigger a ComfyUI workflow with one click
- Download the generated output to their device or save it to cloud storage
- Save and load Combo Templates
- Browse personal run history with timestamps and settings
- Manage the LoRA model library (add, edit, delete — admin only)



**Architecture note:** the browser is a thin client; all UI state, authentication, and business logic run server-side in the NiceGUI app.

---

### 2. Data Validation

All inputs are validated before a run is triggered:
- Email must be a valid format on registration; password must meet minimum strength requirements
- All 8 parameter dropdowns must have a selection
- Output format (resolution, aspect ratio) must be selected before triggering a run
- Combo names must be unique and non-empty
- LoRA model entries are validated via Pydantic schemas before DB insert
- Passwords are never stored in plaintext — hashed via `bcrypt` before persisting to DB

---

### 3. Database Management

All data is managed via SQLAlchemy ORM (SQLite). Entities: `User`, `LoraModel`, `Combo`, `ComboItem`, `RunLog`. Database is initialized automatically on startup via `init_db()`. Each user's run history and combo templates are scoped to their account via foreign key relationships.

---

## ⚙️ Implementation

---

### Technology

- Python 3.10+
- NiceGUI (browser-based UI)
- SQLAlchemy (ORM)
- Pydantic (validation)
- bcrypt (password hashing)
- pytest (testing)
- python-dotenv (configuration)

---

### 📂 Repository Structure

```text
Ai-Module-Configurator/
├── README.md
├── requirements.txt
├── .env.example               # DATABASE_URL + COMFYUI_OUTPUT_PATH + CLOUD_STORAGE_URL
├── .gitignore
├── main.py                    # Entry point
│
├── docs/
│   ├── ui-images/             # Screenshots and wireframes
│   └── architecture-diagrams/ # UML and ER diagrams
│
├── ui/                        # NiceGUI pages
│   ├── login_page.py          # Login form (new)
│   ├── register_page.py       # Registration form (new)
│   ├── main_page.py
│   ├── lora_selector.py
│   ├── combo_manager.py
│   ├── history_view.py
│   ├── library_view.py
│   └── components/
│
├── services/                  # Business logic
│   ├── auth_service.py        # Register, login, password hashing (new)
│   ├── configurator.py
│   ├── json_builder.py
│   ├── file_transfer.py
│   ├── output_service.py      # Local download + cloud save (new)
│   ├── combo_service.py
│   ├── lora_service.py
│   └── history_service.py
│
├── models/                    # ORM entities & DB setup
│   ├── base.py
│   ├── database.py
│   └── entities.py            # Now includes User entity
│
├── utils/                     # Validators and helpers
│   ├── validators.py          # Now includes email + password validators
│   ├── password_utils.py      # bcrypt hashing helpers (new)
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
1. Open the app — register with your email and password, or log in if you already have an account.
2. Select values for Person, Content-Type, Platform, Format, Scenery, Outfit, Lighting, Perspective.
3. Choose the output format (resolution and aspect ratio) for the target platform.
4. (Optional) Save the selection as a Combo Template for reuse.
5. Click **Run** → config is validated, logged, and sent to ComfyUI.
6. Download the generated output to your device or save it to cloud storage.

<!-- ![UI – Main](docs/ui-images/ui_main.png) -->

---

## 🧪 Testing

We test the three core layers of the application: business logic (unit), database persistence (DB), and the end-to-end run pipeline (integration). Each test follows the AAA pattern (Arrange → Act → Assert) and covers both happy paths and edge cases as taught in the course.

**Test mix:**
Overall 15 tests
- 7 Unit tests: e.g. JSON merge with all 8 parameters, missing config file raises `FileNotFoundError`, valid parameter set passes validation, incomplete parameter set raises `ValidationError`, user registration with valid email and password, user login with valid credentials, edit LoRA model updates DB entry
- 4 DB tests: e.g. run history returns correct logged entries (US8), LoRA query returns seeded models, saving a Combo persists Combo + ComboItems, empty DB returns empty run history
- 3 Integration tests: e.g. full run with valid params creates RunLog entry, run with missing param is blocked before API call, saving and reloading a Combo Template restores full parameter set

**Note** : US5 (output format selection) and US6 (download / cloud save) are outside the current test scope cap of 15 and are planned for a future test cycle.


## TC_001 — JSON Builder Happy Path
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



## TC_002 — JSON Builder Missing Config File
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


## TC_003 — Run History Returns Correct Entries (US4)
| Field | Details|
|------|--------------|
| **Test case ID** | TC_003 |
| **Test case title/description** | Run history returns all logged runs with correct data |
| **Preconditions** | Test SQLite DB initialized; multiple `RunLog` rows (e.g. 2) seeded with known config JSON and timestamps |
| **Test steps** | 1. **Arrange** — seed multiple `RunLog` rows (e.g. 2) with distinct config JSON and timestamps.  <br/> 2. **Act** — call `history_service.get_all()`. <br/> 3. **Assert** — result is a list containing all seeded `RunLog` entries with correct config JSON, customer info, and non-null timestamps | 
| **Test data** | Multiple run log entries (e.g. 2) with distinct timestamps and config JSON matching the valid parameter set from TC_004 |
| **Expected result** | Returns a list containing all seeded `RunLog` entries with correct field values in descending timestamp order |
| **Actual result** |  — |
| **Status** | — |
| **Comments** | Happy path for US8 — verifies the operator can view all past runs with their settings; complements the empty history edge case in TC_011 |


## TC_004 — Parameter Validator Happy Path
| Field | Details|
|------|--------------|
| **Test case ID** | TC_004 |
| **Test case title/description** | Validator accepts a fully populated valid parameter set |
| **Preconditions** | Pydantic schema for run parameters is defined|
| **Test steps** | 1. **Arrange** — prepare a dict with all 8 required fields set to valid string values.   <br/> 2. **Act** — instantiate the Pydantic schema with that dict.  <br/> 3. **Assert** — result is a list containing all seeded `RunLog` entries with correct config JSON, customer info, and non-null timestamps | 
| **Test data** | `{ person: "Persona_A", content_type: "Photo", platform: "Instagram", format: "Square", scenery: "Studio", outfit: "Casual", lighting: "Soft", perspective: "Front" }`|
| **Expected result** | Schema instantiates without raising a `ValidationError` |
| **Actual result** |  — |
| **Status** | — |
| **Comments** | baseline validation test |

## TC_005 — Parameter Validator Missing Field
| Field | Details|
|------|--------------|
| **Test case ID** | TC_005 |
| **Test case title/description** | Validator raises `ValidationError` when one required field is missing |
| **Preconditions** | Pydantic schema for run parameters is defined|
| **Test steps** | 1. **Arrange** — prepare the dict from TC_004 with the `perspective` key removed.    <br/> 2. **Act** —instantiate the schema inside `pytest.raises(ValidationError)`.  <br/> 3. **Assert** — error message references the `perspective` field. | 
| **Test data** | Same as TC_004 but `perspective` key removed|
| **Expected result** | Raises `ValidationError` identifying the missing field by name |
| **Actual result** |  — |
| **Status** | — |
| **Comments** | Exception case — ensures all 8 dropdowns are enforced before a run is triggered; uses `pytest.raises()` |


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
