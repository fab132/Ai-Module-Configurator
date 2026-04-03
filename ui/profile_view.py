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

AVATAR_PLACEHOLDER = "https://ui-avatars.com/api/?background=7c3aed&color=fff&size=256&bold=true&name="
COVER_GRADIENT = "linear-gradient(135deg, #12022f 0%, #1e1b4b 45%, #4c1d95 100%)"

ROLE_COLORS = {"Admin": "#dc2626", "Operator": "#7c3aed"}

PROFILE_CSS = """
    .profile-cover-wrap { position: relative; }
    .profile-cover-img  { width:100%; height:240px; object-fit:cover; display:block; }
    .profile-cover-overlay {
        position:absolute; bottom:0; left:0; right:0; height:80px;
        background: linear-gradient(to top, #0a0a14 0%, transparent 100%);
    }
    .profile-avatar-ring {
        position:absolute; bottom:-54px; left:48px;
        width:112px; height:112px; border-radius:50%;
        border:4px solid #0a0a14;
        box-shadow: 0 0 0 3px rgba(139,92,246,0.6), 0 8px 32px rgba(124,58,237,0.4);
        overflow:hidden; background:#1a1a35;
    }
    .stat-card {
        background: linear-gradient(135deg, #13132b 0%, #1a1a35 100%);
        border: 1px solid rgba(139,92,246,0.25);
        border-radius:16px; padding:1.2rem 2rem;
        text-align:center; min-width:120px;
        transition: all 0.2s ease;
    }
    .stat-card:hover {
        border-color: rgba(139,92,246,0.6);
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(124,58,237,0.2);
    }
    .about-row { display:flex; align-items:center; gap:12px; margin-bottom:14px; }
    .about-icon { font-size:1rem; width:22px; text-align:center; flex-shrink:0; }
    .about-label { color:#6b7280; font-size:0.82rem; width:110px; flex-shrink:0; }
    .about-value { color:#e5e7eb; font-size:0.86rem; }
    .edit-cover-btn {
        position:absolute; top:14px; right:14px;
        background:rgba(0,0,0,0.55); border:1px solid rgba(255,255,255,0.15);
        border-radius:10px; padding:5px 14px; cursor:pointer;
        color:white; font-size:0.82rem; display:flex; align-items:center; gap:6px;
        backdrop-filter: blur(4px);
    }
    .recent-run-row {
        display:flex; align-items:center; justify-content:space-between;
        padding:10px 0; border-bottom:1px solid rgba(139,92,246,0.1);
    }
    .recent-run-row:last-child { border-bottom: none; }
"""


def _avatar_url(profile, email: str) -> str:
    if profile and profile.profile_picture and Path(profile.profile_picture).exists():
        return f"/profile_pics/{Path(profile.profile_picture).name}"
    name = (profile.full_name if profile and profile.full_name else email) or "U"
    initials = "+".join(name.split()[:2])
    return AVATAR_PLACEHOLDER + initials


def _cover_style(profile) -> str:
    if profile and profile.cover_picture and Path(profile.cover_picture).exists():
        url = f"/profile_covers/{Path(profile.cover_picture).name}"
        return (
            f"width:100%; height:240px; background-image:url('{url}');"
            "background-size:cover; background-position:center;"
        )
    return f"width:100%; height:240px; background:{COVER_GRADIENT};"


def _get_stats(db, email: str) -> dict:
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


def _get_recent_runs(db, limit=5) -> list:
    return db.query(RunLog).order_by(RunLog.ran_at.desc()).limit(limit).all()


