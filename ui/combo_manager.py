# Save / load / rename Combo Templates
from nicegui import ui


def create_combo_manager():
    with ui.element("div").classes("p-6"):
        ui.label("Templates").classes("text-white font-bold").style("font-size: 1.4rem; margin-bottom: 1rem")
        ui.label("Saved combo templates will appear here.").style("color: #6b7280")
