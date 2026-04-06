from nicegui import ui, app
from ui.lora_selector import create_configurator
from ui.history_view import create_history_view
from ui.library_view import create_library_view
from ui.combo_manager import create_combo_manager
from ui.client_view import create_client_view
from ui.profile_view import create_profile_view
from ui.request_queue import create_request_queue
from ui.shared_styles import SHARED_CSS, ACCENT_LOGO, TEXT_MUTED
from models.database import SessionLocal
from services.history_service import count_pending


def create_main_page():
    @ui.page("/")
    def index():
        if not app.storage.user.get('authenticated'):
            ui.navigate.to("/login")
            return
        if app.storage.user.get('role') == 'Customer':
            ui.navigate.to("/customer")
            return
        ui.dark_mode().enable()
        ui.add_css(SHARED_CSS)

        # ── Header ──────────────────────────────────────────────────────────
        with ui.element("div").classes("aivp-header w-full px-10 py-7"):
            with ui.row().classes("items-center justify-between"):
                with ui.row().classes("items-center gap-4"):
                    ui.label("⚡").style(f"font-size:2.4rem; color:{ACCENT_LOGO}")
                    with ui.column().classes("gap-0"):
                        ui.label("AIVP").classes("text-white font-black tracking-widest").style("font-size:2rem")
                        ui.label("AI Visual Production").style(
                            f"color:{TEXT_MUTED}; font-size:0.85rem; letter-spacing:0.22em"
                        )
                # Logout button
                def logout():
                    app.storage.user['authenticated'] = False
                    ui.navigate.to("/login")
                ui.button("Sign out", on_click=logout).props("flat color=grey-5 dense")

        # ── Pending count for Requests tab badge ────────────────────────────
        _db_n = SessionLocal()
        _pending_n = count_pending(_db_n)
        _db_n.close()

        # ── Tabs ────────────────────────────────────────────────────────────
        with ui.tabs().classes("w-full").props("dense align=left") as tabs:
            tab_profile  = ui.tab("🪪   Profile").props("no-caps")
            tab_config   = ui.tab("🎛️   Configure").props("no-caps")
            tab_combos   = ui.tab("📁   Templates").props("no-caps")
            tab_history  = ui.tab("📋   History").props("no-caps")
            tab_library  = ui.tab("🗂️   Library").props("no-caps")
            tab_clients  = ui.tab("👤   Clients").props("no-caps")
            with ui.tab("📥   Requests").props("no-caps") as tab_requests:
                if _pending_n > 0:
                    ui.badge(str(_pending_n), color="red").props("floating")

        selections = {}

        with ui.tab_panels(tabs, value=tab_profile).classes("w-full"):

            with ui.tab_panel(tab_profile):
                create_profile_view()

            with ui.tab_panel(tab_config):
                selections = create_configurator()

            with ui.tab_panel(tab_combos):
                create_combo_manager(selections)

            with ui.tab_panel(tab_history):
                create_history_view()

            with ui.tab_panel(tab_library):
                create_library_view()

            with ui.tab_panel(tab_clients):
                create_client_view()

            with ui.tab_panel(tab_requests):
                create_request_queue()
