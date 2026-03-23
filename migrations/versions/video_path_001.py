"""add video path to hobby

Revision ID: video_path_001
Revises: fb6211449568
Create Date: 2026-03-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'video_path_001'
down_revision = 'fb6211449568'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('hobbies', sa.Column('video_path', sa.String(), nullable=True))

def downgrade():
    op.drop_column('hobbies', 'video_path')
