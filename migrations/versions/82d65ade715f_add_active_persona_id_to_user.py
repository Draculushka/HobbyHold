"""add active_persona_id to user

Revision ID: 82d65ade715f
Revises: 8f2c5d1e4b3a
Create Date: 2026-03-22 18:50:00.607343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '82d65ade715f'
down_revision: Union[str, Sequence[str], None] = '8f2c5d1e4b3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Определяем диалект БД
    dialect = op.get_context().dialect.name

    op.create_index(op.f('ix_hobbies_created_at'), 'hobbies', ['created_at'], unique=False)
    op.create_index(op.f('ix_hobbies_persona_id'), 'hobbies', ['persona_id'], unique=False)
    op.create_index('ix_hobby_tags_tag_id', 'hobby_tags', ['tag_id'], unique=False)
    op.create_index(op.f('ix_personas_user_id'), 'personas', ['user_id'], unique=False)
    
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('active_persona_id', sa.Integer(), nullable=True))
        
        if dialect == 'postgresql':
            try:
                batch_op.alter_column('is_admin', server_default=None)
                op.execute('ALTER TABLE users ALTER COLUMN is_admin TYPE BOOLEAN USING is_admin::boolean')
                batch_op.alter_column('is_admin', server_default=sa.text('false'))
            except Exception:
                pass
        
        batch_op.alter_column('is_premium',
                   existing_type=sa.BOOLEAN(),
                   nullable=True,
                   existing_server_default=sa.text('false'))
        batch_op.create_foreign_key('fk_user_active_persona', 'personas', ['active_persona_id'], ['id'], use_alter=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('fk_user_active_persona', type_='foreignkey')
        batch_op.alter_column('is_premium',
                   existing_type=sa.BOOLEAN(),
                   nullable=False,
                   existing_server_default=sa.text('false'))
        
        dialect = op.get_context().dialect.name
        if dialect == 'postgresql':
            batch_op.alter_column('is_admin',
                       existing_type=sa.Boolean(),
                       type_=sa.INTEGER(),
                       existing_nullable=True,
                       existing_server_default=sa.text('0'))
        
        batch_op.drop_column('active_persona_id')
    
    op.drop_index(op.f('ix_personas_user_id'), table_name='personas')
    op.drop_index('ix_hobby_tags_tag_id', table_name='hobby_tags')
    op.drop_index(op.f('ix_hobbies_persona_id'), table_name='hobbies')
    op.drop_index(op.f('ix_hobbies_created_at'), table_name='hobbies')
    # ### end Alembic commands ###
