import dataclasses
import os

from dotenv import load_dotenv

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=CURRENT_DIR + "/.env")


@dataclasses.dataclass
class ProducerSettings:
    HOST: str = os.getenv("PRODUCER_HOST")
    PORT: int = os.getenv("PRODUCER_PORT")
    DB_NAME: str = os.getenv("PRODUCER_DB_NAME")
    USER: str = os.getenv("PRODUCER_USER")
    PASSWORD: str = os.getenv("PRODUCER_PASSWORD")
    
    def get_connection_string(self) -> str:
        return f"host={self.HOST} port={self.PORT} dbname={self.DB_NAME} user={self.USER} password={self.PASSWORD}"


@dataclasses.dataclass
class ConsumerSettings:
    HOST: str = os.getenv("CONSUMER_HOST")
    PORT: int = os.getenv("CONSUMER_PORT")
    DB_NAME: str = os.getenv("CONSUMER_DB_NAME")
    USER: str = os.getenv("CONSUMER_USER")
    PASSWORD: str = os.getenv("CONSUMER_PASSWORD")
    
    def get_connection_string(self) -> str:
        return f"host={self.HOST} port={self.PORT} dbname={self.DB_NAME} user={self.USER} password={self.PASSWORD}"


producer_settings = ProducerSettings()
consumer_settings = ConsumerSettings()
