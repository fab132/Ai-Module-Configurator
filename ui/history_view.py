import json
from nicegui import ui
from models.database import SessionLocal
from services.history_service import get_all


def create_history_view():
    with ui.element("div").classes("p-8 w-full max-w-4xl mx-auto"):
        with ui.row().classes("items-center justify-between mb-6"):
            ui.label("Run History").classes("text-white font-bold").style("font-size: 1.4rem")
            refresh_btn = ui.button("↻ Refresh").props("flat dense").style("color:#6B7280")

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
                    with ui.element("div").classes("p-10 text-center").style("color:#6b7280"):
                        ui.label("No runs yet. Configure and trigger a run to see history here.")
                    return

                # Table wrapper
                with ui.element("div").style(
                    "border-radius:8px; overflow:hidden; border:1px solid #2a2a4a"
                ):
                    # Header row
                    with ui.element("div").style(
                        "display:grid; grid-template-columns:60px 1fr 1fr 1fr;"
                        "background:#16213e; padding:10px 16px; border-bottom:1px solid #2a2a4a"
                    ):
                        for col in ["Run", "Timestamp", "Person", "Platform"]:
                            ui.label(col).style(
                                "color:#9CA3AF; font-size:0.82rem; font-weight:700; text-transform:uppercase; letter-spacing:0.06em"
                            )

                    # Data rows
                    for i, log in enumerate(logs):
                        try:
                            meta = json.loads(log.config_json).get("_meta", {})
                        except Exception:
                            meta = {}

                        row_bg = "#1a1a3e" if i % 2 == 0 else "#0f0f23"
                        with ui.element("div").style(
                            f"display:grid; grid-template-columns:60px 1fr 1fr 1fr;"
                            f"background:{row_bg}; padding:10px 16px;"
                            f"border-bottom:1px solid #2a2a4a"
                        ):
                            ui.label(str(log.id)).style("color:white; font-size:0.88rem; font-weight:600")
                            ui.label(log.ran_at.strftime("%Y-%m-%d %H:%M") if log.ran_at else "—").style("color:#D1D5DB; font-size:0.88rem")
                            ui.label(meta.get("person", "—")).style("color:#D1D5DB; font-size:0.88rem")
                            ui.label(meta.get("platform", "—")).style("color:#D1D5DB; font-size:0.88rem")

        refresh_btn.on("click", load_data)
        load_data()