def create_profile_view():
    email = app.storage.user.get("email", "")
    ui.add_css(PROFILE_CSS)
    container = ui.element("div").classes("w-full")

    def render():
        container.clear()
        db = SessionLocal()
        try:
            profile = profile_service.get_or_create(db, email) if email else None
            stats = _get_stats(db, email)
            recent_runs = _get_recent_runs(db)
            from models.entities import User as UserModel
            user_obj = db.query(UserModel).filter_by(email=email).first()
            member_since = user_obj.created_at.strftime("%B %Y") if user_obj and user_obj.created_at else "—"
        finally:
            db.close()

        display_name = (profile.full_name if profile and profile.full_name else "").strip() or email
        role = profile.role if profile else "Operator"
        role_color = ROLE_COLORS.get(role, "#7c3aed")

        with container:
            # ── Cover ────────────────────────────────────────────────────────
            with ui.element("div").classes("profile-cover-wrap"):
                ui.element("div").style(_cover_style(profile))
                ui.element("div").classes("profile-cover-overlay")

                # Edit cover upload
                with ui.element("div").classes("edit-cover-btn"):
                    def handle_cover(e: events.UploadEventArguments):
                        ext = Path(e.name).suffix or ".jpg"
                        dest = COVERS_DIR / f"cover_{uuid.uuid4().hex}{ext}"
                        dest.write_bytes(e.content.read())
                        db2 = SessionLocal()
                        try:
                            profile_service.update(db2, email, cover_picture=str(dest))
                        finally:
                            db2.close()
                        render()
                    ui.label("📷  Edit Cover").style("pointer-events:none; color:white")
                    ui.upload(
                        on_upload=handle_cover, max_file_size=8_000_000, auto_upload=True
                    ).props("accept=image/* flat dense").style(
                        "position:absolute; inset:0; opacity:0; cursor:pointer;"
                    )

                # Avatar
                with ui.element("div").classes("profile-avatar-ring"):
                    ui.image(_avatar_url(profile, email)).style(
                        "width:100%; height:100%; object-fit:cover;"
                    )

            # ── Name / bio / edit ────────────────────────────────────────────
            with ui.element("div").classes("px-12").style("padding-top:70px"):
                with ui.row().classes("items-start justify-between w-full"):
                    with ui.column().classes("gap-1"):
                        with ui.row().classes("items-center gap-3"):
                            ui.label(display_name).classes("text-white font-black").style("font-size:1.75rem")
                            ui.element("span").style(
                                f"background:{role_color}; color:white; font-size:0.72rem; font-weight:700;"
                                "padding:3px 12px; border-radius:99px; letter-spacing:0.06em"
                            ).text = role

                        ui.label(f"@{email}").style("color:#6b7280; font-size:0.86rem")

                        if profile and profile.bio:
                            ui.label(profile.bio).style(
                                "color:#9ca3af; font-size:0.9rem; max-width:500px; line-height:1.6; margin-top:6px"
                            )

                    ui.button("✏️  Edit Profile", on_click=open_edit_dialog).props(
                        "outlined color=deep-purple-3"
                    ).style("margin-top:6px; flex-shrink:0")

            # ── Stats ────────────────────────────────────────────────────────
            with ui.row().classes("gap-5 px-12 mt-8"):
                for value, label, icon in [
                    (stats["runs"],      "Total Runs",    "🎬"),
                    (stats["templates"], "Templates",     "📁"),
                    (stats["clients"],   "Clients",       "👤"),
                ]:
                    with ui.element("div").classes("stat-card"):
                        ui.label(str(value)).classes("text-white font-black").style("font-size:2rem; line-height:1")
                        ui.label(f"{icon}  {label}").style(
                            "color:#a78bfa; font-size:0.78rem; letter-spacing:0.08em; margin-top:6px"
                        )

            # ── Two-column layout: About + Recent Activity ───────────────────
            with ui.row().classes("px-12 mt-8 mb-12 gap-6 w-full items-start").style("flex-wrap:wrap"):

                # About card
                with ui.element("div").classes("param-card p-6").style("min-width:280px; flex:1"):
                    ui.label("About").classes("text-white font-bold mb-5 block").style(
                        "font-size:1rem; letter-spacing:0.06em; text-transform:uppercase"
                    )
                    for icon, label, value in [
                        ("📧", "Email",        email),
                        ("🗓️", "Member since", member_since),
                        ("🎭", "Role",         role),
                        ("⚡", "Platform",     "AIVP – AI Visual Production"),
                    ]:
                        with ui.element("div").classes("about-row"):
                            ui.label(icon).classes("about-icon")
                            ui.label(label).classes("about-label")
                            ui.label(value or "—").classes("about-value")

                # Recent activity card
                with ui.element("div").classes("param-card p-6").style("min-width:300px; flex:2"):
                    ui.label("Recent Activity").classes("text-white font-bold mb-4 block").style(
                        "font-size:1rem; letter-spacing:0.06em; text-transform:uppercase"
                    )
                    if not recent_runs:
                        ui.label("No runs yet — start by configuring a run.").style("color:#6b7280; font-size:0.88rem")
                    else:
                        for run in recent_runs:
                            try:
                                meta = json.loads(run.config_json).get("_meta", {})
                            except Exception:
                                meta = {}
                            with ui.element("div").classes("recent-run-row"):
                                with ui.column().classes("gap-0"):
                                    ui.label(
                                        f"{meta.get('person', '—')}  ·  {meta.get('platform', '—')}  ·  {meta.get('format', '—')}"
                                    ).style("color:#e5e7eb; font-size:0.86rem")
                                    ui.label(run.customer).style("color:#6b7280; font-size:0.78rem")
                                ui.label(
                                    run.ran_at.strftime("%d %b %Y %H:%M") if run.ran_at else "—"
                                ).style("color:#6b7280; font-size:0.78rem; flex-shrink:0")

    def open_edit_dialog():
        db = SessionLocal()
        try:
            profile = profile_service.get_or_create(db, email) if email else None
        finally:
            db.close()

        with ui.dialog() as dlg, ui.card().classes("w-full p-6").style(
            "background:#13132b; border:1px solid rgba(139,92,246,0.3);"
            "max-width:460px; max-height:90vh; overflow-y:auto;"
        ):
            ui.label("Edit Profile").classes("text-white font-bold mb-5").style("font-size:1.2rem")

            f_name = ui.input(
                "Full Name", value=profile.full_name if profile else ""
            ).classes("w-full").props("outlined dark dense color=deep-purple-3")

            f_bio = ui.textarea(
                "Bio", value=profile.bio if profile else ""
            ).classes("w-full mt-4").props("outlined dark dense color=deep-purple-3 rows=3")
            ui.label("Tell people about yourself and your role in the team.").style(
                "color:#6b7280; font-size:0.75rem; margin-top:-0.4rem"
            )

            f_role = ui.select(
                options=["Operator", "Admin"],
                label="Role",
                value=profile.role if profile else "Operator",
            ).classes("w-full mt-4").props("outlined dark dense color=deep-purple-3")

            ui.label("Profile Picture").classes("text-white text-sm mt-5 mb-2 block font-semibold")
            pic_holder = {"path": None}

            def handle_pic(e: events.UploadEventArguments):
                ext = Path(e.name).suffix or ".jpg"
                dest = PICS_DIR / f"avatar_{uuid.uuid4().hex}{ext}"
                dest.write_bytes(e.content.read())
                pic_holder["path"] = str(dest)
                ui.notify("Photo uploaded ✓", type="positive", position="top")

            ui.upload(
                on_upload=handle_pic, label="Upload profile photo",
                max_file_size=5_000_000, auto_upload=True,
            ).props("accept=image/* flat color=deep-purple-3").classes("w-full")

            err = ui.label("").style("color:#f87171; font-size:0.82rem; min-height:1rem; margin-top:4px")

            def save():
                db3 = SessionLocal()
                try:
                    profile_service.update(
                        db3, email,
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
                    db3.close()

            with ui.row().classes("mt-6 justify-end gap-3"):
                ui.button("Cancel", on_click=dlg.close).props("flat color=grey")
                ui.button("Save Changes", on_click=save).props("unelevated color=deep-purple")

        dlg.open()

    render()
