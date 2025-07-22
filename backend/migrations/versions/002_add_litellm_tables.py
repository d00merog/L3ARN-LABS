"""Add LiteLLM tables for community API key donation system

Revision ID: 002_add_litellm_tables
Revises: 0001_create_quiz_results_table
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_litellm_tables'
down_revision = '0001_create_quiz_results_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    api_key_provider_enum = postgresql.ENUM(
        'openai', 'anthropic', 'google', 'cohere', 'replicate', 'huggingface', 'azure', 'bedrock',
        name='apikeyenum',
        create_type=False
    )
    api_key_provider_enum.create(op.get_bind())
    
    api_key_status_enum = postgresql.ENUM(
        'active', 'inactive', 'expired', 'rate_limited', 'error',
        name='apikeystatus',
        create_type=False
    )
    api_key_status_enum.create(op.get_bind())
    
    # Create donated_api_keys table
    op.create_table('donated_api_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('donor_user_id', sa.Integer(), nullable=True),
        sa.Column('provider', api_key_provider_enum, nullable=False),
        sa.Column('key_hash', sa.String(), nullable=False),
        sa.Column('encrypted_key', sa.Text(), nullable=False),
        sa.Column('nickname', sa.String(length=100), nullable=True),
        sa.Column('monthly_limit', sa.Float(), nullable=True),
        sa.Column('usage_this_month', sa.Float(), nullable=True),
        sa.Column('total_usage', sa.Float(), nullable=True),
        sa.Column('status', api_key_status_enum, nullable=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )
    op.create_index(op.f('ix_donated_api_keys_donor_user_id'), 'donated_api_keys', ['donor_user_id'], unique=False)
    op.create_index(op.f('ix_donated_api_keys_id'), 'donated_api_keys', ['id'], unique=False)
    
    # Create api_key_usage table
    op.create_table('api_key_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('api_key_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('request_type', sa.String(length=50), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_api_key_usage_api_key_id'), 'api_key_usage', ['api_key_id'], unique=False)
    op.create_index(op.f('ix_api_key_usage_id'), 'api_key_usage', ['id'], unique=False)
    op.create_index(op.f('ix_api_key_usage_user_id'), 'api_key_usage', ['user_id'], unique=False)
    
    # Create user_contributions table
    op.create_table('user_contributions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('total_donated_usd', sa.Float(), nullable=True),
        sa.Column('credits_earned', sa.Float(), nullable=True),
        sa.Column('credits_used', sa.Float(), nullable=True),
        sa.Column('credits_remaining', sa.Float(), nullable=True),
        sa.Column('contribution_tier', sa.String(length=20), nullable=True),
        sa.Column('monthly_usage_limit', sa.Float(), nullable=True),
        sa.Column('priority_level', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_contributions_id'), 'user_contributions', ['id'], unique=False)
    op.create_index(op.f('ix_user_contributions_user_id'), 'user_contributions', ['user_id'], unique=True)
    
    # Create model_load_balancer table
    op.create_table('model_load_balancer',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('provider_weights', sa.JSON(), nullable=True),
        sa.Column('fallback_order', sa.JSON(), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('min_healthy_keys', sa.Integer(), nullable=True),
        sa.Column('health_check_interval', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('model_name')
    )
    op.create_index(op.f('ix_model_load_balancer_id'), 'model_load_balancer', ['id'], unique=False)
    
    # Create ai_model_requests table
    op.create_table('ai_model_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('api_key_id', sa.Integer(), nullable=True),
        sa.Column('request_type', sa.String(length=50), nullable=True),
        sa.Column('input_tokens', sa.Integer(), nullable=True),
        sa.Column('output_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('user_agent', sa.String(length=200), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_model_requests_api_key_id'), 'ai_model_requests', ['api_key_id'], unique=False)
    op.create_index(op.f('ix_ai_model_requests_id'), 'ai_model_requests', ['id'], unique=False)
    op.create_index(op.f('ix_ai_model_requests_session_id'), 'ai_model_requests', ['session_id'], unique=False)
    op.create_index(op.f('ix_ai_model_requests_user_id'), 'ai_model_requests', ['user_id'], unique=False)
    
    # Create ai_model_health table
    op.create_table('ai_model_health',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', api_key_provider_enum, nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('response_time_avg', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('error_count', sa.Integer(), nullable=True),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.Column('last_check', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_model_health_id'), 'ai_model_health', ['id'], unique=False)
    
    # Create composite indexes for better performance
    op.create_index('idx_donated_keys_provider_status', 'donated_api_keys', ['provider', 'status'], unique=False)
    op.create_index('idx_usage_user_date', 'api_key_usage', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_requests_user_date', 'ai_model_requests', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_health_provider_model', 'ai_model_health', ['provider', 'model_name'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_health_provider_model', table_name='ai_model_health')
    op.drop_index('idx_requests_user_date', table_name='ai_model_requests')
    op.drop_index('idx_usage_user_date', table_name='api_key_usage')
    op.drop_index('idx_donated_keys_provider_status', table_name='donated_api_keys')
    
    # Drop tables
    op.drop_table('ai_model_health')
    op.drop_table('ai_model_requests')
    op.drop_table('model_load_balancer')
    op.drop_table('user_contributions')
    op.drop_table('api_key_usage')
    op.drop_table('donated_api_keys')
    
    # Drop ENUM types
    op.execute('DROP TYPE apikeystatus')
    op.execute('DROP TYPE apikeyenum')