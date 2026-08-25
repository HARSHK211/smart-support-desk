import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:Harshk%4021@localhost:3306/smart_support"
)