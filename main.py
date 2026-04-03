from dotenv import load_dotenv
import os
 
load_dotenv()
 
from models.database import init_db
from ui.main_page import create_main_page
from ui.login_page import create_login_page
from ui.register_page import create_register_page
from ui.client_profile_page import create_client_profile_page
from nicegui import ui
 
init_db()

from pathlib import Path
from nicegui import app as nicegui_app
Path("data/client_pics").mkdir(parents=True, exist_ok=True)
Path("data/client_refs").mkdir(parents=True, exist_ok=True)
Path("data/profile_pics").mkdir(parents=True, exist_ok=True)
Path("data/profile_covers").mkdir(parents=True, exist_ok=True)
nicegui_app.add_static_files('/client_pics', 'data/client_pics')
nicegui_app.add_static_files('/client_refs', 'data/client_refs')
nicegui_app.add_static_files('/profile_pics', 'data/profile_pics')
nicegui_app.add_static_files('/profile_covers', 'data/profile_covers')

create_login_page()
create_register_page()
create_main_page()
create_client_profile_page()
 
ui.run(
    host=os.getenv("APP_HOST", "0.0.0.0"),
    port=int(os.getenv("APP_PORT", 8080)),
    reload=os.getenv("APP_RELOAD", "false").lower() == "true",
    title="AIVP – AI Visual Production",
    storage_secret=os.getenv("STORAGE_SECRET", "aivp-secret-key"),
)
 







