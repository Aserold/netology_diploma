from dotenv import load_dotenv

import os

load_dotenv()

DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_USER = os.environ.get('DB_USER')
