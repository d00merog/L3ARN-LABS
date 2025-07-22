"""Add WebVM tables for browser-based virtual machine integration

Revision ID: 004_add_webvm_tables
Revises: 003_add_bittensor_tables
Create Date: 2024-01-20 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_webvm_tables'
down_revision = '003_add_bittensor_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    vm_environment_type_enum = postgresql.ENUM(
        'python', 'javascript', 'cpp', 'java', 'rust', 'go', 'linux_full', 'custom',
        name='vmenvironmenttype',
        create_type=False
    )
    vm_environment_type_enum.create(op.get_bind())
    
    vm_status_enum = postgresql.ENUM(
        'initializing', 'running', 'paused', 'stopped', 'error', 'terminated',
        name='vmstatus',
        create_type=False
    )
    vm_status_enum.create(op.get_bind())
    
    # Create webvm_instances table
    op.create_table('webvm_instances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('environment_type', vm_environment_type_enum, nullable=False),
        sa.Column('status', vm_status_enum, nullable=True),
        sa.Column('instance_name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cpu_cores', sa.Integer(), nullable=True),
        sa.Column('memory_mb', sa.Integer(), nullable=True),
        sa.Column('disk_mb', sa.Integer(), nullable=True),
        sa.Column('network_enabled', sa.Boolean(), nullable=True),
        sa.Column('startup_time_ms', sa.Integer(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('total_runtime_seconds', sa.Integer(), nullable=True),
        sa.Column('cpu_usage_percent', sa.Float(), nullable=True),
        sa.Column('memory_usage_mb', sa.Float(), nullable=True),
        sa.Column('disk_usage_mb', sa.Float(), nullable=True),
        sa.Column('is_persistent', sa.Boolean(), nullable=True),
        sa.Column('snapshot_data', sa.JSON(), nullable=True),
        sa.Column('environment_variables', sa.JSON(), nullable=True),
        sa.Column('installed_packages', sa.JSON(), nullable=True),
        sa.Column('course_id', sa.Integer(), nullable=True),
        sa.Column('assignment_id', sa.Integer(), nullable=True),
        sa.Column('lesson_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('terminated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index(op.f('ix_webvm_instances_id'), 'webvm_instances', ['id'], unique=False)
    op.create_index(op.f('ix_webvm_instances_session_id'), 'webvm_instances', ['session_id'], unique=True)
    op.create_index(op.f('ix_webvm_instances_user_id'), 'webvm_instances', ['user_id'], unique=False)
    
    # Create code_executions table
    op.create_table('code_executions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vm_instance_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=False),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('input_data', sa.Text(), nullable=True),
        sa.Column('output', sa.Text(), nullable=True),
        sa.Column('error_output', sa.Text(), nullable=True),
        sa.Column('exit_code', sa.Integer(), nullable=True),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('memory_used_mb', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('is_assignment', sa.Boolean(), nullable=True),
        sa.Column('assignment_id', sa.Integer(), nullable=True),
        sa.Column('test_results', sa.JSON(), nullable=True),
        sa.Column('grade_score', sa.Float(), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('code_quality_score', sa.Float(), nullable=True),
        sa.Column('suggestions', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['vm_instance_id'], ['webvm_instances.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_code_executions_id'), 'code_executions', ['id'], unique=False)
    op.create_index(op.f('ix_code_executions_user_id'), 'code_executions', ['user_id'], unique=False)
    
    # Create webvm_files table
    op.create_table('webvm_files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vm_instance_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('filepath', sa.String(length=500), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('is_executable', sa.Boolean(), nullable=True),
        sa.Column('is_readonly', sa.Boolean(), nullable=True),
        sa.Column('permissions', sa.String(length=10), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True),
        sa.Column('parent_version_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('modified_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('accessed_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_template', sa.Boolean(), nullable=True),
        sa.Column('is_solution', sa.Boolean(), nullable=True),
        sa.Column('assignment_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['parent_version_id'], ['webvm_files.id'], ),
        sa.ForeignKeyConstraint(['vm_instance_id'], ['webvm_instances.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webvm_files_id'), 'webvm_files', ['id'], unique=False)
    op.create_index(op.f('ix_webvm_files_user_id'), 'webvm_files', ['user_id'], unique=False)
    
    # Create webvm_templates table
    op.create_table('webvm_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('environment_type', vm_environment_type_enum, nullable=False),
        sa.Column('base_image', sa.String(length=100), nullable=False),
        sa.Column('pre_installed_packages', sa.JSON(), nullable=True),
        sa.Column('default_files', sa.JSON(), nullable=True),
        sa.Column('startup_script', sa.Text(), nullable=True),
        sa.Column('max_cpu_cores', sa.Integer(), nullable=True),
        sa.Column('max_memory_mb', sa.Integer(), nullable=True),
        sa.Column('max_disk_mb', sa.Integer(), nullable=True),
        sa.Column('max_runtime_minutes', sa.Integer(), nullable=True),
        sa.Column('difficulty_level', sa.String(length=20), nullable=True),
        sa.Column('subject_area', sa.String(length=50), nullable=True),
        sa.Column('learning_objectives', sa.JSON(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=True),
        sa.Column('success_rate', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_webvm_templates_id'), 'webvm_templates', ['id'], unique=False)
    
    # Create webvm_sessions table
    op.create_table('webvm_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_token', sa.String(length=100), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('browser_info', sa.JSON(), nullable=True),
        sa.Column('webgpu_supported', sa.Boolean(), nullable=True),
        sa.Column('webassembly_supported', sa.Boolean(), nullable=True),
        sa.Column('browser_performance_score', sa.Float(), nullable=True),
        sa.Column('active_vm_instances', sa.JSON(), nullable=True),
        sa.Column('max_concurrent_vms', sa.Integer(), nullable=True),
        sa.Column('resource_quota_mb', sa.Integer(), nullable=True),
        sa.Column('resource_used_mb', sa.Integer(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('total_session_time', sa.Integer(), nullable=True),
        sa.Column('commands_executed', sa.Integer(), nullable=True),
        sa.Column('files_created', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_token')
    )
    op.create_index(op.f('ix_webvm_sessions_id'), 'webvm_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_webvm_sessions_user_id'), 'webvm_sessions', ['user_id'], unique=False)
    
    # Create webvm_resource_usage table
    op.create_table('webvm_resource_usage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vm_instance_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('cpu_usage_percent', sa.Float(), nullable=False),
        sa.Column('memory_usage_mb', sa.Float(), nullable=False),
        sa.Column('disk_usage_mb', sa.Float(), nullable=False),
        sa.Column('network_bytes_in', sa.Integer(), nullable=True),
        sa.Column('network_bytes_out', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('throughput_ops_per_sec', sa.Float(), nullable=True),
        sa.Column('error_rate', sa.Float(), nullable=True),
        sa.Column('gpu_usage_percent', sa.Float(), nullable=True),
        sa.Column('gpu_memory_mb', sa.Float(), nullable=True),
        sa.Column('webgl_calls_per_sec', sa.Integer(), nullable=True),
        sa.Column('sample_interval_seconds', sa.Integer(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['vm_instance_id'], ['webvm_instances.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webvm_resource_usage_id'), 'webvm_resource_usage', ['id'], unique=False)
    op.create_index(op.f('ix_webvm_resource_usage_user_id'), 'webvm_resource_usage', ['user_id'], unique=False)
    
    # Create webvm_collaborations table
    op.create_table('webvm_collaborations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vm_instance_id', sa.Integer(), nullable=False),
        sa.Column('owner_user_id', sa.Integer(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('max_collaborators', sa.Integer(), nullable=True),
        sa.Column('allow_code_editing', sa.Boolean(), nullable=True),
        sa.Column('allow_file_management', sa.Boolean(), nullable=True),
        sa.Column('allow_execution', sa.Boolean(), nullable=True),
        sa.Column('invited_users', sa.JSON(), nullable=True),
        sa.Column('access_password', sa.String(length=100), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('active_collaborators', sa.JSON(), nullable=True),
        sa.Column('collaboration_history', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['vm_instance_id'], ['webvm_instances.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webvm_collaborations_id'), 'webvm_collaborations', ['id'], unique=False)
    op.create_index(op.f('ix_webvm_collaborations_owner_user_id'), 'webvm_collaborations', ['owner_user_id'], unique=False)
    
    # Create webvm_educational_integration table
    op.create_table('webvm_educational_integration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vm_instance_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=True),
        sa.Column('auto_grading_enabled', sa.Boolean(), nullable=True),
        sa.Column('test_cases', sa.JSON(), nullable=True),
        sa.Column('expected_outputs', sa.JSON(), nullable=True),
        sa.Column('grading_criteria', sa.JSON(), nullable=True),
        sa.Column('completion_status', sa.String(length=20), nullable=True),
        sa.Column('final_score', sa.Float(), nullable=True),
        sa.Column('detailed_results', sa.JSON(), nullable=True),
        sa.Column('ai_feedback', sa.Text(), nullable=True),
        sa.Column('validation_requested', sa.Boolean(), nullable=True),
        sa.Column('bittensor_validation_id', sa.Integer(), nullable=True),
        sa.Column('consensus_score', sa.Float(), nullable=True),
        sa.Column('started_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('graded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['vm_instance_id'], ['webvm_instances.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_webvm_educational_integration_id'), 'webvm_educational_integration', ['id'], unique=False)
    op.create_index(op.f('ix_webvm_educational_integration_user_id'), 'webvm_educational_integration', ['user_id'], unique=False)
    
    # Create composite indexes for better performance
    op.create_index('idx_vm_instances_user_status', 'webvm_instances', ['user_id', 'status'], unique=False)
    op.create_index('idx_executions_vm_user', 'code_executions', ['vm_instance_id', 'user_id'], unique=False)
    op.create_index('idx_files_vm_path', 'webvm_files', ['vm_instance_id', 'filepath'], unique=False)
    op.create_index('idx_sessions_user_active', 'webvm_sessions', ['user_id', 'is_active'], unique=False)
    op.create_index('idx_resource_usage_vm_time', 'webvm_resource_usage', ['vm_instance_id', 'recorded_at'], unique=False)
    op.create_index('idx_collaboration_vm_owner', 'webvm_collaborations', ['vm_instance_id', 'owner_user_id'], unique=False)
    op.create_index('idx_educational_content_user', 'webvm_educational_integration', ['content_id', 'user_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_educational_content_user', table_name='webvm_educational_integration')
    op.drop_index('idx_collaboration_vm_owner', table_name='webvm_collaborations')
    op.drop_index('idx_resource_usage_vm_time', table_name='webvm_resource_usage')
    op.drop_index('idx_sessions_user_active', table_name='webvm_sessions')
    op.drop_index('idx_files_vm_path', table_name='webvm_files')
    op.drop_index('idx_executions_vm_user', table_name='code_executions')
    op.drop_index('idx_vm_instances_user_status', table_name='webvm_instances')
    
    # Drop tables
    op.drop_table('webvm_educational_integration')
    op.drop_table('webvm_collaborations')
    op.drop_table('webvm_resource_usage')
    op.drop_table('webvm_sessions')
    op.drop_table('webvm_templates')
    op.drop_table('webvm_files')
    op.drop_table('code_executions')
    op.drop_table('webvm_instances')
    
    # Drop ENUM types
    op.execute('DROP TYPE vmstatus')
    op.execute('DROP TYPE vmenvironmenttype')