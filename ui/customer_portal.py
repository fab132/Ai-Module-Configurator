import uuid
import json
from pathlib import Path
from nicegui import ui, app, events
from models.database import SessionLocal
from models.entities import RunLog, Client, ClientPhoto
from services import profile_service, client_service

PICS_DIR = Path("data/profile_pics")
COVERS_DIR = Path("data/profile_covers")
REFS_DIR = Path("data/client_refs")
CLIENT_PICS_DIR = Path("data/client_pics")
for d in [PICS_DIR, COVERS_DIR, REFS_DIR, CLIENT_PICS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

AVATAR_PLACEHOLDER = "https://ui-avatars.com/api/?background=7c3aed&color=fff&size=256&bold=true&name="
COVER_GRADIENT = "linear-gradient(135deg, #12022f 0%, #1e1b4b 45%, #4c1d95 100%)"

PHOTO_CATEGORIES = [
    ("face",  "📸  Face Reference",  "Front face, 3/4 angle, profile — essential for face consistency"),
    ("body",  "👤  Body Reference",  "Full body, half body shots — used for pose and outfit generation"),
    ("style", "🎨  Style Reference", "Outfit inspiration, mood boards — defines your aesthetic"),
]

PORTAL_CSS = """
    body, .q-page { background: #0a0a14 !important; }
    .param-card {
        background: linear-gradient(135deg, #13132b 0%, #1a1a35 100%);
        border: 1px solid rgba(139,92,246,0.25);
        border-radius: 18px;
        transition: all 0.2s ease;
    }
    .aivp-header {
        background: linear-gradient(135deg, #12022f 0%, #0a0a14 100%);
        border-bottom: 1px solid rgba(139,92,246,0.25);
    }
    .cover-wrap { position: relative; }
    .avatar-ring {
        position: absolute; bottom: -52px; left: 40px;
        width: 108px; height: 108px; border-radius: 50%;
        border: 4px solid #0a0a14; overflow: hidden;
        box-shadow: 0 0 0 3px rgba(139,92,246,0.55), 0 8px 28px rgba(124,58,237,0.35);
        background: #1a1a35;
    }
    .photo-thumb {
        position: relative; border-radius: 12px; overflow: hidden;
        border: 1px solid rgba(139,92,246,0.2); transition: all 0.2s;
    }
    .photo-thumb:hover { border-color: rgba(139,92,246,0.65); }
    .photo-del {
        position: absolute; top: 4px; right: 4px;
        background: rgba(239,68,68,0.85); border-radius: 6px;
        padding: 2px 7px; font-size: 0.72rem; color: white;
        cursor: pointer; opacity: 0; transition: opacity 0.2s;
    }
    .photo-thumb:hover .photo-del { opacity: 1; }
    .q-tab--active .q-tab__label { color: #a78bfa !important; font-size: 0.95rem !important; }
    .q-tab__label { font-size: 0.95rem !important; }
    .q-tabs__content, .q-tab-panels { background: transparent !important; }
"""


def _avatar_url(profile, email, client=None) -> str:
    if client and client.profile_picture and Path(client.profile_picture).exists():
        return f"/client_pics/{Path(client.profile_picture).name}"
    if profile and profile.profile_picture and Path(profile.profile_picture).exists():
        return f"/profile_pics/{Path(profile.profile_picture).name}"
    name = (client.name if client else None) or (profile.full_name if profile else None) or email
    return AVATAR_PLACEHOLDER + "+".join(name.split()[:2])


def _cover_style(profile) -> str:
    if profile and profile.cover_picture and Path(profile.cover_picture).exists():
        url = f"/profile_covers/{Path(profile.cover_picture).name}"
        return f"width:100%;height:220px;background-image:url('{url}');background-size:cover;background-position:center;"
    return f"width:100%;height:220px;background:{COVER_GRADIENT};"


def create_customer_portal():
    @ui.page("/customer")
    def customer():
        email = app.storage.user.get("email", "")
        if not app.storage.user.get("authenticated"):
            ui.navigate.to("/login")
            return
        if app.storage.user.get("role") not in ("Customer", None):
            # not a customer — shouldn't be here
            pass

        ui.dark_mode().enable()
        ui.add_css(PORTAL_CSS)

        # ── Header ──────────────────────────────────────────────────────────
        with ui.element("div").classes("aivp-header w-full px-10 py-5"):
            with ui.row().classes("items-center justify-between"):
                with ui.row().classes("items-center gap-4"):
                    ui.label("⚡").style("font-size:2rem")
                    with ui.column().classes("gap-0"):
                        ui.label("AIVP").classes("text-white font-black tracking-widest").style("font-size:1.6rem")
                        ui.label("Customer Portal").style("color:#a78bfa; font-size:0.8rem; letter-spacing:0.18em")
                def logout():
                    app.storage.user['authenticated'] = False
                    ui.navigate.to("/login")
                ui.button("Sign out", on_click=logout).props("flat color=grey-5 dense")

        # Load data
        db = SessionLocal()
        try:
            profile = profile_service.get_or_create(db, email) if email else None
            client = db.query(Client).filter(Client.email == email).first()
        finally:
            db.close()

        # ── Cover + Avatar ───────────────────────────────────────────────────
        cover_container = ui.element("div").classes("cover-wrap")

        def render_cover():
            cover_container.clear()
            db2 = SessionLocal()
            try:
                p = profile_service.get_or_create(db2, email) if email else None
                c = db2.query(Client).filter(Client.email == email).first()
            finally:
                db2.close()
            with cover_container:
                ui.element("div").style(_cover_style(p))
                with ui.element("div").style(
                    "position:absolute;bottom:0;left:0;right:0;height:70px;"
                    "background:linear-gradient(to top,#0a0a14 0%,transparent 100%);"
                ):
                    pass
                with ui.element("div").classes("avatar-ring"):
                    ui.image(_avatar_url(p, email, c)).style("width:100%;height:100%;object-fit:cover;")

        render_cover()

        # ── Name + badge ─────────────────────────────────────────────────────
        info_container = ui.element("div").classes("px-10").style("padding-top:66px")

        def render_info():
            info_container.clear()
            db3 = SessionLocal()
            try:
                p = profile_service.get_or_create(db3, email) if email else None
                c = db3.query(Client).filter(Client.email == email).first()
            finally:
                db3.close()
            display_name = (c.name if c else None) or (p.full_name if p else None) or email
            with info_container:
                with ui.row().classes("items-center gap-3"):
                    ui.label(display_name).classes("text-white font-black").style("font-size:1.6rem")
                    ui.element("span").style(
                        "background:#7c3aed;color:white;font-size:0.72rem;font-weight:700;"
                        "padding:3px 12px;border-radius:99px;letter-spacing:0.06em"
                    ).text = "Customer"
                ui.label(f"@{email}").style("color:#6b7280;font-size:0.85rem;margin-top:2px")

        render_info()

        # ── Tabs ─────────────────────────────────────────────────────────────
        with ui.tabs().classes("w-full mt-6").props("dense align=left") as tabs:
            tab_request = ui.tab("⚡   Request Production").props("no-caps")
            tab_profile = ui.tab("🪪   My Profile").props("no-caps")
            tab_photos  = ui.tab("📸   My Photos").props("no-caps")
            tab_history = ui.tab("🎬   My Productions").props("no-caps")

        with ui.tab_panels(tabs, value=tab_request).classes("w-full"):

            # ── REQUEST PRODUCTION ────────────────────────────────────────────
            with ui.tab_panel(tab_request):
                with ui.element("div").classes("p-8 w-full max-w-4xl mx-auto"):
                    ui.label("Request a Production").classes("text-white font-bold mb-1").style("font-size:1.2rem")
                    ui.label("Choose your preferences below and submit — our team will produce your content.").style(
                        "color:#6b7280; font-size:0.86rem; margin-bottom:2rem"
                    )

                    from services.config_loader import get_options
                    db_r = SessionLocal()
                    try:
                        client_r = db_r.query(Client).filter(Client.email == email).first()
                        client_name = client_r.name if client_r else email
                    finally:
                        db_r.close()

                    REQUEST_PARAMS = [
                        ("content_type", "Content Type", "🎬"),
                        ("platform",     "Platform",     "📱"),
                        ("format",       "Format",       "📐"),
                        ("scenery",      "Scenery",      "🏙️"),
                        ("outfit",       "Outfit",       "👗"),
                        ("lighting",     "Lighting",     "💡"),
                        ("perspective",  "Perspective",  "🎯"),
                    ]

                    sel = {}

                    with ui.element("div").style(
                        "display:grid; grid-template-columns:repeat(auto-fill, minmax(220px,1fr)); gap:1.2rem; margin-bottom:1.5rem"
                    ):
                        # Person card — pre-filled, read-only
                        with ui.element("div").classes("param-card p-5 flex flex-col gap-2"):
                            ui.label("👤  Person").style("color:#a78bfa; font-size:0.8rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase")
                            with ui.row().classes("items-center gap-2"):
                                ui.label(client_name).classes("text-white font-semibold").style("font-size:0.95rem")
                                ui.badge("You").props("color=deep-purple-9 text-color=white")

                        for key, label, icon in REQUEST_PARAMS:
                            options = get_options(key)
                            with ui.element("div").classes("param-card p-5 flex flex-col gap-2"):
                                ui.label(f"{icon}  {label}").style(
                                    "color:#a78bfa; font-size:0.8rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase"
                                )
                                s = ui.select(
                                    options=options, label="Select...", with_input=True
                                ).classes("w-full").props("outlined dark dense color=deep-purple-3")
                                sel[key] = s

                    # Notes field
                    with ui.element("div").classes("param-card p-5 mb-6"):
                        ui.label("📝  Additional Notes").style(
                            "color:#a78bfa; font-size:0.8rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.5rem; display:block"
                        )
                        notes_input = ui.textarea(
                            placeholder="Any specific instructions, preferences, or details for the production team..."
                        ).classes("w-full").props("outlined dark dense color=deep-purple-3 rows=3")

                    submit_err = ui.label("").style("color:#f87171; font-size:0.85rem; min-height:1rem")

                    def submit_request():
                        missing = [label for key, label, _ in REQUEST_PARAMS if not sel[key].value]
                        if missing:
                            submit_err.set_text(f"Please select: {', '.join(missing)}")
                            return
                        submit_err.set_text("")
                        params = {key: sel[key].value for key, _, _ in REQUEST_PARAMS}
                        params["person"] = client_name

                        from services.configurator import run as cfg_run
                        db_s = SessionLocal()
                        try:
                            cfg_run(db_s, params=params, customer=client_name,
                                    combo_name=notes_input.value or None, send_to_api=False)
                            # Reset dropdowns
                            for s in sel.values():
                                s.set_value(None)
                            notes_input.set_value("")
                            ui.notify("✅ Production request submitted! Our team will get started soon.", type="positive", position="top", timeout=5000)
                        except Exception as ex:
                            submit_err.set_text(f"Error: {ex}")
                        finally:
                            db_s.close()

                    with ui.row().classes("justify-center mt-2"):
                        ui.button("⚡  Submit Request", on_click=submit_request).props(
                            "unelevated color=deep-purple"
                        ).style(
                            "font-size:1.1rem; padding:0.9rem 4rem; border-radius:14px; letter-spacing:0.12em; font-weight:700"
                        )

            # ── MY PROFILE ────────────────────────────────────────────────────
            with ui.tab_panel(tab_profile):
                profile_panel = ui.element("div").classes("p-8 w-full max-w-xl mx-auto")

                def render_profile_panel():
                    profile_panel.clear()
                    db4 = SessionLocal()
                    try:
                        p = profile_service.get_or_create(db4, email) if email else None
                        c = db4.query(Client).filter(Client.email == email).first()
                    finally:
                        db4.close()
                    with profile_panel:
                        with ui.element("div").classes("param-card p-6"):
                            ui.label("Personal Info").classes("text-white font-bold mb-5 block").style(
                                "font-size:1rem; text-transform:uppercase; letter-spacing:0.06em"
                            )
                            f_name  = ui.input("Your Name", value=c.name if c else "").classes("w-full").props("outlined dark dense color=deep-purple-3")
                            f_bio   = ui.textarea("About Me", value=p.bio if p else "").classes("w-full mt-4").props("outlined dark dense color=deep-purple-3 rows=3")
                            f_notes = ui.textarea("Special Notes for Production", value=c.notes if c else "").classes("w-full mt-4").props(
                                "outlined dark dense color=deep-purple-3 rows=2"
                            )
                            ui.label("e.g. allergies, preferred styles, restrictions").style("color:#6b7280;font-size:0.75rem;margin-top:-0.3rem")

                            ui.label("Profile Photo").classes("text-white text-sm mt-5 mb-2 block font-semibold")
                            pic_holder = {"path": None}

                            def handle_pic(e: events.UploadEventArguments):
                                ext = Path(e.name).suffix or ".jpg"
                                dest = CLIENT_PICS_DIR / f"{uuid.uuid4().hex}{ext}"
                                dest.write_bytes(e.content.read())
                                pic_holder["path"] = str(dest)
                                ui.notify("Photo uploaded ✓", type="positive", position="top")

                            ui.upload(
                                on_upload=handle_pic, label="Upload profile photo",
                                max_file_size=5_000_000, auto_upload=True
                            ).props("accept=image/* flat color=deep-purple-3").classes("w-full")

                            ui.label("Cover Photo").classes("text-white text-sm mt-4 mb-2 block font-semibold")
                            cover_holder = {"path": None}

                            def handle_cover(e: events.UploadEventArguments):
                                ext = Path(e.name).suffix or ".jpg"
                                dest = COVERS_DIR / f"cover_{uuid.uuid4().hex}{ext}"
                                dest.write_bytes(e.content.read())
                                cover_holder["path"] = str(dest)
                                ui.notify("Cover uploaded ✓", type="positive", position="top")

                            ui.upload(
                                on_upload=handle_cover, label="Upload cover photo",
                                max_file_size=8_000_000, auto_upload=True
                            ).props("accept=image/* flat color=deep-purple-3").classes("w-full")

                            err = ui.label("").style("color:#f87171;font-size:0.82rem;min-height:1rem;margin-top:0.3rem")

                            def save_profile():
                                db5 = SessionLocal()
                                try:
                                    profile_service.update(
                                        db5, email,
                                        full_name=f_name.value,
                                        bio=f_bio.value,
                                        profile_picture=pic_holder["path"],
                                        cover_picture=cover_holder["path"],
                                    )
                                    c2 = db5.query(Client).filter(Client.email == email).first()
                                    if c2:
                                        client_service.update(
                                            db5, c2.id,
                                            name=f_name.value or c2.name,
                                            notes=f_notes.value or None,
                                            profile_picture=pic_holder["path"],
                                        )
                                    ui.notify("Profile saved!", type="positive", position="top")
                                    render_cover()
                                    render_info()
                                    render_profile_panel()
                                except Exception as ex:
                                    err.set_text(str(ex))
                                finally:
                                    db5.close()

                            ui.button("💾  Save Profile", on_click=save_profile).classes("w-full mt-5").props("unelevated color=deep-purple")

                render_profile_panel()

            # ── MY PHOTOS ─────────────────────────────────────────────────────
            with ui.tab_panel(tab_photos):
                photos_panel = ui.element("div").classes("p-8 w-full max-w-5xl mx-auto")

                def render_photos():
                    photos_panel.clear()
                    db6 = SessionLocal()
                    try:
                        c = db6.query(Client).filter(Client.email == email).first()
                        if not c:
                            with photos_panel:
                                ui.label("Your client profile is being set up. Check back soon.").style("color:#6b7280")
                            return
                        cat_data = {cat: client_service.get_photos(db6, c.id, cat) for cat, _, _ in PHOTO_CATEGORIES}
                        client_id = c.id
                    finally:
                        db6.close()

                    with photos_panel:
                        ui.label("Your Reference Photos").classes("text-white font-bold mb-2").style("font-size:1.2rem")
                        ui.label(
                            "These photos are used by our production team to create your personalised avatar and visual content. "
                            "Upload at least 5 face photos and 3 body photos for best results."
                        ).style("color:#6b7280;font-size:0.86rem;margin-bottom:1.5rem;line-height:1.5")

                        with ui.row().classes("gap-6 w-full items-start").style("flex-wrap:wrap"):
                            for cat_key, cat_label, cat_tip in PHOTO_CATEGORIES:
                                photos = cat_data[cat_key]
                                with ui.element("div").classes("param-card p-5").style("min-width:260px; flex:1"):
                                    with ui.row().classes("items-center justify-between mb-1"):
                                        ui.label(cat_label).classes("text-white font-semibold").style("font-size:0.95rem")
                                        ui.badge(str(len(photos))).props("color=deep-purple-9 text-color=white")
                                    ui.label(cat_tip).style("color:#6b7280;font-size:0.75rem;margin-bottom:1rem;line-height:1.4")

                                    if photos:
                                        with ui.element("div").style(
                                            "display:grid;grid-template-columns:repeat(auto-fill,minmax(85px,1fr));gap:8px;margin-bottom:12px"
                                        ):
                                            for p in photos:
                                                with ui.element("div").classes("photo-thumb").style("height:85px"):
                                                    ui.image(f"/client_refs/{Path(p.file_path).name}").style(
                                                        "width:100%;height:100%;object-fit:cover;"
                                                    )
                                                    def make_del(pid):
                                                        def do():
                                                            db7 = SessionLocal()
                                                            try:
                                                                client_service.delete_photo(db7, pid)
                                                            finally:
                                                                db7.close()
                                                            render_photos()
                                                        return do
                                                    with ui.element("div").classes("photo-del").on("click", make_del(p.id)):
                                                        ui.label("✕")

                                    def make_uploader(category, cid):
                                        def handle(e: events.UploadEventArguments):
                                            ext = Path(e.name).suffix or ".jpg"
                                            dest = REFS_DIR / f"ref_{uuid.uuid4().hex}{ext}"
                                            dest.write_bytes(e.content.read())
                                            db8 = SessionLocal()
                                            try:
                                                client_service.add_photo(db8, cid, str(dest), category)
                                            finally:
                                                db8.close()
                                            ui.notify("Photo added ✓", type="positive", position="top")
                                            render_photos()
                                        return handle

                                    ui.upload(
                                        on_upload=make_uploader(cat_key, client_id),
                                        label="+ Upload photos",
                                        max_file_size=8_000_000,
                                        auto_upload=True,
                                        multiple=True,
                                    ).props("accept=image/* flat color=deep-purple-3").classes("w-full")

                render_photos()

            # ── MY PRODUCTIONS ────────────────────────────────────────────────
            with ui.tab_panel(tab_history):
                with ui.element("div").classes("p-8 w-full max-w-4xl mx-auto"):
                    ui.label("My Productions").classes("text-white font-bold mb-2").style("font-size:1.2rem")
                    ui.label("Visual content produced for you by our team.").style("color:#6b7280;font-size:0.86rem;margin-bottom:1.5rem")

                    prod_container = ui.element("div").classes("w-full")

                    def load_productions():
                        prod_container.clear()
                        db9 = SessionLocal()
                        try:
                            c = db9.query(Client).filter(Client.email == email).first()
                            if not c:
                                with prod_container:
                                    ui.label("No productions yet.").style("color:#6b7280")
                                return
                            logs = db9.query(RunLog).filter(RunLog.customer == c.name).order_by(RunLog.ran_at.desc()).all()
                        finally:
                            db9.close()

                        with prod_container:
                            if not logs:
                                with ui.element("div").classes("param-card p-8 text-center"):
                                    ui.label("🎬").style("font-size:2.5rem")
                                    ui.label("No productions yet").classes("text-white font-semibold mt-2")
                                    ui.label("Once our team produces content for you, it will appear here.").style("color:#6b7280;font-size:0.86rem;margin-top:4px")
                                return

                            for log in logs:
                                try:
                                    meta = json.loads(log.config_json).get("_meta", {})
                                except Exception:
                                    meta = {}
                                with ui.element("div").classes("param-card p-5 mb-3"):
                                    with ui.row().classes("items-center justify-between"):
                                        with ui.row().classes("gap-3 flex-wrap"):
                                            for k, v in [
                                                ("Platform", meta.get("platform")),
                                                ("Format",   meta.get("format")),
                                                ("Scenery",  meta.get("scenery")),
                                                ("Outfit",   meta.get("outfit")),
                                                ("Lighting", meta.get("lighting")),
                                            ]:
                                                if v:
                                                    ui.badge(f"{k}: {v}").props("color=deep-purple-9 text-color=white")
                                        ui.label(
                                            log.ran_at.strftime("%d %b %Y  %H:%M") if log.ran_at else "—"
                                        ).style("color:#6b7280;font-size:0.8rem;flex-shrink:0")

                    load_productions()
