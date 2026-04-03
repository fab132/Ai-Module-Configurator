import uuid
import json
from pathlib import Path
from nicegui import ui, app, events
from models.database import SessionLocal
from models.entities import RunLog, Client
from services import profile_service

PICS_DIR = Path("data/profile_pics")
COVERS_DIR = Path("data/profile_covers")
PICS_DIR.mkdir(parents=True, exist_ok=True)
COVERS_DIR.mkdir(parents=True, exist_ok=True)

AVATAR_PLACEHOLDER = "https://ui-avatars.com/api/?background=7c3aed&color=fff&size=128&bold=true&name="
COVER_GRADIENT = "linear-gradient(135deg, #12022f 0%, #1e1b4b 40%, #4c1d95 100%)"


def _avatar_url(profile, email: str) -> str:
    if profile and profile.profile_picture and Path(profile.profile_picture).exists():
        return f"/profile_pics/{Path(profile.profile_picture).name}"
    initials = "+".join((profile.full_name if profile and profile.full_name else email).split()[:2])
    return AVATAR_PLACEHOLDER + initials


def _cover_url(profile) -> str:
    if profile and profile.cover_picture and Path(profile.cover_picture).exists():
        return f"/profile_covers/{Path(profile.cover_picture).name}"
    return ""


def _get_stats(db) -> dict:
    runs = db.query(RunLog).count()
    clients = db.query(Client).count()
    templates = 0
    try:
        tf = Path("data/templates.json")
        if tf.exists():
            templates = len(json.loads(tf.read_text()))
    except Exception:
        pass
    return {"runs": runs, "clients": clients, "templates": templates}


