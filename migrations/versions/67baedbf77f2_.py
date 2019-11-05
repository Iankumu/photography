"""empty message

Revision ID: 67baedbf77f2
Revises: 86feb43fe7f6
Create Date: 2019-11-05 13:51:53.850189

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67baedbf77f2'
down_revision = '86feb43fe7f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_first_name', table_name='user')
    op.drop_index('ix_user_second_name', table_name='user')
    op.drop_table('user')
    op.drop_table('roles_users')
    op.drop_table('role')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('role',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=80), nullable=True),
    sa.Column('description', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('roles_users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=True),
    sa.Column('role_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=255), nullable=True),
    sa.Column('password', sa.VARCHAR(length=255), nullable=True),
    sa.Column('first_name', sa.VARCHAR(length=64), nullable=True),
    sa.Column('second_name', sa.VARCHAR(length=64), nullable=True),
    sa.Column('email', sa.VARCHAR(length=255), nullable=False),
    sa.Column('phone_number', sa.VARCHAR(length=20), nullable=False),
    sa.Column('active', sa.BOOLEAN(), nullable=True),
    sa.Column('date_created', sa.DATETIME(), nullable=True),
    sa.CheckConstraint('active IN (0, 1)'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_index('ix_user_second_name', 'user', ['second_name'], unique=1)
    op.create_index('ix_user_first_name', 'user', ['first_name'], unique=1)
    # ### end Alembic commands ###
