from nicegui import ui, app

CUSTOM_CSS = """
    body, .q-page { background: #0f0f23 !important; }
    .auth-card {
        background: #1a1a3e;
        border: 1px solid #2d2d5e;
        border-radius: 12px;
    }
    .auth-btn {
        background: #3B82F6 !important;
        letter-spacing: 0.08em !important;
        transition: all 0.2s ease !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    .auth-btn:hover {
        background: #2563EB !important;
        box-shadow: 0 0 30px rgba(59,130,246,0.45) !important;
    }
    .aivp-header {
        background: #16213e;
        border-bottom: 1px solid #2a2a4a;
    }
"""


def create_login_page():
    @ui.page("/login")
    def login():
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
                ui.label("Sign In").classes("text-white font-bold text-center w-full").style(
                    "font-size: 1.6rem; margin-bottom: 1.5rem"
                )

                email = ui.input("Email").classes("w-full").props('type=email outlined dense dark color=deep-purple-4')
                password = ui.input("Password").classes("w-full mt-4").props(
                    'type=password outlined dense dark color=deep-purple-4'
                )

                error_label = ui.label("").style("color: #f87171; font-size: 0.85rem; min-height: 1.2rem")

                def handle_login():
                    from models.database import SessionLocal
                    from services.auth_service import login as auth_login, get_role
                    error_label.set_text("")
                    try:
                        db = SessionLocal()
                        auth_login(db, email.value, password.value)
                        role = get_role(db, email.value)
                        db.close()
                        app.storage.user['authenticated'] = True
                        app.storage.user['email'] = email.value
                        app.storage.user['role'] = role
                        if role == "Customer":
                            ui.navigate.to("/customer")
                        else:
                            ui.navigate.to("/")
                    except ValueError as e:
                        error_label.set_text(str(e))
                    except Exception as ex:
                        error_label.set_text(f"Error: {ex}")

                ui.button("Sign In", on_click=handle_login).classes("auth-btn w-full mt-6").props("unelevated")

                # ── Demo quick-login ─────────────────────────────────────────
                ui.separator().classes("my-5").style("border-color: rgba(139,92,246,0.2)")
                ui.label("Demo Access").classes("text-center w-full").style(
                    "color:#6b7280; font-size:0.78rem; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.6rem"
                )
                with ui.row().classes("gap-3 w-full"):
                    def quick_login(demo_email, demo_password):
                        def do():
                            email.set_value(demo_email)
                            password.set_value(demo_password)
                            handle_login()
                        return do

                    ui.button("⚡  Operator Demo", on_click=quick_login("admin@aivp.com", "admin123")).props(
                        "unelevated color=deep-purple dense"
                    ).classes("flex-1")
                    ui.button("👤  Customer Demo", on_click=quick_login("client@aivp.com", "client123")).props(
                        "unelevated color=indigo-8 dense"
                    ).classes("flex-1")

                with ui.row().classes("justify-center mt-4 gap-1"):
                    ui.label("Don't have an account?").style("color: #6b7280; font-size: 0.85rem")
                    ui.link("Register", "/register").style("color: #a78bfa; font-size: 0.85rem")
