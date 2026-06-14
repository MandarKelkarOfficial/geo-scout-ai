"""Seed real estate data

Revision ID: 05f9fccea011
Revises: 33ada7a74a78
Create Date: 2026-06-14 20:01:45.532508

"""
from typing import Sequence, Union
import json
import os
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '05f9fccea011'
down_revision: Union[str, Sequence[str], None] = '33ada7a74a78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    data_path = os.path.join(os.path.dirname(__file__), '../../app/services/data/sample_listings.json')
    if not os.path.exists(data_path):
        return
        
    with open(data_path, 'r') as f:
        listings = json.load(f)
        
    mapped_listings = []
    for l in listings:
        mapped_listings.append({
            "title": l.get("title"),
            "price": l.get("price"),
            "currency": l.get("currency", "INR"),
            "area_sqft": l.get("area_sqft"),
            "location_label": l.get("location"),
            "dealer_name": l.get("dealer_name"),
            "dealer_contact": l.get("dealer_contact"),
            "source": "manual"
        })

    real_estate_listings = table('real_estate_listings',
        column('title', sa.String),
        column('price', sa.Float),
        column('currency', sa.String),
        column('area_sqft', sa.Float),
        column('location_label', sa.String),
        column('dealer_name', sa.String),
        column('dealer_contact', sa.String),
        column('source', sa.String)
    )
    
    if mapped_listings:
        op.bulk_insert(real_estate_listings, mapped_listings)


def downgrade() -> None:
    op.execute("DELETE FROM real_estate_listings WHERE source = 'manual'")
