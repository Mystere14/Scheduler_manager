"""
Database configuration and session management.
"""
import os

from sqlalchemy import create_engine, inspect, text
from sqlmodel import Session, SQLModel
from config import settings
import logging

logger = logging.getLogger(__name__)


engine = create_engine(settings.DATABASE_URL, echo=True)

def init_db():
    """
    Initialize the database by creating all tables.
    """

    #SQLModel.metadata.drop_all(engine) # activate this line to update the database schema (drop all tables and recreate them)

    SQLModel.metadata.create_all(engine)

    # Backfill legacy schemas where create_all() did not add newly introduced columns.
    try:
        inspector = inspect(engine)
        table_names = set(inspector.get_table_names())
        if "room" in table_names:
            room_columns = {col["name"] for col in inspector.get_columns("room")}
            with engine.begin() as conn:
                if "like" not in room_columns:
                    conn.execute(
                        text('ALTER TABLE room ADD COLUMN "like" INTEGER NOT NULL DEFAULT 0')
                    )
                    logger.info('Added missing column room."like"')
                if "dislike" not in room_columns:
                    conn.execute(
                        text("ALTER TABLE room ADD COLUMN dislike INTEGER NOT NULL DEFAULT 0")
                    )
                    logger.info("Added missing column room.dislike")

        if "notifications" in table_names:
            notif_columns = {col["name"] for col in inspector.get_columns("notifications")}
            with engine.begin() as conn:
                if "sent_at" not in notif_columns:
                    conn.execute(
                        text(
                            "ALTER TABLE notifications ADD COLUMN sent_at TIMESTAMP WITHOUT TIME ZONE "
                            "NOT NULL DEFAULT CURRENT_TIMESTAMP"
                        )
                    )
                    logger.info("Added missing column notifications.sent_at")
                if "ip_address" not in notif_columns:
                    conn.execute(
                        text("ALTER TABLE notifications ADD COLUMN ip_address VARCHAR")
                    )
                    logger.info("Added missing column notifications.ip_address")

        # Legacy databases may have an older PostgreSQL enum without GUEST.
        with engine.begin() as conn:
            conn.execute(text("ALTER TYPE role ADD VALUE IF NOT EXISTS 'GUEST'"))
    except Exception:
        logger.exception("Error while backfilling room schema")
    
    # User seeds to populate initial users
    try:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        import bcrypt
        from sqlmodel import Session, select
        from models import User, Role
        
        def seed_users_inline(session: Session):
            users = [
                {"username": "responsable", "password": "responsable123", "role": Role.RESPONSABLE},
                {"username": "technicien", "password": "technicien123", "role": Role.TECHNICIEN}
            ]
            for user_data in users:
                db_user = session.exec(select(User).where(User.username == user_data["username"])).first()
                password_bytes = user_data["password"].encode('utf-8')
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
                if not db_user:
                    new_user = User(username=user_data["username"], password_hash=hashed_password, role=user_data["role"])
                    session.add(new_user)
                    logger.info("User created: %s", user_data['username'])
            session.commit()
        
        with Session(engine) as session:
            seed_users_inline(session)
    except Exception as e:
        logger.exception("Error during user seed")


def get_session():
    """
    Provide a transactional scope around a series of operations.
    """
    with Session(engine) as session:
        yield session
