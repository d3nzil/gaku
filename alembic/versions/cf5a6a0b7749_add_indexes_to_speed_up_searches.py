"""Add indexes to speed up searches

Revision ID: cf5a6a0b7749
Revises: cba6f81e6f93
Create Date: 2025-02-01 15:40:52.128275

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "cf5a6a0b7749"
down_revision: Union[str, None] = "cba6f81e6f93"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        "ix_card_source_source_id", "card_source", ["source_id"], unique=False
    )
    op.create_index("ix_fsrs_card_id", "fsrs", ["card_id"], unique=False)
    op.create_index("ix_fsrs_due_date", "fsrs", ["due_date"], unique=False)
    op.create_index(
        "ix_recent_mistakes_mistake_timestamp",
        "recent_mistakes",
        ["mistake_timestamp"],
        unique=False,
    )
    op.create_index("ix_test_cards_card_id", "test_cards", ["card_id"], unique=False)
    op.create_index(
        "ix_test_cards_card_type", "test_cards", ["card_type"], unique=False
    )
    op.create_index("ix_test_cards_data", "test_cards", ["data"], unique=False)
    op.create_index("ix_test_cards_key", "test_cards", ["key"], unique=False)
    op.create_index("ix_test_cards_position", "test_cards", ["position"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("ix_test_cards_position", table_name="test_cards")
    op.drop_index("ix_test_cards_key", table_name="test_cards")
    op.drop_index("ix_test_cards_data", table_name="test_cards")
    op.drop_index("ix_test_cards_card_type", table_name="test_cards")
    op.drop_index("ix_test_cards_card_id", table_name="test_cards")
    op.drop_index("ix_recent_mistakes_mistake_timestamp", table_name="recent_mistakes")
    op.drop_index("ix_fsrs_due_date", table_name="fsrs")
    op.drop_index("ix_fsrs_card_id", table_name="fsrs")
    op.drop_index("ix_card_source_source_id", table_name="card_source")
    # ### end Alembic commands ###
