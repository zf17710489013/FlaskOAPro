"""empty message

Revision ID: c7c1c01976c7
Revises: 
Create Date: 2020-04-13 15:21:07.331652

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7c1c01976c7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('department',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('d_name', sa.String(length=32), nullable=True),
    sa.Column('d_description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('news',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=32), nullable=True),
    sa.Column('author', sa.String(length=32), nullable=True),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('public_time', sa.Date(), nullable=True),
    sa.Column('picture', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('permission',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('p_name', sa.String(length=32), nullable=True),
    sa.Column('p_description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('position',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('p_name', sa.String(length=32), nullable=True),
    sa.Column('p_description', sa.Text(), nullable=True),
    sa.Column('p_level', sa.Integer(), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['department_id'], ['department.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('person',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('password', sa.String(length=32), nullable=True),
    sa.Column('nick_name', sa.String(length=32), nullable=True),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('gender', sa.String(length=16), nullable=True),
    sa.Column('photo', sa.String(length=128), nullable=True),
    sa.Column('phone', sa.String(length=16), nullable=True),
    sa.Column('email', sa.String(length=32), nullable=True),
    sa.Column('address', sa.Text(), nullable=True),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('position_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['position_id'], ['position.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('pos_per',
    sa.Column('pos_id', sa.Integer(), nullable=True),
    sa.Column('per_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['per_id'], ['permission.id'], ),
    sa.ForeignKeyConstraint(['pos_id'], ['position.id'], )
    )
    op.create_table('attendance',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('reason', sa.Text(), nullable=True),
    sa.Column('a_type', sa.String(length=32), nullable=True),
    sa.Column('a_date', sa.Float(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('examine', sa.String(length=32), nullable=True),
    sa.Column('a_status', sa.String(length=32), nullable=True),
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['person_id'], ['person.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('attendance')
    op.drop_table('pos_per')
    op.drop_table('person')
    op.drop_table('position')
    op.drop_table('permission')
    op.drop_table('news')
    op.drop_table('department')
    # ### end Alembic commands ###
