
from sqlite3 import IntegrityError
from venv import logger

from models import Code_ens
from utils import save_to_db
from sqlmodel import Session
from database import engine

def create_code_ens_from_input_cours(code_ens: str):
    """
    Create a code_ens from input_cours.code_ens if it doesn't already exist.
    """
    with Session(engine) as session:
        existing_code_ens = session.get(Code_ens, code_ens)
        if not existing_code_ens:
            new_code_ens = Code_ens(code=code_ens)
            try:
                save_to_db(session, new_code_ens)
                logger.info("Created new code_ens: %s", code_ens)
            except IntegrityError as exc:
                session.rollback()
                logger.exception("Integrity error creating code_ens %s", code_ens)
