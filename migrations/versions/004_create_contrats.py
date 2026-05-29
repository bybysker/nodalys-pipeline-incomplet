"""Crée la table contrats.

Revision ID: 004
Revises: 003

Cette table était manquante au depart
"""

from alembic import op
import sqlalchemy as sa


revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "contrats",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("client_id", sa.Integer, sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("session_id", sa.Integer, sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column("statut", sa.String(50), nullable=False),
        sa.Column("montant_ht", sa.Numeric(10, 2), nullable=False),
        sa.Column("date_signature", sa.Date, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("contrats")
