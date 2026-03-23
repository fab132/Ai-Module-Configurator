from nicegui import ui
from ui.lora_selector import create_configurator

CUSTOM_CSS = """
    body, .q-page { background: #0a0a14 !important; }

    .param-card {
        background: linear-gradient(135deg, #13132b 0%, #1a1a35 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 14px;
        transition: all 0.2s ease;
    }
    .param-card:hover {
        border-color: rgba(139, 92, 246, 0.7);
        transform: translateY(-3px);
        box-shadow: 0 8px 28px rgba(139, 92, 246, 0.18);
    }

    .run-btn {
        background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
        letter-spacing: 0.15em !important;
        transition: all 0.2s ease !important;
    }
    .run-btn:hover {
        background: linear-gradient(135deg, #6d28d9 0%, #4338ca 100%) !important;
        box-shadow: 0 0 40px rgba(124, 58, 237, 0.45) !important;
        transform: scale(1.03);
    }

    .aivp-header {
        background: linear-gradient(135deg, #12022f 0%, #0a0a14 100%);
        border-bottom: 1px solid rgba(139, 92, 246, 0.25);
    }

    .q-tab--active .q-tab__label {
        color: #a78bfa !important;
    }
    .q-tabs__content {
        background: transparent !important;
    }
    .q-tab-panels {
        background: transparent !important;
    }
"""


def create_main_page():
    @ui.page("/")
    def index():
        ui.dark_mode().enable()
        ui.add_css(CUSTOM_CSS)

        # ── Header ──────────────────────────────────────────────────────────
        with ui.element("div").classes("aivp-header w-full px-8 py-5"):
            with ui.row().classes("items-center gap-3"):
                ui.label("⚡").style("font-size: 1.8rem")
                with ui.column().classes("gap-0"):
                    ui.label("AIVP").classes("text-white text-2xl font-black tracking-widest")
                    ui.label("AI Visual Production").style(
                        "color: #a78bfa; font-size: 0.72rem; letter-spacing: 0.2em"
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
