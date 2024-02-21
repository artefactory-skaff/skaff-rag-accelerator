import os

from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Private key used to generate the JWT tokens for secure authentication
SECRET_KEY = os.getenv("SECRET_KEY", "default_unsecure_key")

# Algorithm used to generate JWT tokens
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# If the API runs in admin mode, it will allow the creation of new users
ADMIN_MODE = bool(int(os.getenv("ADMIN_MODE", False)))
