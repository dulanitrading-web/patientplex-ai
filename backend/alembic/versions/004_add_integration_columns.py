"""Add integration columns (Google Ads, Meta Ads, Twilio, Razorpay).

These columns were previously added via ALTER TABLE in main.py startup.
This migration formalizes them so the schema is version-controlled.

Revision ID: 004
Revises: 003
"""

from alembic import op
import sqlalchemy as sa

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- doctors table: Google Ads integration ---
    op.add_column(
        "doctors",
        sa.Column("google_ads_customer_id", sa.String(20), nullable=True),
    )
    op.add_column(
        "doctors",
        sa.Column("google_ads_refresh_token", sa.Text(), nullable=True),
    )
    op.add_column(
        "doctors",
        sa.Column(
            "google_ads_connected",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )

    # --- doctors table: Meta Ads integration ---
    op.add_column(
        "doctors",
        sa.Column("meta_ads_access_token", sa.Text(), nullable=True),
    )
    op.add_column(
        "doctors",
        sa.Column("meta_ads_account_id", sa.String(100), nullable=True),
    )
    op.add_column(
        "doctors",
        sa.Column("meta_ads_page_id", sa.String(100), nullable=True),
    )
    op.add_column(
        "doctors",
        sa.Column(
            "meta_ads_connected",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
    )

    # --- doctors table: Twilio ---
    op.add_column(
        "doctors",
        sa.Column("twilio_phone_number", sa.String(20), nullable=True),
    )

    # --- subscriptions table: Razorpay payment fields ---
    op.add_column(
        "subscriptions",
        sa.Column("razorpay_order_id", sa.String(255), nullable=True),
    )
    op.add_column(
        "subscriptions",
        sa.Column("razorpay_payment_id", sa.String(255), nullable=True),
    )

    # --- Ad platform enum expansion ---
    # These use raw SQL because Alembic can't ALTER TYPE natively
    for val in ("CHATGPT", "INSTAGRAM", "GMB", "WHATSAPP"):
        op.execute(
            sa.text(f"ALTER TYPE ad_platform_enum ADD VALUE IF NOT EXISTS '{val}'")
        )


def downgrade() -> None:
    op.drop_column("subscriptions", "razorpay_payment_id")
    op.drop_column("subscriptions", "razorpay_order_id")
    op.drop_column("doctors", "twilio_phone_number")
    op.drop_column("doctors", "meta_ads_connected")
    op.drop_column("doctors", "meta_ads_page_id")
    op.drop_column("doctors", "meta_ads_account_id")
    op.drop_column("doctors", "meta_ads_access_token")
    op.drop_column("doctors", "google_ads_connected")
    op.drop_column("doctors", "google_ads_refresh_token")
    op.drop_column("doctors", "google_ads_customer_id")
    # Note: Cannot remove enum values in PostgreSQL without dropping/recreating the type
