from collections.abc import Sequence

from sqlmodel import Session, col, select

from app.models.document.document import Document
from app.models.user.base import User


def get_a_document_by_id(session: Session, user: User, document_id: int) -> Document | None:
    return session.exec(select(Document).where(Document.id == document_id, Document.user_id == user.id)).first()


def get_all_template_documents(session: Session) -> Sequence[Document]:
    return session.exec(select(Document).where(col(Document.template) == True)).all()
