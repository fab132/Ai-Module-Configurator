import json
from nicegui import ui
from models.database import SessionLocal
from services.history_service import get_all


def create_history_view():
    with ui.element("div").classes("p-8 w-full max-w-6xl mx-auto"):
        with ui.row().classes("items-center justify-between mb-6"):
            ui.label("Run History").classes("text-white font-bold").style("font-size: 1.4rem")
            refresh_btn = ui.button("↻ Refresh", icon="refresh").props("flat color=deep-purple-3")

        table_container = ui.element("div").classes("w-full")

        def load_data():
            table_container.clear()
            db = SessionLocal()
            try:
                logs = get_all(db)
            finally:
                db.close()

            with table_container:
                if not logs:
                    with ui.element("div").classes("p-10 text-center").style("color: #6b7280"):
                        ui.label("No runs yet. Configure and trigger a run to see history here.")
                    return

                columns = [
                    {"name": "ran_at", "label": "Timestamp", "field": "ran_at", "align": "left", "sortable": True},
                    {"name": "customer", "label": "Customer / Project", "field": "customer", "align": "left"},
                    {"name": "combo_name", "label": "Template", "field": "combo_name", "align": "left"},
                    {"name": "person", "label": "Person", "field": "person", "align": "left"},
                    {"name": "platform", "label": "Platform", "field": "platform", "align": "left"},
                    {"name": "format", "label": "Format", "field": "format", "align": "left"},
                ]

                rows = []
                for log in logs:
                    try:
                        cfg = json.loads(log.config_json)
                        meta = cfg.get("_meta", {})
                    except Exception:
                        meta = {}
                    rows.append({
                        "id": log.id,
                        "ran_at": log.ran_at.strftime("%Y-%m-%d %H:%M:%S") if log.ran_at else "—",
                        "customer": log.customer or "—",
                        "combo_name": log.combo_name or "—",
                        "person": meta.get("person", "—"),
                        "platform": meta.get("platform", "—"),
                        "format": meta.get("format", "—"),
                    })

                ui.table(
                    columns=columns,
                    rows=rows,
                    row_key="id",
                    pagination={"rowsPerPage": 15},
                ).classes("w-full").props("dark flat bordered").style(
                    "background:#1a1a3e; border:1px solid #2a2a4a; border-radius:8px"
                )

        refresh_btn.on("click", load_data)
        load_data()
