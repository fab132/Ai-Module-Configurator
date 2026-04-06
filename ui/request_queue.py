import json
import uuid
from pathlib import Path
from nicegui import ui, events
from models.database import SessionLocal
from models.entities import RunLog, Client, ClientPhoto
from services.history_service import (
    get_all, get_by_status, set_status, set_output, count_pending,
    STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_DONE,
)

OUTPUTS_DIR = Path("data/outputs")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

CLIENT_PICS = Path("data/client_pics")
REFS_DIR    = Path("data/client_refs")

PLACEHOLDER = "https://ui-avatars.com/api/?background=7c3aed&color=fff&size=64&bold=true&name="

STATUS_CFG = {
    STATUS_PENDING:     ("🕐  Pending",     "#6b7280", "#1f2937"),
    STATUS_IN_PROGRESS: ("⚙️  In Progress", "#f59e0b", "#292213"),
    STATUS_DONE:        ("✅  Done",         "#10b981", "#0d2117"),
}


def _avatar(client) -> str:
    if client and client.profile_picture and Path(client.profile_picture).exists():
        return f"/client_pics/{Path(client.profile_picture).name}"
    name = client.name if client else "?"
    return PLACEHOLDER + "+".join(name.split()[:2])


def _meta(run: RunLog) -> dict:
    try:
        return json.loads(run.config_json).get("_meta", {})
    except Exception:
        return {}


def _badge(status: str) -> tuple:
    return STATUS_CFG.get(status, STATUS_CFG[STATUS_PENDING])


