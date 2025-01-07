import reflex as rx
from decouple import config

DATABASE_URL = config("DATABASE_URL", default="none_connection")

config = rx.Config(
    app_name="fullstackgpt",
    assets_dir="assets",
    db_url=DATABASE_URL,
    
)
