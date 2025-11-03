import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from celery import Celery
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import os
from bson import ObjectId

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery_app = Celery(
    'aurorapress_scheduling',
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(name='module7_publishing.tasks.scheduling_tasks.schedule_article_publication')
def schedule_article_publication(
    user_id: str,
    article_data: Dict[str, Any],
    target_platforms: List[str],
    scheduled_time: str
) -> Dict[str, Any]:
    try:
        from database.oauth_db import get_database
        from module7_publishing.tasks.oauth_publishing_tasks import publish_article_oauth
        
        logger.info(f"Scheduling article publication for user {user_id}")
        
        # Parse scheduled time - this creates timezone-aware datetime
        scheduled_dt = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        
        # Make current time timezone-aware to match scheduled_dt
        from datetime import timezone
        current_dt = datetime.now(timezone.utc)
        
        # Now both are timezone-aware and can be compared
        if scheduled_dt <= current_dt:
            return {
                'success': False,
                'error': 'Scheduled time must be in the future',
                'scheduled_time': scheduled_time
            }
        
        # Store scheduled post in database
        db = get_database()
        scheduled_collection = db['scheduled_posts']
        
        scheduled_post = {
            'user_id': user_id,
            'article_id': article_data.get('article_id'),
            'article_data': article_data,
            'target_platforms': target_platforms,
            'scheduled_time': scheduled_dt,
            'created_at': current_dt,  # Use timezone-aware datetime
            'status': 'pending',
            'task_id': None,
            'result': None
        }
        
        result = scheduled_collection.insert_one(scheduled_post)
        scheduled_id = str(result.inserted_id)
        
        # Calculate delay
        delay_seconds = (scheduled_dt - current_dt).total_seconds()
        
        logger.info(f"Scheduling article for {scheduled_dt} (in {delay_seconds:.0f} seconds)")
        
        # Schedule the task
        task = publish_article_oauth.apply_async(
            args=[user_id, article_data, target_platforms],
            eta=scheduled_dt,
            task_id=f"scheduled_{scheduled_id}"
        )
        
        # Update with task_id
        scheduled_collection.update_one(
            {'_id': result.inserted_id},
            {'$set': {'task_id': task.id}}
        )
        
        logger.info(f"Article scheduled successfully: {scheduled_id}, task: {task.id}")
        
        return {
            'success': True,
            'scheduled_id': scheduled_id,
            'task_id': task.id,
            'scheduled_time': scheduled_time,
            'user_id': user_id,
            'article_id': article_data.get('article_id'),
            'platforms': target_platforms,
            'created_at': current_dt.isoformat()
        }
            
    except Exception as e:
        logger.error(f"Error scheduling publication: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }

@celery_app.task(name='module7_publishing.tasks.scheduling_tasks.cancel_scheduled_post')
def cancel_scheduled_post(user_id: str, scheduled_id: str) -> Dict[str, Any]:
    """
    Cancel a scheduled post
    
    Args:
        user_id: User identifier
        scheduled_id: Scheduled post ID
        
    Returns:
        Cancellation result
    """
    try:
        from database.oauth_db import get_database
        from celery.result import AsyncResult
        
        logger.info(f"Cancelling scheduled post {scheduled_id} for user {user_id}")
        
        db = get_database()
        scheduled_collection = db['scheduled_posts']
        
        # Find scheduled post
        scheduled_post = scheduled_collection.find_one({
            '_id': ObjectId(scheduled_id),
            'user_id': user_id
        })
        
        if not scheduled_post:
            return {
                'success': False,
                'error': 'Scheduled post not found'
            }
        
        if scheduled_post['status'] != 'pending':
            return {
                'success': False,
                'error': f"Cannot cancel post with status: {scheduled_post['status']}"
            }
        
        # Revoke the Celery task
        task_id = scheduled_post.get('task_id')
        if task_id:
            celery_app.control.revoke(task_id, terminate=True)
            logger.info(f"Revoked Celery task: {task_id}")
        
        # Update status
        scheduled_collection.update_one(
            {'_id': ObjectId(scheduled_id)},
            {
                '$set': {
                    'status': 'cancelled',
                    'cancelled_at': datetime.utcnow(),
                    'cancelled_by': user_id
                }
            }
        )
        
        logger.info(f"Scheduled post cancelled: {scheduled_id}")
        
        return {
            'success': True,
            'scheduled_id': scheduled_id,
            'cancelled_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cancelling scheduled post: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }

@celery_app.task(name='module7_publishing.tasks.scheduling_tasks.get_user_scheduled_posts')
def get_user_scheduled_posts(user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get all scheduled posts for a user
    
    Args:
        user_id: User identifier
        status: Filter by status (pending, published, failed, cancelled)
        
    Returns:
        List of scheduled posts
    """
    try:
        from database.oauth_db import get_database
        
        logger.info(f"Getting scheduled posts for user {user_id}")
        
        db = get_database()
        scheduled_collection = db['scheduled_posts']
        
        query = {'user_id': user_id}
        if status:
            query['status'] = status
        
        scheduled_posts = list(scheduled_collection.find(query).sort('scheduled_time', -1))
        
        # Convert ObjectIds and datetimes to strings
        for post in scheduled_posts:
            post['_id'] = str(post['_id'])
            post['scheduled_time'] = post['scheduled_time'].isoformat()
            post['created_at'] = post['created_at'].isoformat()
            
            if post.get('cancelled_at'):
                post['cancelled_at'] = post['cancelled_at'].isoformat()
        
        logger.info(f"Found {len(scheduled_posts)} scheduled posts")
        return scheduled_posts
        
    except Exception as e:
        logger.error(f"Error getting scheduled posts: {e}", exc_info=True)
        return []

@celery_app.task(name='module7_publishing.tasks.scheduling_tasks.reschedule_post')
def reschedule_post(
    user_id: str,
    scheduled_id: str,
    new_scheduled_time: str
) -> Dict[str, Any]:
    try:
        from database.oauth_db import get_database
        from module7_publishing.tasks.oauth_publishing_tasks import publish_article_oauth
        from datetime import timezone
        
        logger.info(f"Rescheduling post {scheduled_id} for user {user_id}")
        
        db = get_database()
        scheduled_collection = db['scheduled_posts']
        
        # Find scheduled post
        scheduled_post = scheduled_collection.find_one({
            '_id': ObjectId(scheduled_id),
            'user_id': user_id
        })
        
        if not scheduled_post:
            return {
                'success': False,
                'error': 'Scheduled post not found'
            }
        
        if scheduled_post['status'] != 'pending':
            return {
                'success': False,
                'error': f"Cannot reschedule post with status: {scheduled_post['status']}"
            }
        
        # Parse new time - timezone-aware
        new_scheduled_dt = datetime.fromisoformat(new_scheduled_time.replace('Z', '+00:00'))
        current_dt = datetime.now(timezone.utc)
        
        if new_scheduled_dt <= current_dt:
            return {
                'success': False,
                'error': 'New scheduled time must be in the future'
            }
        
        # Revoke old task
        old_task_id = scheduled_post.get('task_id')
        if old_task_id:
            celery_app.control.revoke(old_task_id, terminate=True)
        
        # Schedule new task
        task = publish_article_oauth.apply_async(
            args=[
                user_id,
                scheduled_post['article_data'],
                scheduled_post['target_platforms']
            ],
            eta=new_scheduled_dt,
            task_id=f"rescheduled_{scheduled_id}"
        )
        
        # Update database
        scheduled_collection.update_one(
            {'_id': ObjectId(scheduled_id)},
            {
                '$set': {
                    'scheduled_time': new_scheduled_dt,
                    'task_id': task.id,
                    'rescheduled_at': current_dt,
                    'previous_scheduled_time': scheduled_post['scheduled_time']
                }
            }
        )
        
        logger.info(f"Post rescheduled: {scheduled_id}, new time: {new_scheduled_dt}")
        
        return {
            'success': True,
            'scheduled_id': scheduled_id,
            'new_task_id': task.id,
            'new_scheduled_time': new_scheduled_time,
            'previous_scheduled_time': scheduled_post['scheduled_time'].isoformat(),
            'rescheduled_at': current_dt.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error rescheduling post: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e)
        }

@celery_app.task(name='module7_publishing.tasks.scheduling_tasks.update_scheduled_post_status')
def update_scheduled_post_status(
    scheduled_id: str,
    status: str,
    result: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Update the status of a scheduled post after execution
    Called automatically by the publishing task
    
    Args:
        scheduled_id: Scheduled post ID
        status: New status (published, failed)
        result: Publication result
        
    Returns:
        True if successful
    """
    try:
        from database.oauth_db import get_database
        
        db = get_database()
        scheduled_collection = db['scheduled_posts']
        
        update_data = {
            'status': status,
            'executed_at': datetime.utcnow()
        }
        
        if result:
            update_data['result'] = result
        
        scheduled_collection.update_one(
            {'_id': ObjectId(scheduled_id)},
            {'$set': update_data}
        )
        
        logger.info(f"Updated scheduled post {scheduled_id} status to {status}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating scheduled post status: {e}")
        return False

@celery_app.task(name='module7_publishing.tasks.scheduling_tasks.check_missed_schedules')
def check_missed_schedules() -> Dict[str, Any]:
    """
    Check for and handle missed scheduled posts
    Should be run periodically via Celery Beat
    
    Returns:
        Check results
    """
    try:
        from database.oauth_db import get_database
        
        logger.info("Checking for missed scheduled posts")
        
        db = get_database()
        scheduled_collection = db['scheduled_posts']
        
        # Find posts that should have been published but weren't
        cutoff_time = datetime.utcnow() - timedelta(minutes=10)
        
        missed_posts = list(scheduled_collection.find({
            'status': 'pending',
            'scheduled_time': {'$lt': cutoff_time}
        }))
        
        if not missed_posts:
            logger.info("No missed schedules found")
            return {
                'success': True,
                'missed_posts': 0
            }
        
        logger.warning(f"Found {len(missed_posts)} missed scheduled posts")
        
        # Mark as failed
        for post in missed_posts:
            scheduled_collection.update_one(
                {'_id': post['_id']},
                {
                    '$set': {
                        'status': 'failed',
                        'error': 'Missed scheduled time',
                        'failed_at': datetime.utcnow()
                    }
                }
            )
        
        return {
            'success': True,
            'missed_posts': len(missed_posts),
            'checked_at': datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking missed schedules: {e}")
        return {
            'success': False,
            'error': str(e)
        }

# Test function
def test_scheduling_tasks():
    """Test scheduling tasks"""
    try:
        print("\n=== Testing Scheduling Tasks ===\n")
        
        # Test scheduling
        print("1. Testing article scheduling...")
        test_article = {
            'article_id': 'scheduled_test_001',
            'title': 'Scheduled Test Article',
            'content': '<p>This will be published in 2 hours</p>'
        }
        
        scheduled_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
        
        result = schedule_article_publication.delay(
            'test_user',
            test_article,
            ['wordpress', 'twitter'],
            scheduled_time
        )
        schedule_result = result.get(timeout=10)
        print(f"   Scheduling: {schedule_result.get('success')}")
        print(f"   Scheduled ID: {schedule_result.get('scheduled_id')}")
        
        # Test getting scheduled posts
        print("\n2. Testing get scheduled posts...")
        result = get_user_scheduled_posts.delay('test_user', 'pending')
        posts = result.get(timeout=10)
        print(f"   Found {len(posts)} pending scheduled posts")
        
        # Test cancellation
        if schedule_result.get('success'):
            print("\n3. Testing cancellation...")
            scheduled_id = schedule_result['scheduled_id']
            result = cancel_scheduled_post.delay('test_user', scheduled_id)
            cancel_result = result.get(timeout=10)
            print(f"   Cancellation: {cancel_result.get('success')}")
        
        # Test missed schedules check
        print("\n4. Testing missed schedules check...")
        result = check_missed_schedules.delay()
        check_result = result.get(timeout=10)
        print(f"   Missed posts found: {check_result.get('missed_posts', 0)}")
        
        print("\n=== Scheduling tasks tests completed ===\n")
        return True
        
    except Exception as e:
        print(f"\nError testing scheduling tasks: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_scheduling_tasks()