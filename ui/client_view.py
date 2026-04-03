import uuid
from pathlib import Path
from nicegui import ui, events
from models.database import SessionLocal
from services import client_service

PICS_DIR = Path("data/client_pics")
PICS_DIR.mkdir(parents=True, exist_ok=True)

PLACEHOLDER = "https://ui-avatars.com/api/?background=7c3aed&color=fff&size=128&bold=true&name="


def _avatar_url(client) -> str:
    if client.profile_picture and Path(client.profile_picture).exists():
        return f"/client_pics/{Path(client.profile_picture).name}"
    initials = "+".join(client.name.split()[:2])
    return PLACEHOLDER + initials


def create_client_view():
    with ui.element("div").classes("p-8 w-full max-w-5xl mx-auto"):
        with ui.row().classes("items-center justify-between mb-6"):
            ui.label("Client Profiles").classes("text-white font-bold").style("font-size: 1.4rem")
            ui.button("+ Add Client", on_click=lambda: open_add_dialog()).props(
                "unelevated color=deep-purple"
            )

        grid_container = ui.element("div").classes("w-full")

        def refresh():
            grid_container.clear()
            db = SessionLocal()
            try:
                clients = client_service.get_all(db)
            finally:
                db.close()

            with grid_container:
                if not clients:
                    with ui.element("div").classes("p-12 text-center"):
                        ui.label("👤").style("font-size: 3rem")
                        ui.label("No clients yet").classes("text-white font-semibold mt-2").style("font-size: 1.1rem")
                        ui.label("Add your first client to start producing personalised content.").style("color: #6b7280; margin-top: 0.5rem")
                    return

                with ui.element("div").style(
                    "display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1.5rem"
                ):
                    for c in clients:
                        with ui.element("div").classes("param-card p-6 flex flex-col gap-3"):
                            with ui.row().classes("items-center gap-4"):
                                ui.image(_avatar_url(c)).style(
                                    "width: 64px; height: 64px; border-radius: 50%; object-fit: cover;"
                                    "border: 2px solid rgba(139,92,246,0.5)"
                                )
                                with ui.column().classes("gap-0 flex-1"):
                                    ui.label(c.name).classes("text-white font-bold").style("font-size: 1rem")
                                    if c.email:
                                        ui.label(c.email).style("color: #9ca3af; font-size: 0.8rem")

                            if c.lora_checkpoint:
                                with ui.row().classes("items-center gap-2"):
                                    ui.label("🧠").style("font-size: 0.9rem")
                                    ui.label(c.lora_checkpoint).style(
                                        "color: #a78bfa; font-size: 0.78rem; word-break: break-all"
                                    )

                            if c.prompt_prefix:
                                ui.label(f'"{c.prompt_prefix}"').style(
                                    "color: #6b7280; font-size: 0.78rem; font-style: italic"
                                )

                            if c.notes:
                                ui.label(c.notes).style("color: #9ca3af; font-size: 0.78rem")

                            with ui.row().classes("mt-2 gap-2"):
                                def make_edit(client_obj):
                                    def do_edit():
                                        open_edit_dialog(client_obj)
                                    return do_edit

                                def make_delete(cid, cname):
                                    def do_delete():
                                        open_delete_dialog(cid, cname)
                                    return do_delete

                                def make_open(cid):
                                    def do_open():
                                        ui.navigate.to(f"/client/{cid}")
                                    return do_open

                                ui.button("View Profile", on_click=make_open(c.id)).props("unelevated color=deep-purple dense")
                                ui.button("Edit", on_click=make_edit(c)).props("flat color=deep-purple-3 dense")
                                ui.button("Delete", on_click=make_delete(c.id, c.name)).props("flat color=red dense")

        def _client_form_fields(dialog_card, existing=None):
            """Render form fields. Returns a getter function that returns field values."""
            with dialog_card:
                f_name = ui.input("Full Name *", value=existing.name if existing else "").classes("w-full").props("outlined dark dense color=deep-purple-3")
                f_email = ui.input("Email", value=existing.email or "" if existing else "").classes("w-full mt-3").props("outlined dark dense color=deep-purple-3")
                f_lora = ui.input("LoRA Checkpoint path", value=existing.lora_checkpoint or "" if existing else "").classes("w-full mt-3").props(
                    "outlined dark dense color=deep-purple-3"
                )
                ui.label("e.g. models/lora/sarah_v1.safetensors").style("color: #6b7280; font-size: 0.75rem; margin-top: -0.5rem")
                f_prefix = ui.input("Prompt Prefix", value=existing.prompt_prefix or "" if existing else "").classes("w-full mt-3").props(
                    "outlined dark dense color=deep-purple-3"
                )
                ui.label('e.g. "photo of sarah, woman, "').style("color: #6b7280; font-size: 0.75rem; margin-top: -0.5rem")
                f_notes = ui.textarea("Notes", value=existing.notes or "" if existing else "").classes("w-full mt-3").props(
                    "outlined dark dense color=deep-purple-3 rows=2"
                )

                pic_path_holder = {"path": existing.profile_picture if existing else None}

                ui.label("Profile Picture").classes("text-white text-sm mt-4 mb-1 block")

                def handle_upload(e: events.UploadEventArguments):
                    ext = Path(e.name).suffix or ".jpg"
                    fname = f"{uuid.uuid4().hex}{ext}"
                    dest = PICS_DIR / fname
                    dest.write_bytes(e.content.read())
                    pic_path_holder["path"] = str(dest)
                    ui.notify("Picture uploaded", type="positive", position="top")

                ui.upload(
                    on_upload=handle_upload,
                    label="Upload photo",
                    max_file_size=5_000_000,
                    auto_upload=True,
                ).props("accept=image/* flat color=deep-purple-3").classes("w-full")

                err = ui.label("").style("color: #f87171; font-size: 0.82rem; min-height: 1rem")

            def get_values():
                return {
                    "name": f_name.value,
                    "email": f_email.value,
                    "lora_checkpoint": f_lora.value,
                    "prompt_prefix": f_prefix.value,
                    "notes": f_notes.value,
                    "profile_picture": pic_path_holder["path"],
                }

            return get_values, err

        def open_add_dialog():
            with ui.dialog() as dlg, ui.card().classes("w-full max-w-lg p-6").style(
                "background: #13132b; border: 1px solid rgba(139,92,246,0.3); max-height: 90vh; overflow-y: auto"
            ):
                ui.label("Add New Client").classes("text-white font-bold mb-4").style("font-size: 1.2rem")

                inner = ui.element("div").classes("w-full")
                get_values, err = _client_form_fields(inner)

                def do_add():
                    vals = get_values()
                    if not vals["name"].strip():
                        err.set_text("Client name is required")
                        return
                    db = SessionLocal()
                    try:
                        client_service.add(db, **{k: v or None if k != "prompt_prefix" else v for k, v in vals.items()})
                        dlg.close()
                        refresh()
                        ui.notify(f"Client \"{vals['name']}\" added!", type="positive", position="top")
                    except Exception as ex:
                        err.set_text(str(ex))
                    finally:
                        db.close()

                with ui.row().classes("mt-5 justify-end gap-3"):
                    ui.button("Cancel", on_click=dlg.close).props("flat color=grey")
                    ui.button("Add Client", on_click=do_add).props("unelevated color=deep-purple")
            dlg.open()

        def open_edit_dialog(existing_client):
            with ui.dialog() as dlg, ui.card().classes("w-full max-w-lg p-6").style(
                "background: #13132b; border: 1px solid rgba(139,92,246,0.3); max-height: 90vh; overflow-y: auto"
            ):
                ui.label("Edit Client").classes("text-white font-bold mb-4").style("font-size: 1.2rem")

                inner = ui.element("div").classes("w-full")
                get_values, err = _client_form_fields(inner, existing=existing_client)

                def do_edit():
                    vals = get_values()
                    if not vals["name"].strip():
                        err.set_text("Client name is required")
                        return
                    db = SessionLocal()
                    try:
                        client_service.update(db, existing_client.id, **{k: v or None if k != "prompt_prefix" else v for k, v in vals.items()})
                        dlg.close()
                        refresh()
                        ui.notify("Client updated", type="positive", position="top")
                    except Exception as ex:
                        err.set_text(str(ex))
                    finally:
                        db.close()

                with ui.row().classes("mt-5 justify-end gap-3"):
                    ui.button("Cancel", on_click=dlg.close).props("flat color=grey")
                    ui.button("Save Changes", on_click=do_edit).props("unelevated color=deep-purple")
            dlg.open()

        def open_delete_dialog(cid, cname):
            with ui.dialog() as dlg, ui.card().classes("w-80 p-6").style(
                "background: #13132b; border: 1px solid rgba(239,68,68,0.4)"
            ):
                ui.label("Delete Client?").classes("text-white font-bold mb-2").style("font-size: 1.1rem")
                ui.label(f'"{cname}" and all their data will be permanently removed.').style("color: #9ca3af; font-size: 0.88rem")
                with ui.row().classes("mt-5 justify-end gap-3"):
                    ui.button("Cancel", on_click=dlg.close).props("flat color=grey")
                    def do_del():
                        db = SessionLocal()
                        try:
                            client_service.delete(db, cid)
                            dlg.close()
                            refresh()
                            ui.notify(f'"{cname}" deleted', type="warning", position="top")
                        finally:
                            db.close()
                    ui.button("Delete", on_click=do_del).props("unelevated color=red")
            dlg.open()

        refresh()
