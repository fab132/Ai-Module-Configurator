import json
from pathlib import Path
from nicegui import ui

TEMPLATES_FILE = Path("data/templates.json")
PARAMS_KEYS = ["person", "content_type", "platform", "format", "scenery", "outfit", "lighting", "perspective"]
PARAMS_LABELS = ["Person", "Content-Type", "Platform", "Format", "Scenery", "Outfit", "Lighting", "Perspective"]


def _load_templates() -> dict:
    TEMPLATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not TEMPLATES_FILE.exists():
        return {}
    try:
        return json.loads(TEMPLATES_FILE.read_text())
    except Exception:
        return {}


def _save_templates(templates: dict):
    TEMPLATES_FILE.parent.mkdir(parents=True, exist_ok=True)
    TEMPLATES_FILE.write_text(json.dumps(templates, indent=2))


def create_combo_manager(selections: dict = None):
    """
    selections: dict mapping param key -> ui.select instance (from create_configurator).
    If provided, enables loading combos into the configurator dropdowns.
    Templates are stored as JSON in data/templates.json to avoid schema complications.
    """
    with ui.element("div").classes("p-8 w-full max-w-4xl mx-auto"):
        ui.label("Combo Templates").classes("text-white font-bold mb-6 block").style("font-size: 1.4rem")

        list_container = ui.element("div").classes("w-full mb-10")

        def refresh_list():
            list_container.clear()
            templates = _load_templates()

            with list_container:
                if not templates:
                    ui.label("No templates saved yet. Fill in the Configure tab and save a template below.").style("color: #6b7280")
                    return

                for tname, tparams in sorted(templates.items()):
                    with ui.element("div").classes("param-card p-4 mb-3"):
                        with ui.row().classes("items-center justify-between"):
                            ui.label(tname).classes("text-white font-semibold")
                            with ui.row().classes("gap-2"):
                                def make_load(template_params):
                                    def do_load():
                                        if selections:
                                            for key, val in template_params.items():
                                                if key in selections:
                                                    selections[key].set_value(val)
                                            ui.notify("Template loaded into Configure tab", type="positive", position="top")
                                        else:
                                            ui.notify("Switch to the Configure tab to see the loaded values", type="info", position="top")
                                    return do_load

                                def make_delete(template_name):
                                    def do_delete():
                                        ts = _load_templates()
                                        ts.pop(template_name, None)
                                        _save_templates(ts)
                                        refresh_list()
                                        ui.notify(f'Template "{template_name}" deleted', type="warning", position="top")
                                    return do_delete

                                ui.button("Load", on_click=make_load(tparams)).props("unelevated dense").style(
                                    "background:#3B82F6;color:white;border-radius:6px;font-weight:700"
                                )
                                ui.button("Delete", on_click=make_delete(tname)).props("unelevated dense").style(
                                    "background:#EF4444;color:white;border-radius:6px;font-weight:700"
                                )

                        # Show params summary
                        with ui.row().classes("flex-wrap gap-2 mt-2"):
                            for key, label in zip(PARAMS_KEYS, PARAMS_LABELS):
                                val = tparams.get(key, "—")
                                ui.badge(f"{label}: {val}").props("color=deep-purple-9 text-color=white")

        # Save current selection as template
        with ui.element("div").classes("param-card p-6"):
            ui.label("Save Current Selection as Template").classes("text-white font-semibold mb-4 block")

            with ui.row().classes("gap-4 items-end"):
                template_name_input = ui.input("Template name").classes("flex-1").props("outlined dark dense color=deep-purple-3")
                save_err = ui.label("").style("color: #f87171; font-size: 0.82rem")

            def save_current():
                name = template_name_input.value.strip()
                if not name:
                    save_err.set_text("Enter a template name")
                    return
                if not selections:
                    save_err.set_text("No Configure tab available")
                    return
                params = {key: (sel.value or "") for key, sel in selections.items()}
                missing = [k for k, v in params.items() if not v]
                if missing:
                    save_err.set_text(f"Fill in all parameters first ({', '.join(missing)})")
                    return
                ts = _load_templates()
                ts[name] = params
                _save_templates(ts)
                template_name_input.set_value("")
                save_err.set_text("")
                refresh_list()
                ui.notify(f'Template "{name}" saved!', type="positive", position="top")

            ui.button("💾 Save Template", on_click=save_current).classes("mt-3").props("unelevated").style(
                "background:#10B981;color:white;border-radius:6px;font-weight:700"
            )

        refresh_list()
