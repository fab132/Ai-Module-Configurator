# CRUD UI for the LoRA model library
from nicegui import ui


def create_library_view():
    with ui.element("div").classes("p-6"):
        ui.label("Library").classes("text-white font-bold").style("font-size: 1.4rem; margin-bottom: 1rem")
        ui.label("Your LoRA model library will appear here.").style("color: #6b7280")
