from nicegui import ui
from ui.lora_selector import create_configurator

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
        ui.dark_mode().enable()
        ui.add_css(CUSTOM_CSS)

        # ── Header ──────────────────────────────────────────────────────────
        with ui.element("div").classes("aivp-header w-full px-10 py-7"):
            with ui.row().classes("items-center gap-4"):
                ui.label("⚡").style("font-size: 2.4rem")
                with ui.column().classes("gap-0"):
                    ui.label("AIVP").classes("text-white font-black tracking-widest").style("font-size: 2rem")
                    ui.label("AI Visual Production").style(
                        "color: #a78bfa; font-size: 0.85rem; letter-spacing: 0.22em"
                    )

        # ── Tabs ────────────────────────────────────────────────────────────
        with ui.tabs().classes("w-full").props("dense align=left") as tabs:
            tab_config  = ui.tab("🎛️   Configure").props("no-caps")
            tab_combos  = ui.tab("📁   Templates").props("no-caps")
            tab_history = ui.tab("📋   History").props("no-caps")
            tab_library = ui.tab("🗂️   Library").props("no-caps")

        with ui.tab_panels(tabs, value=tab_config).classes("w-full"):

            with ui.tab_panel(tab_config):
                create_configurator()

            with ui.tab_panel(tab_combos):
                with ui.element("div").classes("p-10 text-center").style("color: #6b7280"):
                    ui.label("📁  Templates — coming soon")

            with ui.tab_panel(tab_history):
                with ui.element("div").classes("p-10 text-center").style("color: #6b7280"):
                    ui.label("📋  History — coming soon")

            with ui.tab_panel(tab_library):
                with ui.element("div").classes("p-10 text-center").style("color: #6b7280"):
                    ui.label("🗂️  Library — coming soon")
