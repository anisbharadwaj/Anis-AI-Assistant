from dotenv import load_dotenv
from config.settings import Settings

load_dotenv()

def create_app_settings():
    return Settings()
