import os

from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import Engine, create_engine

# Get the database credentials and instance connection name from environment variables
db_user = os.getenv("DATABASE_USER")
db_password = os.getenv("DATABASE_PASSWORD")
db_name = os.getenv("DATABASE_NAME")
instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")


def get_engine(driver: str) -> Engine:
    connector = Connector()

    def get_conn():
        return connector.connect(
            instance_connection_name,
            driver,
            db=db_name,
            password=db_password,
            user=db_user,
            ip_type=IPTypes.PUBLIC,
        )

    engine = create_engine(
        f"postgresql+{driver}://{db_user}:{db_password}@/{db_name}",
        echo=True,
        creator=get_conn,
    )

    return engine
