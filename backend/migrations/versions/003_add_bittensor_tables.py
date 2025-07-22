"""Add Bittensor tables for decentralized AI network integration

Revision ID: 003_add_bittensor_tables
Revises: 002_add_litellm_tables
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_add_bittensor_tables'
down_revision = '002_add_litellm_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    subnet_type_enum = postgresql.ENUM(
        'text_prompting', 'compute', 'educational', 'image_generation', 'translation', 'storage',
        name='subnettype',
        create_type=False
    )
    subnet_type_enum.create(op.get_bind())
    
    validation_type_enum = postgresql.ENUM(
        'content_quality', 'fact_checking', 'educational_value', 'code_correctness', 'assignment_grading',
        name='validationtype',
        create_type=False
    )
    validation_type_enum.create(op.get_bind())
    
    # Create bittensor_nodes table
    op.create_table('bittensor_nodes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('node_type', sa.String(length=20), nullable=False),
        sa.Column('hotkey', sa.String(length=100), nullable=False),
        sa.Column('coldkey', sa.String(length=100), nullable=False),
        sa.Column('netuid', sa.Integer(), nullable=False),
        sa.Column('subnet_type', subnet_type_enum, nullable=False),
        sa.Column('uid', sa.Integer(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('port', sa.Integer(), nullable=True),
        sa.Column('stake', sa.Float(), nullable=True),
        sa.Column('trust', sa.Float(), nullable=True),
        sa.Column('consensus', sa.Float(), nullable=True),
        sa.Column('incentive', sa.Float(), nullable=True),
        sa.Column('dividends', sa.Float(), nullable=True),
        sa.Column('emission', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_update', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('hotkey')
    )
    op.create_index(op.f('ix_bittensor_nodes_id'), 'bittensor_nodes', ['id'], unique=False)
    
    # Create bittensor_queries table
    op.create_table('bittensor_queries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('query_type', sa.String(length=50), nullable=False),
        sa.Column('input_data', sa.JSON(), nullable=False),
        sa.Column('target_miners', sa.JSON(), nullable=True),
        sa.Column('responses_received', sa.Integer(), nullable=True),
        sa.Column('consensus_score', sa.Float(), nullable=True),
        sa.Column('final_result', sa.JSON(), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('cost_tao', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['node_id'], ['bittensor_nodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bittensor_queries_id'), 'bittensor_queries', ['id'], unique=False)
    op.create_index(op.f('ix_bittensor_queries_session_id'), 'bittensor_queries', ['session_id'], unique=False)
    op.create_index(op.f('ix_bittensor_queries_user_id'), 'bittensor_queries', ['user_id'], unique=False)
    
    # Create bittensor_responses table
    op.create_table('bittensor_responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('query_id', sa.Integer(), nullable=False),
        sa.Column('miner_uid', sa.Integer(), nullable=False),
        sa.Column('miner_hotkey', sa.String(length=100), nullable=False),
        sa.Column('response_data', sa.JSON(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('trust_score', sa.Float(), nullable=True),
        sa.Column('incentive_score', sa.Float(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=True),
        sa.Column('weight_assigned', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['query_id'], ['bittensor_queries.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bittensor_responses_id'), 'bittensor_responses', ['id'], unique=False)
    
    # Create bittensor_validations table
    op.create_table('bittensor_validations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('node_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('content_id', sa.Integer(), nullable=True),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('validation_type', validation_type_enum, nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('original_content', sa.Text(), nullable=False),
        sa.Column('validation_prompt', sa.Text(), nullable=False),
        sa.Column('miner_responses', sa.JSON(), nullable=False),
        sa.Column('consensus_result', sa.JSON(), nullable=False),
        sa.Column('consensus_score', sa.Float(), nullable=False),
        sa.Column('validator_count', sa.Integer(), nullable=False),
        sa.Column('agreement_ratio', sa.Float(), nullable=False),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('fact_accuracy', sa.Float(), nullable=True),
        sa.Column('educational_value', sa.Float(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=True),
        sa.Column('approval_threshold', sa.Float(), nullable=True),
        sa.Column('tao_cost', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['node_id'], ['bittensor_nodes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bittensor_validations_id'), 'bittensor_validations', ['id'], unique=False)
    
    # Create tao_transactions table
    op.create_table('tao_transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('amount_tao', sa.Float(), nullable=False),
        sa.Column('balance_before', sa.Float(), nullable=False),
        sa.Column('balance_after', sa.Float(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=True),
        sa.Column('activity_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('bittensor_block', sa.Integer(), nullable=True),
        sa.Column('transaction_hash', sa.String(length=64), nullable=True),
        sa.Column('is_confirmed', sa.Boolean(), nullable=True),
        sa.Column('confirmation_block', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tao_transactions_id'), 'tao_transactions', ['id'], unique=False)
    op.create_index(op.f('ix_tao_transactions_user_id'), 'tao_transactions', ['user_id'], unique=False)
    
    # Create user_tao_wallets table
    op.create_table('user_tao_wallets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('hotkey', sa.String(length=100), nullable=True),
        sa.Column('coldkey', sa.String(length=100), nullable=True),
        sa.Column('current_balance', sa.Float(), nullable=True),
        sa.Column('total_earned', sa.Float(), nullable=True),
        sa.Column('total_spent', sa.Float(), nullable=True),
        sa.Column('pending_transactions', sa.Float(), nullable=True),
        sa.Column('last_sync_block', sa.Integer(), nullable=True),
        sa.Column('last_sync_time', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_tao_wallets_id'), 'user_tao_wallets', ['id'], unique=False)
    op.create_index(op.f('ix_user_tao_wallets_user_id'), 'user_tao_wallets', ['user_id'], unique=True)
    
    # Create bittensor_subnets table
    op.create_table('bittensor_subnets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('netuid', sa.Integer(), nullable=False),
        sa.Column('subnet_type', subnet_type_enum, nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('repository_url', sa.String(length=200), nullable=True),
        sa.Column('registration_cost', sa.Float(), nullable=True),
        sa.Column('burn_cost', sa.Float(), nullable=True),
        sa.Column('max_validators', sa.Integer(), nullable=True),
        sa.Column('max_miners', sa.Integer(), nullable=True),
        sa.Column('immunity_period', sa.Integer(), nullable=True),
        sa.Column('min_allowed_weights', sa.Integer(), nullable=True),
        sa.Column('max_weights_limit', sa.Float(), nullable=True),
        sa.Column('tempo', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('netuid')
    )
    op.create_index(op.f('ix_bittensor_subnets_id'), 'bittensor_subnets', ['id'], unique=False)
    
    # Create educational_mining table
    op.create_table('educational_mining',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=False),
        sa.Column('difficulty_level', sa.String(length=20), nullable=False),
        sa.Column('completion_time_seconds', sa.Integer(), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=True),
        sa.Column('validation_score', sa.Float(), nullable=True),
        sa.Column('base_reward_tao', sa.Float(), nullable=False),
        sa.Column('multiplier', sa.Float(), nullable=True),
        sa.Column('final_reward_tao', sa.Float(), nullable=False),
        sa.Column('is_validated', sa.Boolean(), nullable=True),
        sa.Column('validation_id', sa.Integer(), nullable=True),
        sa.Column('mined_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('validated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['validation_id'], ['bittensor_validations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_educational_mining_id'), 'educational_mining', ['id'], unique=False)
    op.create_index(op.f('ix_educational_mining_user_id'), 'educational_mining', ['user_id'], unique=False)
    
    # Create bittensor_network_health table
    op.create_table('bittensor_network_health',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('netuid', sa.Integer(), nullable=False),
        sa.Column('total_miners', sa.Integer(), nullable=True),
        sa.Column('active_miners', sa.Integer(), nullable=True),
        sa.Column('total_validators', sa.Integer(), nullable=True),
        sa.Column('active_validators', sa.Integer(), nullable=True),
        sa.Column('network_difficulty', sa.Float(), nullable=True),
        sa.Column('total_stake', sa.Float(), nullable=True),
        sa.Column('emission_rate', sa.Float(), nullable=True),
        sa.Column('average_trust', sa.Float(), nullable=True),
        sa.Column('average_consensus', sa.Float(), nullable=True),
        sa.Column('block_time_avg', sa.Float(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('response_time_avg', sa.Float(), nullable=True),
        sa.Column('health_score', sa.Float(), nullable=True),
        sa.Column('checked_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bittensor_network_health_id'), 'bittensor_network_health', ['id'], unique=False)
    
    # Create composite indexes for better performance
    op.create_index('idx_queries_user_created', 'bittensor_queries', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_responses_query_miner', 'bittensor_responses', ['query_id', 'miner_uid'], unique=False)
    op.create_index('idx_validations_content_type', 'bittensor_validations', ['content_type', 'validation_type'], unique=False)
    op.create_index('idx_transactions_user_type', 'tao_transactions', ['user_id', 'transaction_type'], unique=False)
    op.create_index('idx_mining_user_activity', 'educational_mining', ['user_id', 'activity_type'], unique=False)
    op.create_index('idx_health_netuid_time', 'bittensor_network_health', ['netuid', 'checked_at'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_health_netuid_time', table_name='bittensor_network_health')
    op.drop_index('idx_mining_user_activity', table_name='educational_mining')
    op.drop_index('idx_transactions_user_type', table_name='tao_transactions')
    op.drop_index('idx_validations_content_type', table_name='bittensor_validations')
    op.drop_index('idx_responses_query_miner', table_name='bittensor_responses')
    op.drop_index('idx_queries_user_created', table_name='bittensor_queries')
    
    # Drop tables
    op.drop_table('bittensor_network_health')
    op.drop_table('educational_mining')
    op.drop_table('bittensor_subnets')
    op.drop_table('user_tao_wallets')
    op.drop_table('tao_transactions')
    op.drop_table('bittensor_validations')
    op.drop_table('bittensor_responses')
    op.drop_table('bittensor_queries')
    op.drop_table('bittensor_nodes')
    
    # Drop ENUM types
    op.execute('DROP TYPE validationtype')
    op.execute('DROP TYPE subnettype')