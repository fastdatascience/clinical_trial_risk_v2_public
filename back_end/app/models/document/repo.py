from collections.abc import Sequence

from sqlmodel import Session, col, select

from app.models.document.document import Document
from app.models.user.base import User
from app.models.user.user_resource_usage import UserResourceUsage


def get_a_document_by_id(session: Session, user: User, document_id: int) -> Document | None:
    return session.exec(select(Document).where(Document.id == document_id, Document.user_id == user.id)).first()


def get_all_template_documents(session: Session) -> Sequence[Document]:
    return session.exec(select(Document).where(col(Document.template) == True)).all()


def get_a_document_template_run_result(session: Session, document_id: int) -> tuple[Document, UserResourceUsage] | None:
    template_document = session.exec(select(Document).where(Document.id == document_id, col(Document.template) == True)).first()

    if not template_document:
        return None

    resource_usage = session.exec(select(UserResourceUsage).where(UserResourceUsage.resource_id == template_document.id)).first()

    if not resource_usage:
        return None

    return template_document, resource_usage