def create_profile_view():
    email = app.storage.user.get("email", "")
    container = ui.element("div").classes("w-full")

    def render():
        container.clear()
        db = SessionLocal()
        try:
            profile = profile_service.get_or_create(db, email) if email else None
            stats = _get_stats(db)
            user_obj = db.query(__import__("models.entities", fromlist=["User"]).User).filter_by(email=email).first()
            member_since = user_obj.created_at.strftime("%B %Y") if user_obj and user_obj.created_at else "—"
        finally:
            db.close()

        with container:
            # ── Cover + Avatar ───────────────────────────────────────────────
            cover_url = _cover_url(profile)
            cover_style = (
                f"width:100%; height:230px; background-image:url('{cover_url}'); "
                f"background-size:cover; background-position:center; "
                f"background-color:transparent; position:relative; "
                f"background: {COVER_GRADIENT};"
            ) if not cover_url else (
                f"width:100%; height:230px; background-image:url('{cover_url}'); "
                f"background-size:cover; background-position:center; position:relative;"
            )

            with ui.element("div").style(cover_style):
                # Edit cover button — top right
                def handle_cover_upload(e: events.UploadEventArguments):
                    ext = Path(e.name).suffix or ".jpg"
                    fname = f"cover_{uuid.uuid4().hex}{ext}"
                    dest = COVERS_DIR / fname
                    dest.write_bytes(e.content.read())
                    db2 = SessionLocal()
                    try:
                        profile_service.update(db2, email, cover_picture=str(dest))
                    finally:
                        db2.close()
                    ui.notify("Cover updated", type="positive", position="top")
                    render()

                with ui.element("div").style("position:absolute; top:16px; right:16px;"):
                    with ui.element("div").style(
                        "background:rgba(0,0,0,0.5); border-radius:10px; padding:4px 12px;"
                        "display:flex; align-items:center; gap:6px; cursor:pointer;"
                    ):
                        ui.upload(
                            on_upload=handle_cover_upload,
                            max_file_size=8_000_000,
                            auto_upload=True,
                            label="📷  Edit Cover",
                        ).props("accept=image/* flat dense color=white").style(
                            "color:white; font-size:0.82rem;"
                        )

                # Avatar — bottom-left, overlapping cover
                with ui.element("div").style(
                    "position:absolute; bottom:-52px; left:48px;"
                    "width:108px; height:108px; border-radius:50%;"
                    "border:4px solid #0a0a14; overflow:hidden; background:#1a1a35;"
                ):
                    ui.image(_avatar_url(profile, email)).style(
                        "width:100%; height:100%; object-fit:cover;"
                    )

            # ── Profile info ─────────────────────────────────────────────────
            with ui.element("div").classes("px-12").style("padding-top: 68px"):
                with ui.row().classes("items-start justify-between w-full"):
                    with ui.column().classes("gap-1"):
                        name = (profile.full_name if profile and profile.full_name else "").strip()
                        ui.label(name or email).classes("text-white font-black").style("font-size:1.6rem")

                        role_color = {"Admin": "#ef4444", "Operator": "#7c3aed"}.get(
                            profile.role if profile else "Operator", "#7c3aed"
                        )
                        with ui.row().classes("items-center gap-3 mt-1"):
                            ui.label(f"@{email}").style("color:#6b7280; font-size:0.88rem")
                            ui.badge(profile.role if profile else "Operator").style(
                                f"background:{role_color}; color:white; font-size:0.75rem; padding:2px 10px; border-radius:99px"
                            )

                        if profile and profile.bio:
                            ui.label(profile.bio).classes("mt-2").style(
                                "color:#9ca3af; font-size:0.92rem; max-width:520px; line-height:1.5"
                            )

                    # Edit Profile button
                    ui.button("✏️  Edit Profile", on_click=open_edit_dialog).props(
                        "outlined color=deep-purple-3"
                    ).style("margin-top:4px")

            # ── Stats ────────────────────────────────────────────────────────
            with ui.element("div").classes("px-12 mt-8"):
                with ui.row().classes("gap-6"):
                    for icon, label, value in [
                        ("🎬", "Runs", stats["runs"]),
                        ("📁", "Templates", stats["templates"]),
                        ("👤", "Clients", stats["clients"]),
                    ]:
                        with ui.element("div").classes("param-card px-8 py-5 text-center").style("min-width:130px"):
                            ui.label(str(value)).classes("text-white font-black").style("font-size:1.8rem")
                            ui.label(f"{icon}  {label}").style("color:#a78bfa; font-size:0.82rem; letter-spacing:0.08em")

            # ── About ────────────────────────────────────────────────────────
            with ui.element("div").classes("px-12 mt-8 mb-10"):
                with ui.element("div").classes("param-card p-6").style("max-width:520px"):
                    ui.label("About").classes("text-white font-bold mb-4 block").style("font-size:1rem; letter-spacing:0.05em")
                    for icon, label, value in [
                        ("📧", "Email", email),
                        ("🗓️", "Member since", member_since),
                        ("🎭", "Role", profile.role if profile else "Operator"),
                    ]:
                        with ui.row().classes("items-center gap-3 mb-3"):
                            ui.label(icon).style("font-size:1rem; width:20px; text-align:center")
                            ui.label(label).style("color:#6b7280; font-size:0.85rem; width:100px")
                            ui.label(value or "—").style("color:#e5e7eb; font-size:0.88rem")

    def open_edit_dialog():
        db = SessionLocal()
        try:
            profile = profile_service.get_or_create(db, email) if email else None
        finally:
            db.close()

        with ui.dialog() as dlg, ui.card().classes("w-full p-6").style(
            "background:#13132b; border:1px solid rgba(139,92,246,0.3); "
            "max-width:480px; max-height:90vh; overflow-y:auto"
        ):
            ui.label("Edit Profile").classes("text-white font-bold mb-5").style("font-size:1.2rem")

            f_name = ui.input(
                "Full Name",
                value=profile.full_name if profile else ""
            ).classes("w-full").props("outlined dark dense color=deep-purple-3")

            f_bio = ui.textarea(
                "Bio",
                value=profile.bio if profile else ""
            ).classes("w-full mt-4").props("outlined dark dense color=deep-purple-3 rows=3")

            f_role = ui.select(
                options=["Operator", "Admin"],
                label="Role",
                value=profile.role if profile else "Operator"
            ).classes("w-full mt-4").props("outlined dark dense color=deep-purple-3")

            ui.label("Profile Picture").classes("text-white text-sm mt-5 mb-1 block")
            pic_holder = {"path": None}

            def handle_pic(e: events.UploadEventArguments):
                ext = Path(e.name).suffix or ".jpg"
                fname = f"avatar_{uuid.uuid4().hex}{ext}"
                dest = PICS_DIR / fname
                dest.write_bytes(e.content.read())
                pic_holder["path"] = str(dest)
                ui.notify("Photo uploaded", type="positive", position="top")

            ui.upload(
                on_upload=handle_pic,
                label="Upload photo",
                max_file_size=5_000_000,
                auto_upload=True,
            ).props("accept=image/* flat color=deep-purple-3").classes("w-full")

            err = ui.label("").style("color:#f87171; font-size:0.82rem; min-height:1rem")

            def save():
                db2 = SessionLocal()
                try:
                    profile_service.update(
                        db2, email,
                        full_name=f_name.value,
                        bio=f_bio.value,
                        role=f_role.value,
                        profile_picture=pic_holder["path"],
                    )
                    dlg.close()
                    render()
                    ui.notify("Profile saved!", type="positive", position="top")
                except Exception as ex:
                    err.set_text(str(ex))
                finally:
                    db2.close()

            with ui.row().classes("mt-5 justify-end gap-3"):
                ui.button("Cancel", on_click=dlg.close).props("flat color=grey")
                ui.button("Save", on_click=save).props("unelevated color=deep-purple")

        dlg.open()

    render()
