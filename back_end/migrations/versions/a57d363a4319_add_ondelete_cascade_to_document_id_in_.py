"""Add ondelete cascade to document_id in analysis_report

Revision ID: a57d363a4319
Revises: a3952c9adbec
Create Date: 2025-01-23 12:00:46.341185

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'a57d363a4319'
down_revision: Union[str, None] = 'a3952c9adbec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_analysis_report_document_id_document', 'analysis_report', type_='foreignkey')
    op.create_foreign_key('fk_analysis_report_document_id_document', 'analysis_report', 'document', ['document_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('fk_analysis_report_document_id_document', 'analysis_report', type_='foreignkey')
    op.create_foreign_key('fk_analysis_report_document_id_document', 'analysis_report', 'document', ['document_id'], ['id'])
    # ### end Alembic commands ###
