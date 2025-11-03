"""
Celery worker startup script for Module 7
Handles all publishing, monitoring, and scheduling tasks
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import Celery app
from module7_publishing.celery_app import celery_app

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('celery_worker.log')
    ]
)

logger = logging.getLogger(__name__)

def start_worker():
    """Start the Celery worker with appropriate configuration"""
    logger.info("Starting AuroraPress Publishing Worker...")
    
    # Worker configuration for M1 Mac
    worker_args = [
        '--loglevel=info',
        '--concurrency=4',  # Adjust based on your M1 Mac performance
        '--queues=publishing,social,monitoring,scheduling',
        '--hostname=worker@%h',
        '--without-heartbeat',  # Helps with M1 Mac compatibility
        '--pool=threads'        # Use threads instead of prefork for M1 compatibility
    ]
    
    try:
        celery_app.worker_main(worker_args)
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Worker error: {e}")
        raise

if __name__ == '__main__':
    start_worker()