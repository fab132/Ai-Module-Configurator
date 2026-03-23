from dotenv import load_dotenv
import os

load_dotenv()

from models.database import init_db
from ui.main_page import create_main_page
from nicegui import ui

init_db()

create_main_page()

ui.run(
    host=os.getenv("APP_HOST", "0.0.0.0"),
    port=int(os.getenv("APP_PORT", 8080)),
    reload=os.getenv("APP_RELOAD", "false").lower() == "true",
    title="AIVP – AI Visual Production",
)
