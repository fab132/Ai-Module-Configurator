from nicegui import ui
from models.database import SessionLocal
from services import lora_service


def create_library_view():
    with ui.element("div").classes("p-8 w-full max-w-4xl mx-auto"):
        ui.label("LoRA Model Library").classes("text-white font-bold mb-6 block").style("font-size: 1.4rem")

        list_container = ui.element("div").classes("w-full mb-10")

        def load_models():
            list_container.clear()
            db = SessionLocal()
            try:
                models = lora_service.get_all(db)
            finally:
                db.close()

            with list_container:
                if not models:
                    ui.label("No LoRA models yet. Add one below.").style("color: #6b7280")
                    return

                for m in models:
                    with ui.element("div").classes("param-card p-4 mb-3 flex items-center justify-between"):
                        with ui.column().classes("gap-0"):
                            ui.label(m.name).classes("text-white font-semibold")
                            ui.label(f"{m.category}  ·  {m.file_path}").style("color: #9ca3af; font-size: 0.8rem")

                        with ui.row().classes("gap-2"):
                            def make_edit(model_id, model_name, model_cat, model_path):
                                def do_edit():
                                    with ui.dialog() as dlg, ui.card().classes("w-96 p-6").style(
                                        "background: #13132b; border: 1px solid rgba(139,92,246,0.3)"
                                    ):
                                        ui.label("Edit LoRA Model").classes("text-white font-bold mb-4 text-lg")
                                        e_name = ui.input("Name", value=model_name).classes("w-full").props("outlined dark dense color=deep-purple-3")
                                        e_cat = ui.input("Category", value=model_cat).classes("w-full mt-3").props("outlined dark dense color=deep-purple-3")
                                        e_path = ui.input("File Path", value=model_path).classes("w-full mt-3").props("outlined dark dense color=deep-purple-3")
                                        err = ui.label("").style("color: #f87171; font-size: 0.82rem; min-height: 1.1rem")

                                        def save_edit():
                                            if not e_name.value.strip() or not e_cat.value.strip() or not e_path.value.strip():
                                                err.set_text("All fields are required")
                                                return
                                            db = SessionLocal()
                                            try:
                                                lora_service.update(db, model_id, e_name.value, e_cat.value, e_path.value)
                                                dlg.close()
                                                load_models()
                                                ui.notify("Model updated", type="positive", position="top")
                                            except Exception as ex:
                                                err.set_text(str(ex))
                                            finally:
                                                db.close()

                                        with ui.row().classes("mt-5 justify-end gap-3"):
                                            ui.button("Cancel", on_click=dlg.close).props("flat color=grey")
                                            ui.button("Save", on_click=save_edit).props("unelevated color=deep-purple")
                                    dlg.open()
                                return do_edit

                            def make_delete(model_id, model_name):
                                def do_delete():
                                    with ui.dialog() as dlg, ui.card().classes("w-80 p-6").style(
                                        "background: #13132b; border: 1px solid rgba(239,68,68,0.4)"
                                    ):
                                        ui.label("Delete LoRA Model?").classes("text-white font-bold mb-2 text-lg")
                                        ui.label(f'"{model_name}" will be permanently removed.').style("color: #9ca3af; font-size: 0.9rem")
                                        with ui.row().classes("mt-5 justify-end gap-3"):
                                            ui.button("Cancel", on_click=dlg.close).props("flat color=grey")
                                            def confirm():
                                                db = SessionLocal()
                                                try:
                                                    lora_service.delete(db, model_id)
                                                    dlg.close()
                                                    load_models()
                                                    ui.notify("Model deleted", type="warning", position="top")
                                                finally:
                                                    db.close()
                                            ui.button("Delete", on_click=confirm).props("unelevated color=red")
                                    dlg.open()
                                return do_delete

                            ui.button("✏", on_click=make_edit(m.id, m.name, m.category, m.file_path)).props("unelevated dense").style(
                                "background:#3B82F6;color:white;min-width:32px;padding:0 8px;border-radius:4px"
                            )
                            ui.button("✕", on_click=make_delete(m.id, m.name)).props("unelevated dense").style(
                                "background:#EF4444;color:white;min-width:32px;padding:0 8px;border-radius:4px"
                            )

        # Add new model form
        with ui.element("div").classes("param-card p-6"):
            ui.label("Add New LoRA Model").classes("text-white font-semibold mb-4 block").style("font-size: 1rem")
            with ui.row().classes("gap-4 items-end w-full"):
                n_name = ui.input("Name").classes("flex-1").props("outlined dark dense color=deep-purple-3")
                n_cat = ui.input("Category").classes("flex-1").props("outlined dark dense color=deep-purple-3")
                n_path = ui.input("File Path").classes("flex-1").props("outlined dark dense color=deep-purple-3")
                add_err = ui.label("").style("color: #f87171; font-size: 0.82rem")

            def add_model():
                if not n_name.value.strip() or not n_cat.value.strip() or not n_path.value.strip():
                    add_err.set_text("All fields required")
                    return
                db = SessionLocal()
                try:
                    lora_service.add(db, n_name.value, n_cat.value, n_path.value)
                    n_name.set_value("")
                    n_cat.set_value("")
                    n_path.set_value("")
                    add_err.set_text("")
                    load_models()
                    ui.notify("Model added", type="positive", position="top")
                except Exception as ex:
                    add_err.set_text(str(ex))
                finally:
                    db.close()

            ui.button("+ Add", on_click=add_model).classes("mt-3").props("unelevated").style(
                "background:#10B981;color:white;border-radius:6px;font-weight:700"
            )

        load_models()
