"""
Manual migration: rename columns to PascalCase to match model mappings.
This migration performs safe column renames. BACKUP your DB before running.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_map_pascal'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Users table: rename columns
    op.alter_column('users', 'id', new_column_name='Id', existing_type=sa.String(length=36))
    op.alter_column('users', 'username', new_column_name='Username', existing_type=sa.String(length=50))
    op.alter_column('users', 'email', new_column_name='Email', existing_type=sa.String(length=100))
    # If PasswordHash doesn't exist, rename password_hash -> PasswordHash
    op.alter_column('users', 'password_hash', new_column_name='PasswordHash', existing_type=sa.String(length=200))
    op.alter_column('users', 'full_name', new_column_name='FullName', existing_type=sa.String(length=100))
    op.alter_column('users', 'is_deleted', new_column_name='IsDeleted', existing_type=sa.Boolean())
    op.alter_column('users', 'email_confirmed', new_column_name='EmailConfirmed', existing_type=sa.Boolean())
    op.alter_column('users', 'email_confirmation_token', new_column_name='EmailConfirmationToken', existing_type=sa.String(length=200))
    op.alter_column('users', 'email_confirmation_expiry', new_column_name='EmailConfirmationExpiry', existing_type=sa.DateTime())
    op.alter_column('users', 'role', new_column_name='Role', existing_type=sa.String(length=50))

    # Refresh tokens table: rename columns
    op.alter_column('refresh_tokens', 'token', new_column_name='Token', existing_type=sa.String(length=191))
    op.alter_column('refresh_tokens', 'user_id', new_column_name='UserId', existing_type=sa.String(length=36))
    op.alter_column('refresh_tokens', 'expires', new_column_name='Expires', existing_type=sa.DateTime())
    op.alter_column('refresh_tokens', 'created_at', new_column_name='CreatedAt', existing_type=sa.DateTime())
    op.alter_column('refresh_tokens', 'is_revoked', new_column_name='IsRevoked', existing_type=sa.Boolean())


def downgrade():
    # Reverse renames
    op.alter_column('refresh_tokens', 'Token', new_column_name='token', existing_type=sa.String(length=191))
    op.alter_column('refresh_tokens', 'UserId', new_column_name='user_id', existing_type=sa.String(length=36))
    op.alter_column('refresh_tokens', 'Expires', new_column_name='expires', existing_type=sa.DateTime())
    op.alter_column('refresh_tokens', 'CreatedAt', new_column_name='created_at', existing_type=sa.DateTime())
    op.alter_column('refresh_tokens', 'IsRevoked', new_column_name='is_revoked', existing_type=sa.Boolean())

    op.alter_column('users', 'Id', new_column_name='id', existing_type=sa.String(length=36))
    op.alter_column('users', 'Username', new_column_name='username', existing_type=sa.String(length=50))
    op.alter_column('users', 'Email', new_column_name='email', existing_type=sa.String(length=100))
    op.alter_column('users', 'PasswordHash', new_column_name='password_hash', existing_type=sa.String(length=200))
    op.alter_column('users', 'FullName', new_column_name='full_name', existing_type=sa.String(length=100))
    op.alter_column('users', 'IsDeleted', new_column_name='is_deleted', existing_type=sa.Boolean())
    op.alter_column('users', 'EmailConfirmed', new_column_name='email_confirmed', existing_type=sa.Boolean())
    op.alter_column('users', 'EmailConfirmationToken', new_column_name='email_confirmation_token', existing_type=sa.String(length=200))
    op.alter_column('users', 'EmailConfirmationExpiry', new_column_name='email_confirmation_expiry', existing_type=sa.DateTime())
    op.alter_column('users', 'Role', new_column_name='role', existing_type=sa.String(length=50))
