from nicegui import ui
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


def create_configurator():
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
                        label=f"Select...",
                        with_input=True,
                    ).classes("w-full").props("outlined dark color=deep-purple-3")
                    selections[key] = sel

        with ui.row().classes("w-full justify-center mt-6"):
            def handle_run():
                missing = [
                    label for key, label, _ in PARAMS if not selections[key].value
                ]
                if missing:
                    ui.notify(
                        f"Missing: {', '.join(missing)}",
                        type="negative",
                        position="top",
                        timeout=3000,
                    )
                    return
                config = {key: selections[key].value for key, _, _ in PARAMS}
                ui.notify(
                    "⚡ Workflow sent to ComfyUI!",
                    type="positive",
                    position="top",
                    timeout=4000,
                )

            ui.button("⚡  RUN", on_click=handle_run).classes(
                "run-btn text-white font-bold tracking-widest"
            )