def create_request_queue():
    filter_state = {"value": "all"}

    with ui.element("div").classes("p-8 w-full max-w-5xl mx-auto"):
        with ui.row().classes("items-center justify-between mb-4"):
            ui.label("Production Requests").classes("text-white font-bold").style("font-size:1.4rem")

            # Live pending count
            db0 = SessionLocal()
            pending_n = count_pending(db0)
            db0.close()
            pending_badge = ui.badge(str(pending_n)).props("color=red").style(
                "font-size:0.85rem; padding:4px 10px;" + ("display:none" if pending_n == 0 else "")
            )

        # Filter row
        with ui.row().classes("gap-3 mb-6"):
            for label, val in [("All", "all"), ("🕐 Pending", "pending"), ("⚙️ In Progress", "in_progress"), ("✅ Done", "done")]:
                def make_filter(v):
                    def do():
                        filter_state["value"] = v
                        refresh()
                    return do
                ui.button(label, on_click=make_filter(val)).props(
                    f"{'unelevated color=deep-purple' if filter_state['value'] == val else 'outlined color=blue-4'} dense"
                )

        list_container = ui.element("div").classes("w-full")

        def refresh():
            list_container.clear()
            db = SessionLocal()
            try:
                if filter_state["value"] == "all":
                    runs = get_all(db)
                else:
                    runs = get_by_status(db, filter_state["value"])
                pending_count = count_pending(db)
                # pre-load client data
                clients = {c.email: c for c in db.query(Client).all()}
            finally:
                db.close()

            pending_badge.set_text(str(pending_count))
            pending_badge.style("display:none" if pending_count == 0 else "font-size:0.85rem;padding:4px 10px;")

            with list_container:
                if not runs:
                    with ui.element("div").classes("param-card p-10 text-center"):
                        ui.label("No requests yet.").style("color:#6b7280")
                    return

                for run in runs:
                    meta = _meta(run)
                    client = clients.get(run.customer) or next(
                        (c for c in clients.values() if c.name == run.customer), None
                    )
                    label, color, bg = _badge(run.status)

                    with ui.element("div").classes("param-card p-5 mb-4").style(
                        f"border-left: 4px solid {color};"
                    ):
                        with ui.row().classes("items-start justify-between w-full mb-3"):
                            with ui.row().classes("items-center gap-4"):
                                ui.image(_avatar(client)).style(
                                    "width:48px;height:48px;border-radius:50%;object-fit:cover;"
                                    "border:2px solid rgba(139,92,246,0.4)"
                                )
                                with ui.column().classes("gap-0"):
                                    ui.label(run.customer).classes("text-white font-bold").style("font-size:1rem")
                                    ui.label(
                                        run.ran_at.strftime("%d %b %Y  %H:%M") if run.ran_at else "—"
                                    ).style("color:#6b7280;font-size:0.78rem")

                            ui.element("span").style(
                                f"background:{bg};color:{color};border:1px solid {color};"
                                "border-radius:99px;padding:4px 14px;font-size:0.78rem;font-weight:700;"
                                "letter-spacing:0.06em;flex-shrink:0;"
                            ).text = label

                        # Parameters
                        with ui.row().classes("flex-wrap gap-2 mb-3"):
                            for k, v in [
                                ("Platform",    meta.get("platform")),
                                ("Format",      meta.get("format")),
                                ("Content",     meta.get("content_type")),
                                ("Scenery",     meta.get("scenery")),
                                ("Outfit",      meta.get("outfit")),
                                ("Lighting",    meta.get("lighting")),
                                ("Perspective", meta.get("perspective")),
                            ]:
                                if v:
                                    ui.badge(f"{k}: {v}").props("color=blue-9 text-color=white")

                        # Client reference photo count
                        if client:
                            db2 = SessionLocal()
                            try:
                                face_n  = db2.query(ClientPhoto).filter_by(client_id=client.id, category="face").count()
                                body_n  = db2.query(ClientPhoto).filter_by(client_id=client.id, category="body").count()
                                style_n = db2.query(ClientPhoto).filter_by(client_id=client.id, category="style").count()
                            finally:
                                db2.close()
                            ui.label(
                                f"📸 {face_n} face  ·  👤 {body_n} body  ·  🎨 {style_n} style reference photos"
                            ).style("color:#6b7280;font-size:0.78rem;margin-bottom:0.6rem")

                        # Operator notes
                        if run.operator_notes:
                            ui.label(f"📝 {run.operator_notes}").style(
                                "color:#9ca3af;font-size:0.8rem;font-style:italic;margin-bottom:0.5rem"
                            )

                        # Action buttons
                        with ui.row().classes("gap-3 mt-2 items-center flex-wrap"):
                            run_id = run.id
                            run_status = run.status

                            if run_status == STATUS_PENDING:
                                def make_start(rid):
                                    def do():
                                        db3 = SessionLocal()
                                        try:
                                            set_status(db3, rid, STATUS_IN_PROGRESS)
                                        finally:
                                            db3.close()
                                        refresh()
                                        ui.notify("Marked as In Progress", type="info", position="top")
                                    return do
                                ui.button("⚙️  Start", on_click=make_start(run_id)).props("unelevated color=amber-8 dense")

                            if run_status in (STATUS_PENDING, STATUS_IN_PROGRESS):
                                notes_inp = ui.input(placeholder="Operator notes (optional)").props(
                                    "outlined dark dense color=blue-4"
                                ).style("min-width:220px")

                                def make_done(rid, ni):
                                    def do():
                                        db4 = SessionLocal()
                                        try:
                                            set_status(db4, rid, STATUS_DONE, operator_notes=ni.value or None)
                                        finally:
                                            db4.close()
                                        refresh()
                                        ui.notify("Marked as Done", type="positive", position="top")
                                    return do
                                ui.button("✅  Mark Done", on_click=make_done(run_id, notes_inp)).props("unelevated color=green-8 dense")

                            # Upload output file
                            output_holder = {"path": run.output_file}

                            def make_output_upload(rid):
                                def handle(e: events.UploadEventArguments):
                                    ext = Path(e.name).suffix or ".mp4"
                                    dest = OUTPUTS_DIR / f"output_{rid}_{uuid.uuid4().hex[:6]}{ext}"
                                    dest.write_bytes(e.content.read())
                                    db5 = SessionLocal()
                                    try:
                                        set_output(db5, rid, str(dest))
                                    finally:
                                        db5.close()
                                    refresh()
                                    ui.notify("Output uploaded — customer can now download it ✓", type="positive", position="top")
                                return handle

                            ui.upload(
                                on_upload=make_output_upload(run_id),
                                label="📤  Upload Output",
                                max_file_size=500_000_000,
                                auto_upload=True,
                            ).props("flat color=blue-4 dense").style("max-width:180px")

                            if run.output_file and Path(run.output_file).exists():
                                ui.label("✓ Output ready for customer").style("color:#10b981;font-size:0.8rem")

        refresh()
