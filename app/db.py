from sqlmodel import SQLModel, create_engine

DATABASE_URL = "sqlite:///./photo_manager.db"

engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
