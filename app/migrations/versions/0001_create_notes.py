from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_notes'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'notes',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

def downgrade():
    op.drop_table('notes')
