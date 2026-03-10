🎬 AIVP – AI Video Production Configurator (Browser App)

This project is intended to:
-Practice the complete process from application requirements analysis to implementation
-Apply advanced Python concepts in a browser-based application (NiceGUI)
-Demonstrate data validation, a clean architecture (presentation / application logic / persistence), and database access via ORM
-Produce clean, well-structured, and documented code (incl. tests)
-Solve a real-world bottleneck in AI video production by automating JSON configuration assembly

#📝 Application Requirements

###Problem
In current AI video production, operators must manually identify and move specific JSON configuration files (representing different LoRA models) into production folders. This process is slow, lacks version control, and is highly prone to human error, such as selecting incompatible models or missing a required component for a client’s brand style.

###Scenario
The AIVP Configurator solves this by providing a dynamic interface where an operator selects the number of required AI "components" and picks specific trained LoRAs from dropdowns. Upon clicking "Go," the system validates the selection, saves the configuration to the database, and automatically moves the JSON files to the ComfyUI working directory to trigger the GPU rendering process.

###User stories
-As a user (Operator), I want to dynamically add or remove component columns using "+" and "−" so I can adapt the workflow to the client project.
-As a user (Operator), I want to select LoRA models from dropdowns to avoid manual filename searches.
-As a user (Operator), I want to save successful model combinations as "Combo Templates" for reuse.
-As a CTO, I want the system to move the corresponding JSON files to a defined "working folder" automatically.
-As an admin, I want to see all past production runs, ordered by date, to track volume and costs.

**Use cases**

-Manage Workflow Layout (Operator): Add/Remove columns dynamically.
-Configure Production (Operator): Select LoRAs and validate settings.
-Execute Run (CTO/Operator): Move JSON files and log transaction.
-Manage Templates (Operator/Product Owner): Save, Load, and Rename Combos.
-View History (Admin): Review past transactions.

**Actors**
-Operator: Builds daily configurations.
-CTO: Manages system integration and file paths.
-Admin: Oversees production history and business reporting.

### Wireframes / Mockups

## 🏛️ Architecture
Software Architecture
The project follows a Layered Architecture pattern, ensuring that the UI is decoupled from the actual logic of moving files or querying the database.

**Layers / components:**

-UI: NiceGUI pages using reactive state for dynamic column generation.
-Application logic: logic.py for validation and file_service.py for OS/shutil operations.
-Persistence: SQLite database accessed via SQLModel/SQLAlchemy ORM.

**Design decisions:**

-Organize code using **MVC**:
  - **Model:** ORM entities (LoRA, Combo, Log).
  - **View:** NiceGUI UI components and reactive layouts.
  - **Controller:** Event handlers coordinating between UI and file services.
-Repository Pattern: Centralized data access for LoRAs and Templates to minimize coupling.

**Design patterns used (examples):**
-MVC (Model–View–Controller): For structured separation of data, logic, and interface.
-Repository Pattern: Implemented in queries.py to abstract database access, providing a clean API for the UI to fetch LoRAs and Templates.
-Strategy Pattern: Used for validation rules (e.g., different validation "strategies" for Cinematic vs. Product video workflows).
-Adapter Pattern: The file_service.py acts as an adapter, translating the application’s internal configuration into the specific file-system structure required by the external ComfyUI engine.

### 🗄️ Database and ORM
The database uses a relational schema to manage the dynamic nature of AI model combinations.

**ORM and Entities (example):** In the database, configurations are stored in ComboTemplate entities. The ComboTemplate ↔ ComboItem relationship (1:N) ensures that a single template can contain any number of LoRA components. Each ComboItem stores a position (column index) and a foreign key to a LoraModel. This ensures that when a template is loaded, the models appear in the correct sequence. The ProductionLog entity acts as an audit trail for every "Go" action taken by the operator.

## ✅ Project Requirements

---

> 🚧 Requirements act as a contract: implement and demonstrate each point below.

Each app must meet the following criteria in order to be accepted:

1. Using NiceGUI for building an interactive web app.
2. Data validation in the app.
3. Using an ORM for database management.


### 1. Browser-based App (NiceGUI)

>The application provides a dynamic, real-time interface for AI video production. The browser acts as a thin client, where the UI state is managed on the server-side to ensure consistency.

Key Interactive Features:

-Dynamic Component Grid: Users can add or remove LoRA selection columns using + and − buttons. The UI automatically re-renders the grid without a page reload using NiceGUI's -reactive state.
-Searchable Dropdowns: LoRA models are fetched from the database and presented in searchable ui.select components for rapid configuration.
-Live Status Dashboard: A summary panel shows the currently selected models and the calculated production cost (e.g., CHF 2.50) before execution.
-Execution Feedback: When the "Go" button is clicked, the app provides visual notifications (success/error) and progress indicators while JSON files are being moved.

---

### 2. Data Validation
To prevent production failures and GPU credit waste, the application validates all inputs before any files are moved or the database is updated.

**Implemented Checks:**

