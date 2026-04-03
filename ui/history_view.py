# Table view of all RunLog entries
from nicegui import ui


def create_history_view():
    with ui.element("div").classes("p-6"):
        ui.label("History").classes("text-white font-bold").style("font-size: 1.4rem; margin-bottom: 1rem")
        ui.label("Run history will appear here.").style("color: #6b7280")
