import uuid
from pathlib import Path
from nicegui import ui, events
from models.database import SessionLocal
from services import client_service

REFS_DIR = Path("data/client_refs")
PICS_DIR = Path("data/client_pics")
REFS_DIR.mkdir(parents=True, exist_ok=True)
PICS_DIR.mkdir(parents=True, exist_ok=True)

PLACEHOLDER = "https://ui-avatars.com/api/?background=7c3aed&color=fff&size=128&bold=true&name="
COVER_GRADIENT = "linear-gradient(135deg, #12022f 0%, #1e1b4b 50%, #4c1d95 100%)"

PHOTO_CATEGORIES = [
    ("face",  "📸  Face Reference",  "Front face, profile, 3/4 angle — used for face consistency in LoRA training"),
    ("body",  "👤  Body Reference",  "Full body, half body, close-up — used for body and outfit generation"),
    ("style", "🎨  Style Reference", "Outfit mood, environment, lighting inspiration — used for aesthetic matching"),
]

PAGE_CSS = """
    body, .q-page { background: #0a0a14 !important; }
    .param-card {
        background: linear-gradient(135deg, #13132b 0%, #1a1a35 100%);
        border: 1px solid rgba(139,92,246,0.25);
        border-radius: 18px;
        transition: all 0.2s ease;
    }
    .photo-thumb {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid rgba(139,92,246,0.25);
        transition: all 0.2s ease;
    }
    .photo-thumb:hover { border-color: rgba(139,92,246,0.7); }
    .photo-delete {
        position: absolute; top: 4px; right: 4px;
        background: rgba(239,68,68,0.85);
        border-radius: 6px; padding: 2px 6px;
        font-size: 0.72rem; color: white; cursor: pointer;
        opacity: 0; transition: opacity 0.2s;
    }
    .photo-thumb:hover .photo-delete { opacity: 1; }
    .aivp-header {
        background: linear-gradient(135deg, #12022f 0%, #0a0a14 100%);
        border-bottom: 1px solid rgba(139,92,246,0.25);
    }
"""


def _avatar_url(client) -> str:
    if client.profile_picture and Path(client.profile_picture).exists():
        return f"/client_pics/{Path(client.profile_picture).name}"
    initials = "+".join(client.name.split()[:2])
    return PLACEHOLDER + initials


def _ref_url(photo) -> str:
    return f"/client_refs/{Path(photo.file_path).name}"