-Completeness Validation: The system blocks execution if any added component column has no LoRA model selected.
-Duplicate Prevention: A warning is triggered if the same LoRA is selected in multiple slots, which could cause "over-fitting" or crashes in the ComfyUI engine.
-File Integrity Check: Before finalizing, the app verifies that the physical .json file associated with the selected LoraModel actually exists in the source directory.
-Template Naming: When saving a "Combo," the app validates that the name is not empty and does not already exist in the database.

---

### 3. Database Management

All relevant data is managed via ORM (SQLModel). This includes the library of available LoRA models, saved templates, and the production history.

---

### 3. Database Management

All persistent data is managed via SQLModel (SQLAlchemy + Pydantic). This ensures a clean mapping between Python objects and the SQLite database.

---

## ⚙️ Implementation

### Technology
The project leverages a modern Python stack designed for fast, reactive web applications and reliable data persistence.

-Python 3.13: The latest stable version, utilized for its performance improvements and advanced type-hinting support.
-Environment: GitHub Codespaces: Provides a consistent, containerized development environment, ensuring that the shutil file operations and database paths remain uniform across the team.
-External Libraries:
   -NiceGUI: Used to build the high-level UI. It handles the websocket communication between the browser and the Python backend, enabling the "Thin Client" architecture.
   -SQLModel: A library for interacting with SQL databases from Python code. It combines SQLAlchemy (the industry-standard ORM) and Pydantic (for data validation), 
   ensuring that our LoRA models and Combo templates are type-safe.
   -Pydantic: Strictly used for validating the JSON configuration structures before they are passed to the ComfyUI engine.
   -Aiofiles / Shutil: Standard libraries used for asynchronous and synchronous file system management to move AI configuration files into production folders.
   -Pytest: The framework used for unit testing the logic in pricing.py and logic.py without needing to launch the UI.


### 📂 Repository Structure

aivp-configurator/
├─ app/
│  ├─ main.py                # Entrypoint: starts the NiceGUI app
│  ├─ aivp/                  # Main module
│  │  ├─ persistence/        # Data access layer
│  │  │  ├─ models.py        # ORM models (LoraModel, ComboTemplate, ProductionLog)
│  │  │  ├─ queries.py       # Repository pattern: CRUD operations
│  │  │  └─ db.py            # SQLite engine & session factory
│  │  ├─ file_service.py     # Logic to move JSON files to ComfyUI
│  │  ├─ logic.py            # Validation rules and dynamic column state
│  │  └─ seed.py             # Script to populate initial LoRA library
├─ data/                     # Local SQLite database (gitignored)
├─ models_json/              # Source directory of all available LoRA JSONs
├─ production_working/       # Target folder where ComfyUI reads configs
└─ tests/                    # Automated test suite

---

### How to Run

### 1. Project Setup
-Python 3.13 is required for this project.
-Create and activate a virtual environment:
   - **macOS/Linux:**
      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```
   - **Windows:**
      ```bash
      python -m venv .venv
      .venv\Scripts\Activate
      ```
- Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
### 2. Configuration

-Setup environment variables in a .env file:

  -DATABASE_URL: Path to your SQLite database (e.g., sqlite:///data/config.db).
  -SOURCE_JSON_PATH: Directory containing your LoRA JSON library.
  -OUTPUT_JSON_PATH: The working directory where ComfyUI reads active configs.

### 3. Launch
- Start the NiceGUI app (example):
   ```bash
   python app/main.py
   ```
- Open the URL printed in the console.

### 4. Usage (document as steps)
Generate AI Video Configuration:
  1. Define Layout: Use the "+" and "−" buttons to set the number of LoRA component columns needed for the specific client project.
  2. Select Models: Use the dropdown menus in each column to choose the appropriate trained AI models (e.g., specific brand style, lighting, or product LoRA).
  3.Manage Templates: (Optional) Load an existing "Combo Template" for standard brand styles or save your current selection as a new template.
  4.Validate & Produce: Click "Start Production". The system validates that all fields are filled, logs the transaction in the database, and automatically moves the corresponding JSON files to the ComfyUI production folder.

## 🧪 Testing

> The testing strategy focuses on ensuring that the dynamic configuration logic is robust and that the file system operations (moving JSON files) are reliable without corrupting the production environment.

**Types:**

-Unit Tests: * Validation Rules: Testing the logic.py module to ensure that configurations with missing fields or duplicate LoRAs are correctly rejected.
  -Pricing Logic: Verifying that the cost calculation (e.g., CHF 2–3 per video) accurately reflects the number of components used.
  
-Integration Tests: * ORM Mappings: Testing persistence/models.py to ensure that ComboTemplates and their related ComboItems are correctly saved and retrieved from the SQLite database.
  -File System Adapter: Using a mock file system to verify that file_service.py correctly identifies source JSON files and "moves" them to the target production folder.

  **Run:**
```bash
pytest
```
---

### Libraries Used

nicegui: For the reactive web interface and state management.
sqlmodel (sqlalchemy + pydantic): For database ORM and data structure validation.
pytest: For automated unit and integration testing.
python-dotenv: For managing environment-specific file paths.
shutil/os: For interacting with the server's file system.
