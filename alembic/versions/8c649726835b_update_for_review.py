"""update for review

Revision ID: 8c649726835b
Revises: 2e7226290fd8
Create Date: 2026-04-01 07:34:40.775901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql # Crucial for Postgres Enums

# revision identifiers, used by Alembic.
revision: str = '8c649726835b'
down_revision: Union[str, Sequence[str], None] = '2e7226290fd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create the Enum type manually in Postgres
    review_status = postgresql.ENUM('PENDING', 'APPROVED', 'REJECTED', 'FLAGGED', name='reviewstatus')
    review_status.create(op.get_bind(), checkfirst=True)

    # 2. Add columns
    op.add_column('reviews', sa.Column('owner_reply_at', sa.DateTime(), nullable=True))
    op.add_column('reviews', sa.Column('updated_at', sa.DateTime(), nullable=True))
    
    # We use create_type=False because we just created it manually above
    op.add_column('reviews', sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', 'FLAGGED', name='reviewstatus', create_type=False), nullable=True))
    
    op.add_column('reviews', sa.Column('moderated_at', sa.DateTime(), nullable=True))
    op.add_column('reviews', sa.Column('moderator_id', sa.Integer(), nullable=True))
    
    # Handle constraints and alterations
    # Note: If you have existing reviews, setting user_id to nullable=False might fail 
    # unless you have a user assigned to every review already.
    op.alter_column('reviews', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
               
    op.drop_constraint('reviews_user_id_fkey', 'reviews', type_='foreignkey')
    op.create_foreign_key(None, 'reviews', 'users', ['moderator_id'], ['id'])
    op.create_foreign_key(None, 'reviews', 'users', ['user_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    # 1. Drop constraints
    op.drop_constraint(None, 'reviews', type_='foreignkey')
    op.drop_constraint(None, 'reviews', type_='foreignkey')
    
    # 2. Revert columns
    op.create_foreign_key('reviews_user_id_fkey', 'reviews', 'users', ['user_id'], ['id'])
    op.alter_column('reviews', 'user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
               
    op.drop_column('reviews', 'moderator_id')
    op.drop_column('reviews', 'moderated_at')
    op.drop_column('reviews', 'status')
    op.drop_column('reviews', 'updated_at')
    op.drop_column('reviews', 'owner_reply_at')

    # 3. Drop the Enum type manually
    review_status = postgresql.ENUM('PENDING', 'APPROVED', 'REJECTED', 'FLAGGED', name='reviewstatus')
    review_status.drop(op.get_bind(), checkfirst=True)