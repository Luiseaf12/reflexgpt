from typing import List
import reflex as rx
from datetime import datetime, timezone
from sqlmodel import Field, Relationship, SQLModel, create_engine
import sqlalchemy


class ChatSession(rx.Model, table=True):

    def get_utc_now() -> datetime:
        return datetime.now(timezone.utc)

    messages: List["ChatSessionMessageModel"] = Relationship(back_populates="session")

    created_at: datetime = Field(
        default_factory=get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False,
    )

    updated_at: datetime = Field(
        default_factory=get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": sqlalchemy.func.now(),
            "onupdate": sqlalchemy.func.now(),
        },
        nullable=False,
    )


class ChatSessionMessageModel(rx.Model, table=True):
    id: int = Field(default=None, primary_key=True)
    session_id: int = Field(default=None, foreign_key="chatsession.id")
    session: ChatSession = Relationship(back_populates="messages")
    content: str
    role: str

    def get_utc_now() -> datetime:
        return datetime.now(timezone.utc)

    created_at: datetime = Field(
        default_factory=get_utc_now,
        sa_type=sqlalchemy.DateTime(timezone=True),
        sa_column_kwargs={"server_default": sqlalchemy.func.now()},
        nullable=False,
    )




# from decouple import config
# def db_init():
#     """
#     Inicializa la base de datos y crea todas las tablas necesarias.
#     Fuerza el uso de PostgreSQL y evita la creación de reflex.db
#     """
#     try:
#         DATABASE_URL = config('DATABASE_URL', strict=True)
#         if not DATABASE_URL.startswith('postgresql://'):
#             raise ValueError("La URL de la base de datos debe ser PostgreSQL")
        
#         engine = create_engine(
#             DATABASE_URL,
#             echo=True,  # Establece en False en producción
#             connect_args={"sslmode": "require"}
#         )
        
#         # Crear todas las tablas
#         SQLModel.metadata.create_all(engine)
#         print(f"✅ Base de datos PostgreSQL inicializada correctamente")
        
#         return engine
        
#     except UndefinedValueError:
#         raise ValueError("❌ DATABASE_URL no está definida en el archivo .env")
#     except Exception as e:
#         raise ValueError(f"❌ Error al inicializar la base de datos: {str(e)}")

