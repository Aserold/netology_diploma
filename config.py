from dotenv import load_dotenv

import os

load_dotenv()

DB_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
DB_USER = os.environ.get('POSTGRES_USER')
