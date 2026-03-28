"""refactor tasks schema and remove tokens

Revision ID: 8c5d2f3b5a1e
Revises: eb5407a27093
Create Date: 2026-03-28 17:10:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "8c5d2f3b5a1e"
down_revision: Union[str, Sequence[str], None] = "eb5407a27093"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("tokens")
    op.drop_column("tasks", "task_id")
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=100),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("now()"),
        existing_nullable=False,
    )
    op.alter_column(
        "tasks",
        "email",
        existing_type=sa.String(length=100),
        nullable=False,
        existing_nullable=True,
    )
    op.alter_column("tasks", "description", existing_type=sa.String(), type_=sa.Text())
    op.alter_column(
        "tasks",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=sa.text("now()"),
        existing_nullable=False,
    )
    op.create_index(op.f("ix_tasks_email"), "tasks", ["email"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_tasks_email"), table_name="tasks")
    op.alter_column(
        "tasks",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=None,
        existing_nullable=False,
    )
    op.alter_column("tasks", "description", existing_type=sa.Text(), type_=sa.String())
    op.alter_column(
        "tasks",
        "email",
        existing_type=sa.String(length=100),
        nullable=True,
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(),
        server_default=None,
        existing_nullable=False,
    )
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=255),
        type_=sa.String(length=100),
        existing_nullable=False,
    )
    op.add_column("tasks", sa.Column("task_id", sa.Integer(), nullable=False, server_default="1"))
    op.alter_column("tasks", "task_id", server_default=None)
    op.create_table(
        "tokens",
        sa.Column("email", sa.String(length=100), nullable=False),
        sa.Column("token", sa.Text(), nullable=True),
        sa.Column("expired", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["email"], ["users.email"]),
        sa.PrimaryKeyConstraint("email"),
    )
