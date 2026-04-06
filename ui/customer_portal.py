import uuid
import json
from pathlib import Path
from nicegui import ui, app, events
from models.database import SessionLocal
from models.entities import RunLog, Client, ClientPhoto
from services import profile_service, client_service
from ui.shared_styles import (
    SHARED_CSS, AVATAR_PLACEHOLDER, COVER_GRADIENT,
    ACCENT_LOGO, ACCENT_BLUE, TEXT_MUTED, BG_PAGE, BTN_PRIMARY, BTN_SUCCESS
)

PICS_DIR = Path("data/profile_pics")
COVERS_DIR = Path("data/profile_covers")
REFS_DIR = Path("data/client_refs")
CLIENT_PICS_DIR = Path("data/client_pics")
for d in [PICS_DIR, COVERS_DIR, REFS_DIR, CLIENT_PICS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

PHOTO_CATEGORIES = [
    ("face",  "📸  Face Reference",  "Front face, 3/4 angle, profile — essential for face consistency"),
    ("body",  "👤  Body Reference",  "Full body, half body shots — used for pose and outfit generation"),
    ("style", "🎨  Style Reference", "Outfit inspiration, mood boards — defines your aesthetic"),
]


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

        ui.dark_mode().enable()
        ui.add_css(SHARED_CSS)

        # ── Header ──────────────────────────────────────────────────────────
        with ui.element("div").classes("aivp-header w-full px-10 py-5"):
            with ui.row().classes("items-center justify-between"):
                with ui.row().classes("items-center gap-4"):
                    ui.label("⚡").style(f"font-size:2rem; color:{ACCENT_LOGO}")
                    with ui.column().classes("gap-0"):
                        ui.label("AIVP").classes("text-white font-black tracking-widest").style("font-size:1.6rem")
                        ui.label("Customer Portal").style(f"color:{TEXT_MUTED}; font-size:0.8rem; letter-spacing:0.18em")
                def logout():
                    app.storage.user['authenticated'] = False
                    ui.navigate.to("/login")
                ui.button("Sign out", on_click=logout).props("flat color=grey-5 dense")

        # ── Tabs (right after header, same as admin) ─────────────────────────
        with ui.tabs().classes("w-full").props("dense align=left") as tabs:
            tab_profile = ui.tab("🪪   My Profile").props("no-caps")
            tab_request = ui.tab("⚡   Request Production").props("no-caps")
            tab_photos  = ui.tab("📸   My Photos").props("no-caps")
            tab_history = ui.tab("🎬   My Productions").props("no-caps")

        with ui.tab_panels(tabs, value=tab_profile).classes("w-full"):

            # ── REQUEST PRODUCTION ────────────────────────────────────────────
            with ui.tab_panel(tab_request):
                with ui.element("div").classes("p-8 w-full max-w-4xl mx-auto"):
                    ui.label("Request a Production").classes("text-white font-bold mb-1").style("font-size:1.2rem")
                    ui.label("Choose your preferences below and submit — our team will produce your content.").style(
                        f"color:{TEXT_MUTED}; font-size:0.86rem; margin-bottom:2rem"
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
                        with ui.element("div").classes("param-card p-5 flex flex-col gap-2"):
                            ui.label("👤  Person").style(
                                f"color:{ACCENT_BLUE}; font-size:0.8rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase"
                            )
                            with ui.row().classes("items-center gap-2"):
                                ui.label(client_name).classes("text-white font-semibold").style("font-size:0.95rem")
                                ui.badge("You").props("color=blue-9 text-color=white")

                        for key, label, icon in REQUEST_PARAMS:
                            options = get_options(key)
                            with ui.element("div").classes("param-card p-5 flex flex-col gap-2"):
                                ui.label(f"{icon}  {label}").style(
                                    f"color:{ACCENT_BLUE}; font-size:0.8rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase"
                                )
                                s = ui.select(
                                    options=options, label="Select...", with_input=True
                                ).classes("w-full").props("outlined dark dense color=blue-4")
                                sel[key] = s

                    with ui.element("div").classes("param-card p-5 mb-6"):
                        ui.label("📝  Additional Notes").style(
                            f"color:{ACCENT_BLUE}; font-size:0.8rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; margin-bottom:0.5rem; display:block"
                        )
                        notes_input = ui.textarea(
                            placeholder="Any specific instructions, preferences, or details for the production team..."
                        ).classes("w-full").props("outlined dark dense color=blue-4 rows=3")

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
                            for s in sel.values():
                                s.set_value(None)
                            notes_input.set_value("")
                            ui.notify("✅ Production request submitted! Our team will get started soon.", type="positive", position="top", timeout=5000)
                        except Exception as ex:
                            submit_err.set_text(f"Error: {ex}")
                        finally:
                            db_s.close()

                    with ui.row().classes("justify-center mt-2"):
                        ui.button("⚡  Submit Request", on_click=submit_request).props("unelevated").style(
                            f"background:{BTN_PRIMARY};color:white;font-size:1.1rem;padding:0.9rem 4rem;border-radius:14px;letter-spacing:0.12em;font-weight:700"
                        )

            # ── MY PROFILE ────────────────────────────────────────────────────
            with ui.tab_panel(tab_profile):
                profile_panel = ui.element("div").classes("w-full")

                pic_holder   = {"path": None}
                cover_holder = {"path": None}

                def render_profile_panel():
                    profile_panel.clear()
                    db4 = SessionLocal()
                    try:
                        p = profile_service.get_or_create(db4, email) if email else None
                        c = db4.query(Client).filter(Client.email == email).first()
                    finally:
                        db4.close()

                    display_name = (c.name if c else None) or (p.full_name if p else None) or email

                    with profile_panel:
                        # ── Cover photo with overlay "Change Cover" button ──────
                        with ui.element("div").classes("profile-cover-wrap"):
                            ui.element("div").style(_cover_style(p))
                            ui.element("div").classes("profile-cover-overlay")

                            # "Change Cover" button top-right
                            with ui.element("div").classes("edit-cover-btn"):
                                ui.label("📷  Change Cover")
                                cover_upload = ui.upload(
                                    label="",
                                    max_file_size=8_000_000,
                                    auto_upload=True,
                                ).props("accept=image/* flat color=white").style(
                                    "position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%"
                                )
                                def handle_cover(e: events.UploadEventArguments):
                                    ext = Path(e.name).suffix or ".jpg"
                                    dest = COVERS_DIR / f"cover_{uuid.uuid4().hex}{ext}"
                                    dest.write_bytes(e.content.read())
                                    cover_holder["path"] = str(dest)
                                    db_c = SessionLocal()
                                    try:
                                        profile_service.update(db_c, email, cover_picture=str(dest))
                                    finally:
                                        db_c.close()
                                    ui.notify("Cover updated ✓", type="positive", position="top")
                                    render_profile_panel()
                                cover_upload.on_upload(handle_cover)

                            # Avatar with click-to-change
                            with ui.element("div").classes("profile-avatar-ring").style("cursor:pointer").tooltip("Click to change photo"):
                                ui.image(_avatar_url(p, email, c)).style("width:100%;height:100%;object-fit:cover;")
                                avatar_upload = ui.upload(
                                    label="",
                                    max_file_size=5_000_000,
                                    auto_upload=True,
                                ).props("accept=image/* flat").style(
                                    "position:absolute;inset:0;opacity:0;cursor:pointer;width:100%;height:100%"
                                )
                                def handle_pic(e: events.UploadEventArguments):
                                    ext = Path(e.name).suffix or ".jpg"
                                    dest = CLIENT_PICS_DIR / f"{uuid.uuid4().hex}{ext}"
                                    dest.write_bytes(e.content.read())
                                    pic_holder["path"] = str(dest)
                                    db_p2 = SessionLocal()
                                    try:
                                        profile_service.update(db_p2, email, profile_picture=str(dest))
                                        c2 = db_p2.query(Client).filter(Client.email == email).first()
                                        if c2:
                                            client_service.update(db_p2, c2.id, profile_picture=str(dest))
                                    finally:
                                        db_p2.close()
                                    ui.notify("Profile photo updated ✓", type="positive", position="top")
                                    render_profile_panel()
                                avatar_upload.on_upload(handle_pic)

                        # ── Name + badge ────────────────────────────────────────
                        with ui.element("div").classes("px-10").style("padding-top:70px"):
                            with ui.row().classes("items-center gap-3 mb-1"):
                                ui.label(display_name).classes("text-white font-black").style("font-size:1.6rem")
                                ui.element("span").style(
                                    f"background:{BTN_PRIMARY};color:white;font-size:0.72rem;font-weight:700;"
                                    "padding:3px 12px;border-radius:99px;letter-spacing:0.06em"
                                ).text = "Customer"
                            ui.label(f"@{email}").style(f"color:{TEXT_MUTED};font-size:0.85rem")

                        # ── Edit form ───────────────────────────────────────────
                        with ui.element("div").classes("p-8 w-full max-w-xl"):
                            with ui.element("div").classes("param-card p-6"):
                                ui.label("Personal Info").classes("text-white font-bold mb-5 block").style(
                                    "font-size:1rem; text-transform:uppercase; letter-spacing:0.06em"
                                )
                                f_name  = ui.input("Your Name", value=c.name if c else "").classes("w-full").props("outlined dark dense color=blue-4")
                                f_bio   = ui.textarea("About Me", value=p.bio if p else "").classes("w-full mt-4").props("outlined dark dense color=blue-4 rows=3")
                                f_notes = ui.textarea("Special Notes for Production", value=c.notes if c else "").classes("w-full mt-4").props(
                                    "outlined dark dense color=blue-4 rows=2"
                                )
                                ui.label("e.g. allergies, preferred styles, restrictions").style(f"color:{TEXT_MUTED};font-size:0.75rem;margin-top:-0.3rem")

                                err = ui.label("").style("color:#f87171;font-size:0.82rem;min-height:1rem;margin-top:1rem")

                                def save_profile():
                                    db5 = SessionLocal()
                                    try:
                                        profile_service.update(
                                            db5, email,
                                            full_name=f_name.value,
                                            bio=f_bio.value,
                                        )
                                        c2 = db5.query(Client).filter(Client.email == email).first()
                                        if c2:
                                            client_service.update(
                                                db5, c2.id,
                                                name=f_name.value or c2.name,
                                                notes=f_notes.value or None,
                                            )
                                        ui.notify("Profile saved!", type="positive", position="top")
                                        render_profile_panel()
                                    except Exception as ex:
                                        err.set_text(str(ex))
                                    finally:
                                        db5.close()

                                ui.button("💾  Save Profile", on_click=save_profile).classes("w-full mt-5").props("unelevated").style(
                                    f"background:{BTN_SUCCESS};color:white"
                                )

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
                                ui.label("Your client profile is being set up. Check back soon.").style(f"color:{TEXT_MUTED}")
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
                        ).style(f"color:{TEXT_MUTED};font-size:0.86rem;margin-bottom:1.5rem;line-height:1.5")

                        with ui.row().classes("gap-6 w-full items-start").style("flex-wrap:wrap"):
                            for cat_key, cat_label, cat_tip in PHOTO_CATEGORIES:
                                photos = cat_data[cat_key]
                                with ui.element("div").classes("param-card p-5").style("min-width:260px; flex:1"):
                                    with ui.row().classes("items-center justify-between mb-1"):
                                        ui.label(cat_label).classes("text-white font-semibold").style("font-size:0.95rem")
                                        ui.badge(str(len(photos))).props("color=blue-9 text-color=white")
                                    ui.label(cat_tip).style(f"color:{TEXT_MUTED};font-size:0.75rem;margin-bottom:1rem;line-height:1.4")

                                    if photos:
                                        with ui.element("div").style(
                                            "display:grid;grid-template-columns:repeat(auto-fill,minmax(85px,1fr));gap:8px;margin-bottom:12px"
                                        ):
                                            for ph in photos:
                                                with ui.element("div").classes("photo-thumb").style("height:85px"):
                                                    ui.image(f"/client_refs/{Path(ph.file_path).name}").style(
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
                                                    with ui.element("div").classes("photo-del").on("click", make_del(ph.id)):
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
                                    ).props("accept=image/* flat color=blue-4").classes("w-full")

                render_photos()

            # ── MY PRODUCTIONS ────────────────────────────────────────────────
            with ui.tab_panel(tab_history):
                with ui.element("div").classes("p-8 w-full max-w-4xl mx-auto"):
                    ui.label("My Productions").classes("text-white font-bold mb-2").style("font-size:1.2rem")
                    ui.label("Visual content produced for you by our team.").style(f"color:{TEXT_MUTED};font-size:0.86rem;margin-bottom:1.5rem")

                    prod_container = ui.element("div").classes("w-full")

                    def load_productions():
                        prod_container.clear()
                        db9 = SessionLocal()
                        try:
                            c = db9.query(Client).filter(Client.email == email).first()
                            if not c:
                                with prod_container:
                                    ui.label("No productions yet.").style(f"color:{TEXT_MUTED}")
                                return
                            logs = db9.query(RunLog).filter(RunLog.customer == c.name).order_by(RunLog.ran_at.desc()).all()
                        finally:
                            db9.close()

                        with prod_container:
                            if not logs:
                                with ui.element("div").classes("param-card p-8 text-center"):
                                    ui.label("🎬").style("font-size:2.5rem")
                                    ui.label("No productions yet").classes("text-white font-semibold mt-2")
                                    ui.label("Once our team produces content for you, it will appear here.").style(f"color:{TEXT_MUTED};font-size:0.86rem;margin-top:4px")
                                return

                            STATUS_STYLE = {
                                "pending":     ("🕐 Pending",     "#6b7280", "#1f2937"),
                                "in_progress": ("⚙️ In Progress", "#f59e0b", "#292213"),
                                "done":        ("✅ Done",         "#10b981", "#0d2117"),
                            }

                            for log in logs:
                                try:
                                    meta = json.loads(log.config_json).get("_meta", {})
                                except Exception:
                                    meta = {}

                                s_label, s_color, s_bg = STATUS_STYLE.get(log.status, STATUS_STYLE["pending"])

                                with ui.element("div").classes("param-card p-5 mb-3").style(
                                    f"border-left: 4px solid {s_color};"
                                ):
                                    with ui.row().classes("items-center justify-between mb-2 flex-wrap gap-2"):
                                        with ui.row().classes("gap-3 flex-wrap"):
                                            for k, v in [
                                                ("Platform", meta.get("platform")),
                                                ("Format",   meta.get("format")),
                                                ("Scenery",  meta.get("scenery")),
                                                ("Outfit",   meta.get("outfit")),
                                                ("Lighting", meta.get("lighting")),
                                            ]:
                                                if v:
                                                    ui.badge(f"{k}: {v}").props("color=blue-9 text-color=white")

                                        with ui.row().classes("items-center gap-3 flex-shrink-0"):
                                            ui.element("span").style(
                                                f"background:{s_bg};color:{s_color};border:1px solid {s_color};"
                                                "border-radius:99px;padding:3px 12px;font-size:0.75rem;font-weight:700;"
                                            ).text = s_label
                                            ui.label(
                                                log.ran_at.strftime("%d %b %Y  %H:%M") if log.ran_at else "—"
                                            ).style(f"color:{TEXT_MUTED};font-size:0.8rem")

                                    if log.operator_notes:
                                        ui.label(f"📝 {log.operator_notes}").style(
                                            "color:#9ca3af;font-size:0.8rem;font-style:italic;margin-top:0.3rem"
                                        )

                                    if log.output_file and Path(log.output_file).exists():
                                        output_name = Path(log.output_file).name
                                        with ui.row().classes("items-center gap-3 mt-3"):
                                            ui.label("🎬 Your production is ready!").style(
                                                "color:#10b981;font-size:0.88rem;font-weight:600"
                                            )
                                            ui.button(
                                                "⬇️  Download",
                                                on_click=lambda p=f"/outputs/{output_name}": ui.navigate.to(p, new_tab=True)
                                            ).props("unelevated color=green-8 dense")

                    load_productions()
