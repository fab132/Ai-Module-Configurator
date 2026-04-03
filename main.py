from dotenv import load_dotenv
import os
 
load_dotenv()
 
from models.database import init_db
from ui.main_page import create_main_page
from ui.login_page import create_login_page
from ui.register_page import create_register_page
from nicegui import ui
 
init_db()

from pathlib import Path
from nicegui import app as nicegui_app
Path("data/client_pics").mkdir(parents=True, exist_ok=True)
nicegui_app.add_static_files('/client_pics', 'data/client_pics')

create_login_page()
create_register_page()
create_main_page()
 
ui.run(
    host=os.getenv("APP_HOST", "0.0.0.0"),
    port=int(os.getenv("APP_PORT", 8080)),
    reload=os.getenv("APP_RELOAD", "false").lower() == "true",
    title="AIVP – AI Visual Production",
    storage_secret=os.getenv("STORAGE_SECRET", "aivp-secret-key"),
)
 