def create_client_profile_page():
    @ui.page("/client/{client_id}")
    def client_profile(client_id: int):
        ui.dark_mode().enable()
        ui.add_css(PAGE_CSS)

        # ── App header ───────────────────────────────────────────────────────
        with ui.element("div").classes("aivp-header w-full px-10 py-5"):
            with ui.row().classes("items-center justify-between"):
                with ui.row().classes("items-center gap-4"):
                    ui.label("⚡").style("font-size: 2rem")
                    ui.label("AIVP").classes("text-white font-black tracking-widest").style("font-size: 1.6rem")
                ui.button("← Back to Clients", on_click=lambda: ui.navigate.to("/")).props(
                    "flat color=grey-4 dense"
                )

        db = SessionLocal()
        try:
            client = client_service.get_by_id(db, client_id)
        finally:
            db.close()

        if not client:
            with ui.element("div").classes("p-16 text-center"):
                ui.label("Client not found").classes("text-white text-2xl")
                ui.button("← Go back", on_click=lambda: ui.navigate.to("/")).props("flat color=deep-purple-3")
            return

        page_container = ui.element("div").classes("w-full")

        def render():
            page_container.clear()
            db2 = SessionLocal()
            try:
                c = client_service.get_by_id(db2, client_id)
                photos_face  = client_service.get_photos(db2, client_id, "face")
                photos_body  = client_service.get_photos(db2, client_id, "body")
                photos_style = client_service.get_photos(db2, client_id, "style")
            finally:
                db2.close()

            if not c:
                return

            with page_container:
                # ── Cover + Avatar ───────────────────────────────────────────
                with ui.element("div").style(f"position:relative; {COVER_GRADIENT}"):
                    with ui.element("div").style(
                        f"width:100%; height:210px; background:{COVER_GRADIENT};"
                    ):
                        pass

                    # Avatar overlapping cover
                    with ui.element("div").style(
                        "position:absolute; bottom:-50px; left:48px;"
                        "width:104px; height:104px; border-radius:50%;"
                        "border:4px solid #0a0a14; overflow:hidden; background:#1a1a35;"
                        "box-shadow: 0 0 0 3px rgba(139,92,246,0.5);"
                    ):
                        ui.image(_avatar_url(c)).style("width:100%; height:100%; object-fit:cover;")

                # ── Client info ──────────────────────────────────────────────
                with ui.element("div").classes("px-12").style("padding-top:64px"):
                    with ui.row().classes("items-start justify-between w-full"):
                        with ui.column().classes("gap-1"):
                            ui.label(c.name).classes("text-white font-black").style("font-size:1.7rem")
                            if c.email:
                                ui.label(c.email).style("color:#6b7280; font-size:0.88rem")
                            if c.prompt_prefix:
                                ui.label(f'"{c.prompt_prefix}"').style(
                                    "color:#a78bfa; font-size:0.85rem; font-style:italic; margin-top:4px"
                                )
                            if c.notes:
                                ui.label(c.notes).style(
                                    "color:#9ca3af; font-size:0.85rem; max-width:480px; margin-top:4px"
                                )

                        ui.button("✏️  Edit Client", on_click=lambda: open_edit_dialog(c)).props(
                            "outlined color=deep-purple-3"
                        )

                    # LoRA info pill
                    if c.lora_checkpoint:
                        with ui.row().classes("items-center gap-3 mt-4"):
                            with ui.element("div").style(
                                "background:rgba(124,58,237,0.15); border:1px solid rgba(139,92,246,0.35);"
                                "border-radius:99px; padding:6px 16px; display:flex; align-items:center; gap:8px;"
                            ):
                                ui.label("🧠").style("font-size:0.9rem")
                                ui.label(c.lora_checkpoint).style("color:#a78bfa; font-size:0.82rem")
                                ui.label(f"weight: {c.lora_weight:.1f}").style(
                                    "color:#6b7280; font-size:0.78rem; margin-left:4px"
                                )

                # ── Divider ──────────────────────────────────────────────────
                ui.element("div").style(
                    "width:100%; height:1px; background:rgba(139,92,246,0.15); margin:2rem 0 1.5rem"
                )

                # ── Reference Photos ─────────────────────────────────────────
                with ui.element("div").classes("px-12"):
                    ui.label("Reference Photos for Avatar Creation").classes(
                        "text-white font-bold mb-1"
                    ).style("font-size:1.15rem; letter-spacing:0.04em")
                    ui.label(
                        "Upload high-quality photos in each category. The more variety, the better the LoRA model quality."
                    ).style("color:#6b7280; font-size:0.85rem; margin-bottom:1.5rem")

                    cat_photos = {"face": photos_face, "body": photos_body, "style": photos_style}

                    with ui.row().classes("w-full gap-6 items-start").style("flex-wrap:wrap"):
                        for cat_key, cat_label, cat_tip in PHOTO_CATEGORIES:
                            photos = cat_photos[cat_key]
                            with ui.element("div").classes("param-card p-5 flex-1").style("min-width:280px"):
                                with ui.row().classes("items-center justify-between mb-1"):
                                    ui.label(cat_label).classes("text-white font-semibold").style("font-size:0.95rem")
                                    ui.badge(str(len(photos))).props("color=deep-purple-9 text-color=white")

                                ui.label(cat_tip).style(
                                    "color:#6b7280; font-size:0.75rem; margin-bottom:1rem; line-height:1.4"
                                )

                                # Photo grid
                                if photos:
                                    with ui.element("div").style(
                                        "display:grid; grid-template-columns:repeat(auto-fill,minmax(90px,1fr)); gap:8px; margin-bottom:12px"
                                    ):
                                        for p in photos:
                                            with ui.element("div").classes("photo-thumb").style("height:90px"):
                                                ui.image(_ref_url(p)).style(
                                                    "width:100%; height:100%; object-fit:cover;"
                                                )
                                                def make_del(pid):
                                                    def do_del():
                                                        db3 = SessionLocal()
                                                        try:
                                                            client_service.delete_photo(db3, pid)
                                                        finally:
                                                            db3.close()
                                                        render()
                                                    return do_del
                                                with ui.element("div").classes("photo-delete").on(
                                                    "click", make_del(p.id)
                                                ):
                                                    ui.label("✕")

                                # Upload button
                                def make_uploader(category):
                                    def handle_ref_upload(e: events.UploadEventArguments):
                                        ext = Path(e.name).suffix or ".jpg"
                                        fname = f"ref_{uuid.uuid4().hex}{ext}"
                                        dest = REFS_DIR / fname
                                        dest.write_bytes(e.content.read())
                                        db4 = SessionLocal()
                                        try:
                                            client_service.add_photo(db4, client_id, str(dest), category)
                                        finally:
                                            db4.close()
                                        ui.notify("Photo added", type="positive", position="top")
                                        render()
                                    return handle_ref_upload

                                ui.upload(
                                    on_upload=make_uploader(cat_key),
                                    label=f"+ Upload",
                                    max_file_size=8_000_000,
                                    auto_upload=True,
                                    multiple=True,
                                ).props("accept=image/* flat color=deep-purple-3").classes("w-full")

                # ── Generation Settings ──────────────────────────────────────
                ui.element("div").style(
                    "width:100%; height:1px; background:rgba(139,92,246,0.15); margin:2rem 0 1.5rem"
                )

                with ui.element("div").classes("px-12 pb-12"):
                    ui.label("Generation Settings").classes("text-white font-bold mb-4").style("font-size:1.15rem")

                    with ui.element("div").classes("param-card p-6").style("max-width:600px"):
                        ui.label("LoRA Weight").style("color:#a78bfa; font-size:0.82rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase")
                        weight_val = ui.label(f"{c.lora_weight:.2f}").style("color:#e5e7eb; font-size:0.9rem; margin-top:4px")

                        weight_slider = ui.slider(min=0.0, max=1.0, step=0.05, value=c.lora_weight).classes(
                            "w-full mt-2"
                        ).props("color=deep-purple-3 thumb-label")
                        weight_slider.on("update:model-value", lambda e: weight_val.set_text(f"{e.args:.2f}"))

                        ui.label("Negative Prompt").style(
                            "color:#a78bfa; font-size:0.82rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; margin-top:1.2rem"
                        )
                        neg_input = ui.textarea(
                            value=c.negative_prompt or "",
                            placeholder="e.g. blurry, low quality, distorted face, bad anatomy",
                        ).classes("w-full mt-2").props("outlined dark dense color=deep-purple-3 rows=2")

                        def save_settings():
                            db5 = SessionLocal()
                            try:
                                client_service.update(
                                    db5, client_id,
                                    name=c.name,
                                    lora_weight=weight_slider.value,
                                    negative_prompt=neg_input.value,
                                )
                                ui.notify("Settings saved", type="positive", position="top")
                            finally:
                                db5.close()

                        ui.button("💾  Save Settings", on_click=save_settings).classes("mt-4").props(
                            "unelevated color=deep-purple"
                        )

        def open_edit_dialog(existing_client):
            with ui.dialog() as dlg, ui.card().classes("w-full max-w-lg p-6").style(
                "background:#13132b; border:1px solid rgba(139,92,246,0.3); max-height:90vh; overflow-y:auto"
            ):
                ui.label("Edit Client").classes("text-white font-bold mb-4").style("font-size:1.2rem")
                f_name   = ui.input("Name *", value=existing_client.name).classes("w-full").props("outlined dark dense color=deep-purple-3")
                f_email  = ui.input("Email", value=existing_client.email or "").classes("w-full mt-3").props("outlined dark dense color=deep-purple-3")
                f_lora   = ui.input("LoRA Checkpoint", value=existing_client.lora_checkpoint or "").classes("w-full mt-3").props("outlined dark dense color=deep-purple-3")
                f_prefix = ui.input("Prompt Prefix", value=existing_client.prompt_prefix or "").classes("w-full mt-3").props("outlined dark dense color=deep-purple-3")
                f_notes  = ui.textarea("Notes", value=existing_client.notes or "").classes("w-full mt-3").props("outlined dark dense color=deep-purple-3 rows=2")

                pic_holder = {"path": None}
                ui.label("Profile Picture").classes("text-white text-sm mt-4 mb-1 block")

                def handle_pic(e: events.UploadEventArguments):
                    ext = Path(e.name).suffix or ".jpg"
                    dest = PICS_DIR / f"{uuid.uuid4().hex}{ext}"
                    dest.write_bytes(e.content.read())
                    pic_holder["path"] = str(dest)
                    ui.notify("Photo uploaded", type="positive", position="top")

                ui.upload(on_upload=handle_pic, label="Upload photo", max_file_size=5_000_000, auto_upload=True).props(
                    "accept=image/* flat color=deep-purple-3"
                ).classes("w-full")
                err = ui.label("").style("color:#f87171; font-size:0.82rem; min-height:1rem")

                def do_save():
                    if not f_name.value.strip():
                        err.set_text("Name is required")
                        return
                    db6 = SessionLocal()
                    try:
                        client_service.update(
                            db6, existing_client.id,
                            name=f_name.value, email=f_email.value or None,
                            lora_checkpoint=f_lora.value or None,
                            prompt_prefix=f_prefix.value,
                            notes=f_notes.value or None,
                            profile_picture=pic_holder["path"],
                        )
                        dlg.close()
                        render()
                        ui.notify("Client updated", type="positive", position="top")
                    except Exception as ex:
                        err.set_text(str(ex))
                    finally:
                        db6.close()

                with ui.row().classes("mt-5 justify-end gap-3"):
                    ui.button("Cancel", on_click=dlg.close).props("flat color=grey")
                    ui.button("Save", on_click=do_save).props("unelevated color=deep-purple")
            dlg.open()

        render()
