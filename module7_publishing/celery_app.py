"""
Celery application configuration for Module 7 - Publishing & Distribution
Compatible with M1 Mac and integrated with existing AuroraPress system
"""

from celery import Celery
import os
from datetime import timedelta

# Redis configuration (M1 Mac compatible)
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Create Celery application
celery_app = Celery(
    'aurorapress_publishing',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'module7_publishing.tasks.oauth_publishing_tasks',
        'module7_publishing.tasks.scheduling_tasks'
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task execution settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'module7_publishing.tasks.oauth_publishing_tasks.publish_article_oauth': {'queue': 'publishing'},
        'module7_publishing.tasks.oauth_publishing_tasks.check_user_platform_status': {'queue': 'publishing'},
        'module7_publishing.tasks.oauth_publishing_tasks.publish_seo_optimized_article': {'queue': 'publishing'},
        'module7_publishing.tasks.scheduling_tasks.execute_scheduled_publish': {'queue': 'scheduling'},
    },
    
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    task_soft_time_limit=300,     # 5 minutes
    task_time_limit=600,          # 10 minutes
    
    # Result backend settings
    result_expires=3600,          # 1 hour
    result_backend_transport_options={'db': 1},
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=50,
    worker_disable_rate_limits=True,
    
    # Beat scheduler settings (for periodic tasks)
    beat_schedule={
        'process-scheduled-publications': {
            'task': 'module7_publishing.tasks.scheduling_tasks.process_scheduled_tasks',
            'schedule': timedelta(minutes=5),   # Check every 5 minutes
        },
    },
)

# Connection retry settings
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.broker_connection_retry = True

# Task discovery - use correct module paths
celery_app.autodiscover_tasks([
    'module7_publishing.tasks.oauth_publishing_tasks',
    'module7_publishing.tasks.scheduling_tasks'
])

# Health check task
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery functionality"""
    return f'Request: {self.request!r}'

# Test connectivity
@celery_app.task
def ping():
    """Simple ping task to test Celery worker"""
    return 'pong'

if __name__ == '__main__':
    celery_app.start()