from nicegui import ui

CUSTOM_CSS = """
    body, .q-page { background: #0a0a14 !important; }
    .auth-card {
        background: linear-gradient(135deg, #13132b 0%, #1a1a35 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 18px;
    }
    .auth-btn {
        background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%) !important;
        letter-spacing: 0.12em !important;
        transition: all 0.2s ease !important;
        border-radius: 12px !important;
    }
    .auth-btn:hover {
        background: linear-gradient(135deg, #6d28d9 0%, #4338ca 100%) !important;
        box-shadow: 0 0 40px rgba(124, 58, 237, 0.5) !important;
    }
    .aivp-header {
        background: linear-gradient(135deg, #12022f 0%, #0a0a14 100%);
        border-bottom: 1px solid rgba(139, 92, 246, 0.25);
    }
"""


def create_register_page():
    @ui.page("/register")
    def register():
        ui.dark_mode().enable()
        ui.add_css(CUSTOM_CSS)

        with ui.element("div").classes("aivp-header w-full px-10 py-7"):
            with ui.row().classes("items-center gap-4"):
                ui.label("⚡").style("font-size: 2.4rem")
                with ui.column().classes("gap-0"):
                    ui.label("AIVP").classes("text-white font-black tracking-widest").style("font-size: 2rem")
                    ui.label("AI Visual Production").style(
                        "color: #a78bfa; font-size: 0.85rem; letter-spacing: 0.22em"
                    )

        with ui.element("div").classes("flex items-center justify-center").style("min-height: calc(100vh - 110px)"):
            with ui.element("div").classes("auth-card p-10").style("width: 400px"):
                ui.label("Create Account").classes("text-white font-bold text-center w-full").style(
                    "font-size: 1.6rem; margin-bottom: 1.5rem"
                )

                email = ui.input("Email").classes("w-full").props('type=email outlined dense dark color=deep-purple-4')
                password = ui.input("Password").classes("w-full mt-4").props(
                    'type=password outlined dense dark color=deep-purple-4'
                )
                confirm = ui.input("Confirm Password").classes("w-full mt-4").props(
                    'type=password outlined dense dark color=deep-purple-4'
                )

                error_label = ui.label("").style("color: #f87171; font-size: 0.85rem; min-height: 1.2rem")

                def handle_register():
                    from models.base import SessionLocal
                    from services.auth_service import register as auth_register
                    error_label.set_text("")
                    if password.value != confirm.value:
                        error_label.set_text("Passwords do not match")
                        return
                    if len(password.value) < 8:
                        error_label.set_text("Password must be at least 8 characters")
                        return
                    try:
                        db = SessionLocal()
                        auth_register(db, email.value, password.value)
                        db.close()
                        ui.navigate.to("/login")
                    except ValueError as e:
                        error_label.set_text(str(e))
                    except Exception:
                        error_label.set_text("An unexpected error occurred")

                ui.button("Create Account", on_click=handle_register).classes("auth-btn w-full mt-6").props("unelevated")

                with ui.row().classes("justify-center mt-4 gap-1"):
                    ui.label("Already have an account?").style("color: #6b7280; font-size: 0.85rem")
                    ui.link("Sign In", "/login").style("color: #a78bfa; font-size: 0.85rem")
