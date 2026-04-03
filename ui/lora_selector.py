from nicegui import ui, app
from services.config_loader import get_options

PARAMS = [
    ("person",       "Person",       "👤"),
    ("content_type", "Content-Type", "🎬"),
    ("platform",     "Platform",     "📱"),
    ("format",       "Format",       "📐"),
    ("scenery",      "Scenery",      "🏙️"),
    ("outfit",       "Outfit",       "👗"),
    ("lighting",     "Lighting",     "💡"),
    ("perspective",  "Perspective",  "🎯"),
]


def create_configurator() -> dict:
    """Creates the configure-run UI. Returns selections dict for external use."""
    selections: dict[str, ui.select] = {}

    with ui.element("div").classes("p-10 w-full max-w-7xl mx-auto"):
        ui.label("Configure your run").classes(
            "text-white text-2xl font-semibold mb-8 block tracking-wide"
        )

        with ui.element("div").classes(
            "grid grid-cols-2 gap-6 mb-10"
        ).style("grid-template-columns: repeat(4, 1fr)"):
            for key, label, icon in PARAMS:
                options = get_options(key)
                with ui.element("div").classes("param-card p-6 flex flex-col gap-3"):
                    ui.label(f"{icon}  {label}").classes(
                        "text-sm font-bold uppercase tracking-widest"
                    ).style("color: #a78bfa")
                    sel = ui.select(
                        options=options,
                        label="Select...",
                        with_input=True,
                    ).classes("w-full").props("outlined dark color=deep-purple-3")
                    selections[key] = sel

        # Customer / Project field
        with ui.element("div").classes("param-card p-6 mb-6").style("max-width: 420px"):
            ui.label("👤  Customer / Project").classes(
                "text-sm font-bold uppercase tracking-widest mb-3 block"
            ).style("color: #a78bfa")
            customer_input = ui.input("Customer or project name").classes("w-full").props(
                "outlined dense dark color=deep-purple-3"
            )

        with ui.row().classes("w-full justify-center mt-6"):
            def handle_run():
                missing = [label for key, label, _ in PARAMS if not selections[key].value]
                if missing:
                    ui.notify(f"Missing: {', '.join(missing)}", type="negative", position="top", timeout=3000)
                    return

                params = {key: selections[key].value for key, _, _ in PARAMS}
                customer = customer_input.value.strip() or app.storage.user.get("email", "anonymous")

                from models.database import SessionLocal
                from services.configurator import run as cfg_run
                import requests

                db = SessionLocal()
                try:
                    cfg_run(db, params=params, customer=customer, send_to_api=True)
                    ui.notify("⚡ Workflow sent to ComfyUI!", type="positive", position="top", timeout=4000)
                except Exception as e:
                    if "requests" in type(e).__module__ or "ConnectionError" in type(e).__name__ or "RequestException" in type(e).__name__:
                        # ComfyUI not reachable — still log the run without sending
                        from services.configurator import run as cfg_run2
                        try:
                            cfg_run2(db, params=params, customer=customer, send_to_api=False)
                            ui.notify("⚠️ ComfyUI unreachable — run logged locally.", type="warning", position="top", timeout=5000)
                        except Exception as inner:
                            ui.notify(f"Error: {inner}", type="negative", position="top", timeout=5000)
                    else:
                        ui.notify(f"Error: {e}", type="negative", position="top", timeout=5000)
                finally:
                    db.close()

            ui.button("⚡  RUN", on_click=handle_run).classes(
                "run-btn text-white font-bold tracking-widest"
            )

    return selections
