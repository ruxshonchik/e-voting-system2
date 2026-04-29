"""initial

Revision ID: e09bbe163f79
Revises:
Create Date: 2026-04-07 13:03:11.481541

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'e09bbe163f79'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # users jadvali
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='user'),
        sa.Column('avatar', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # polls jadvali
    op.create_table(
        'polls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(length=10), nullable=False, server_default='draft'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_polls_id', 'polls', ['id'], unique=False)

    # options jadvali
    op.create_table(
        'options',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('poll_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(length=255), nullable=False),
        sa.Column('vote_count', sa.Integer(), nullable=False, server_default='0'),
        sa.ForeignKeyConstraint(['poll_id'], ['polls.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_options_id', 'options', ['id'], unique=False)
    op.create_index('ix_options_poll_id', 'options', ['poll_id'], unique=False)

    # votes jadvali
    op.create_table(
        'votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('poll_id', sa.Integer(), nullable=False),
        sa.Column('option_id', sa.Integer(), nullable=False),
        sa.Column('voted_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['option_id'], ['options.id']),
        sa.ForeignKeyConstraint(['poll_id'], ['polls.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'poll_id', name='uq_votes_user_poll'),
    )
    op.create_index('ix_votes_id', 'votes', ['id'], unique=False)
    op.create_index('ix_votes_user_id', 'votes', ['user_id'], unique=False)
    op.create_index('ix_votes_poll_id', 'votes', ['poll_id'], unique=False)


def downgrade() -> None:
    op.drop_table('votes')
    op.drop_table('options')
    op.drop_table('polls')
    op.drop_table('users')
