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

