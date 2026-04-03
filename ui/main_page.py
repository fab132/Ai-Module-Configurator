from nicegui import ui, app
from ui.lora_selector import create_configurator
from ui.history_view import create_history_view
from ui.library_view import create_library_view
from ui.combo_manager import create_combo_manager
from ui.client_view import create_client_view
from ui.profile_view import create_profile_view

CUSTOM_CSS = """
    body, .q-page { background: #0a0a14 !important; }

    .param-card {
        background: linear-gradient(135deg, #13132b 0%, #1a1a35 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 18px;
        transition: all 0.2s ease;
    }
    .param-card:hover {
        border-color: rgba(139, 92, 246, 0.7);
        transform: translateY(-4px);
        box-shadow: 0 12px 36px rgba(139, 92, 246, 0.22);
    }

    .run-btn {
        background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
        letter-spacing: 0.18em !important;
        transition: all 0.2s ease !important;
        font-size: 1.25rem !important;
        padding: 1.1rem 5rem !important;
        border-radius: 16px !important;
    }
    .run-btn:hover {
        background: linear-gradient(135deg, #6d28d9 0%, #4338ca 100%) !important;
        box-shadow: 0 0 56px rgba(124, 58, 237, 0.55) !important;
        transform: scale(1.04);
    }

    .aivp-header {
        background: linear-gradient(135deg, #12022f 0%, #0a0a14 100%);
        border-bottom: 1px solid rgba(139, 92, 246, 0.25);
    }

    .q-tab--active .q-tab__label {
        color: #a78bfa !important;
        font-size: 1rem !important;
    }
    .q-tab__label {
        font-size: 1rem !important;
    }
    .q-tabs__content {
        background: transparent !important;
    }
    .q-tab-panels {
        background: transparent !important;
    }
    .q-select .q-field__label {
        font-size: 1rem !important;
    }
    .q-select .q-field__native {
        font-size: 1rem !important;
    }
"""


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
        ui.add_css(CUSTOM_CSS)

        # ── Header ──────────────────────────────────────────────────────────
        with ui.element("div").classes("aivp-header w-full px-10 py-7"):
            with ui.row().classes("items-center justify-between"):
                with ui.row().classes("items-center gap-4"):
                    ui.label("⚡").style("font-size: 2.4rem")
                    with ui.column().classes("gap-0"):
                        ui.label("AIVP").classes("text-white font-black tracking-widest").style("font-size: 2rem")
                        ui.label("AI Visual Production").style(
                            "color: #a78bfa; font-size: 0.85rem; letter-spacing: 0.22em"
                        )
                # Logout button
                def logout():
                    app.storage.user['authenticated'] = False
                    ui.navigate.to("/login")
                ui.button("Sign out", on_click=logout).props("flat color=grey-5 dense")

        # ── Tabs ────────────────────────────────────────────────────────────
        with ui.tabs().classes("w-full").props("dense align=left") as tabs:
            tab_profile = ui.tab("🪪   Profile").props("no-caps")
            tab_config  = ui.tab("🎛️   Configure").props("no-caps")
            tab_combos  = ui.tab("📁   Templates").props("no-caps")
            tab_history = ui.tab("📋   History").props("no-caps")
            tab_library = ui.tab("🗂️   Library").props("no-caps")
            tab_clients = ui.tab("👤   Clients").props("no-caps")

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
