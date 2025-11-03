import sys
from pathlib import Path
current_dir = Path(__file__).parent.parent
sys.path.insert(0, str(current_dir))

from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging
from bson import ObjectId

from module7_publishing.config.settings import settings

logger = logging.getLogger(__name__)

class PublishingDB:
    """MongoDB operations for publishing and distribution records"""
    
    def __init__(self, use_async: bool = False):
        self.use_async = use_async
        self.db_name = settings.MONGODB_DB
        
        if use_async:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        else:
            self.client = MongoClient(settings.MONGODB_URL)
        
        self.db = self.client[self.db_name]
        
        # Collection names
        self.publications = self.db.published_articles
        self.content_updates = self.db.content_updates
        self.platform_configs = self.db.platform_configs
        self.workflow_records = self.db.workflow_records
        self.task_records = self.db.task_records
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for better query performance"""
        try:
            # Publications collection indexes
            self.publications.create_index("article_id")
            self.publications.create_index("platform")
            self.publications.create_index("published_at")
            self.publications.create_index("status")
            self.publications.create_index("task_id")
            
            # Content updates indexes
            self.content_updates.create_index("article_id")
            self.content_updates.create_index("detected_at")
            self.content_updates.create_index("processed")
            
            # Workflow records indexes
            self.workflow_records.create_index("article_id")
            self.workflow_records.create_index("completed_at")
            self.workflow_records.create_index("workflow_type")
            
            # Task records indexes
            self.task_records.create_index("task_id")
            self.task_records.create_index("created_at")
            
            logger.info("✅ Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")
    
    def store_publication_record(self, publication_data: Dict[str, Any]) -> str:
        """
        Store publication record in database
        
        Args:
            publication_data: Publication information
            
        Returns:
            Document ID of stored record
        """
        try:
            # Add metadata
            publication_data['created_at'] = datetime.utcnow()
            publication_data['_id'] = ObjectId()
            
            # Store in database
            result = self.publications.insert_one(publication_data)
            
            logger.info(f"✅ Publication record stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Error storing publication record: {e}")
            return None
    
    def get_publication_record(self, article_id: str, platform: str = None) -> Optional[Dict[str, Any]]:
        """
        Get publication record for an article
        
        Args:
            article_id: Article identifier
            platform: Specific platform (optional)
            
        Returns:
            Publication record or None
        """
        try:
            query = {'article_id': article_id}
            if platform:
                query['platform'] = platform
            
            # Get most recent record
            record = self.publications.find_one(
                query,
                sort=[('published_at', -1)]
            )
            
            if record:
                record['_id'] = str(record['_id'])
                return record
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting publication record: {e}")
            return None
    
    def get_all_publications(self, article_id: str) -> List[Dict[str, Any]]:
        """
        Get all publication records for an article
        
        Args:
            article_id: Article identifier
            
        Returns:
            List of publication records
        """
        try:
            records = list(self.publications.find(
                {'article_id': article_id},
                sort=[('published_at', -1)]
            ))
            
            # Convert ObjectIds to strings
            for record in records:
                record['_id'] = str(record['_id'])
            
            return records
            
        except Exception as e:
            logger.error(f"❌ Error getting all publications: {e}")
            return []
    
    def update_publication_status(self, article_id: str, platform: str, new_status: str, additional_data: Dict = None) -> bool:
        """
        Update publication status
        
        Args:
            article_id: Article identifier
            platform: Platform name
            new_status: New status
            additional_data: Additional data to update
            
        Returns:
            Success status
        """
        try:
            update_data = {
                'status': new_status,
                'updated_at': datetime.utcnow()
            }
            
            if additional_data:
                update_data.update(additional_data)
            
            result = self.publications.update_one(
                {'article_id': article_id, 'platform': platform},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"✅ Publication status updated: {article_id} - {platform} - {new_status}")
                return True
            else:
                logger.warning(f"⚠️ No publication record found to update: {article_id} - {platform}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating publication status: {e}")
            return False
    
    def store_update_record(self, update_data: Dict[str, Any]) -> str:
        """
        Store article update record
        
        Args:
            update_data: Update information
            
        Returns:
            Document ID of stored record
        """
        try:
            # Add metadata
            update_data['created_at'] = datetime.utcnow()
            update_data['_id'] = ObjectId()
            
            # Store in database
            result = self.content_updates.insert_one(update_data)
            
            logger.info(f"✅ Update record stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Error storing update record: {e}")
            return None
    
    def get_content_updates(self, article_id: str, processed: bool = None) -> List[Dict[str, Any]]:
        """
        Get content updates for an article
        
        Args:
            article_id: Article identifier
            processed: Filter by processed status (optional)
            
        Returns:
            List of content updates
        """
        try:
            query = {'article_id': article_id}
            if processed is not None:
                query['processed'] = processed
            
            updates = list(self.content_updates.find(
                query,
                sort=[('detected_at', -1)]
            ))
            
            # Convert ObjectIds to strings
            for update in updates:
                update['_id'] = str(update['_id'])
            
            return updates
            
        except Exception as e:
            logger.error(f"❌ Error getting content updates: {e}")
            return []
    
    def store_workflow_record(self, workflow_data: Dict[str, Any]) -> str:
        """
        Store workflow execution record
        
        Args:
            workflow_data: Workflow execution information
            
        Returns:
            Document ID of stored record
        """
        try:
            # Add metadata
            workflow_data['created_at'] = datetime.utcnow()
            workflow_data['_id'] = ObjectId()
            
            # Store in database
            result = self.workflow_records.insert_one(workflow_data)
            
            logger.info(f"✅ Workflow record stored: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Error storing workflow record: {e}")
            return None
    
    def get_workflow_records(self, article_id: str = None, workflow_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get workflow records
        
        Args:
            article_id: Filter by article ID (optional)
            workflow_type: Filter by workflow type (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of workflow records
        """
        try:
            query = {}
            if article_id:
                query['article_id'] = article_id
            if workflow_type:
                query['workflow_type'] = workflow_type
            
            records = list(self.workflow_records.find(
                query,
                sort=[('completed_at', -1)]
            ).limit(limit))
            
            # Convert ObjectIds to strings
            for record in records:
                record['_id'] = str(record['_id'])
            
            return records
            
        except Exception as e:
            logger.error(f"❌ Error getting workflow records: {e}")
            return []
    
    def store_platform_config(self, user_id: str, platform: str, config_data: Dict[str, Any]) -> str:
        """
        Store platform configuration
        
        Args:
            user_id: User identifier
            platform: Platform name
            config_data: Configuration data
            
        Returns:
            Document ID of stored record
        """
        try:
            platform_config = {
                'user_id': user_id,
                'platform': platform,
                'config': config_data,
                'active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Update existing or insert new
            result = self.platform_configs.update_one(
                {'user_id': user_id, 'platform': platform},
                {'$set': platform_config},
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"✅ Platform config created: {platform}")
                return str(result.upserted_id)
            else:
                logger.info(f"✅ Platform config updated: {platform}")
                return "updated"
                
        except Exception as e:
            logger.error(f"❌ Error storing platform config: {e}")
            return None
    
    def get_platform_config(self, user_id: str, platform: str) -> Optional[Dict[str, Any]]:
        """
        Get platform configuration
        
        Args:
            user_id: User identifier
            platform: Platform name
            
        Returns:
            Platform configuration or None
        """
        try:
            config = self.platform_configs.find_one({
                'user_id': user_id,
                'platform': platform,
                'active': True
            })
            
            if config:
                config['_id'] = str(config['_id'])
                return config
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting platform config: {e}")
            return None
    
    def store_task_data(self, task_id: str, task_type: str, task_data: Dict[str, Any]) -> str:
        """
        Store task data for retry purposes
        
        Args:
            task_id: Celery task ID
            task_type: Type of task
            task_data: Task execution data
            
        Returns:
            Document ID of stored record
        """
        try:
            task_record = {
                'task_id': task_id,
                'task_type': task_type,
                'task_data': task_data,
                'created_at': datetime.utcnow()
            }
            
            result = self.task_records.insert_one(task_record)
            
            logger.debug(f"Task data stored: {task_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"❌ Error storing task data: {e}")
            return None
    
    def get_task_data(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task data for retry
        
        Args:
            task_id: Celery task ID
            
        Returns:
            Task data or None
        """
        try:
            task_record = self.task_records.find_one({'task_id': task_id})
            
            if task_record:
                task_record['_id'] = str(task_record['_id'])
                return task_record
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting task data: {e}")
            return None
    
    def get_publication_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get publication analytics for the last N days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Analytics data
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get publications in date range
            publications = list(self.publications.find({
                'published_at': {'$gte': start_date}
            }))
            
            # Analyze data
            analytics = {
                'total_publications': len(publications),
                'platforms': {},
                'success_rate': 0,
                'articles_published': len(set(p['article_id'] for p in publications)),
                'date_range': {
                    'start': start_date.isoformat(),
                    'end': datetime.utcnow().isoformat()
                }
            }
            
            # Platform breakdown
            successful_count = 0
            for pub in publications:
                platform = pub['platform']
                if platform not in analytics['platforms']:
                    analytics['platforms'][platform] = {
                        'total': 0,
                        'successful': 0,
                        'failed': 0
                    }
                
                analytics['platforms'][platform]['total'] += 1
                
                if pub.get('status') == 'published':
                    analytics['platforms'][platform]['successful'] += 1
                    successful_count += 1
                else:
                    analytics['platforms'][platform]['failed'] += 1
            
            # Calculate success rate
            if len(publications) > 0:
                analytics['success_rate'] = (successful_count / len(publications)) * 100
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")
            return {}
    
    def cleanup_old_records(self, days: int = 90) -> Dict[str, int]:
        """
        Clean up old records to prevent database bloat
        
        Args:
            days: Records older than this will be deleted
            
        Returns:
            Cleanup statistics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Clean up old task records
            task_result = self.task_records.delete_many({
                'created_at': {'$lt': cutoff_date}
            })
            
            # Clean up old workflow records
            workflow_result = self.workflow_records.delete_many({
                'completed_at': {'$lt': cutoff_date}
            })
            
            # Clean up processed content updates
            update_result = self.content_updates.delete_many({
                'detected_at': {'$lt': cutoff_date},
                'processed': True
            })
            
            cleanup_stats = {
                'task_records_deleted': task_result.deleted_count,
                'workflow_records_deleted': workflow_result.deleted_count,
                'update_records_deleted': update_result.deleted_count,
                'cutoff_date': cutoff_date.isoformat()
            }
            
            logger.info(f"✅ Database cleanup completed: {cleanup_stats}")
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"❌ Error during cleanup: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        try:
            self.client.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")

# Test function for database operations
def test_database_operations():
    """Test database connectivity and basic operations"""
    try:
        db = PublishingDB()
        
        # Test publication record
        test_publication = {
            'article_id': 'test_article_123',
            'platform': 'wordpress',
            'post_id': '999',
            'url': 'https://example.com/test-post',
            'published_at': datetime.utcnow(),
            'status': 'published',
            'task_id': 'test_task_123'
        }
        
        # Store test record
        record_id = db.store_publication_record(test_publication)
        if record_id:
            print(f"✅ Test publication record stored: {record_id}")
            
            # Retrieve test record
            retrieved = db.get_publication_record('test_article_123', 'wordpress')
            if retrieved:
                print(f"✅ Test publication record retrieved: {retrieved['_id']}")
                
                # Clean up test record
                db.publications.delete_one({'_id': ObjectId(record_id)})
                print(f"✅ Test record cleaned up")
                
                return True
            else:
                print("❌ Failed to retrieve test record")
                return False
        else:
            print("❌ Failed to store test record")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    finally:
        try:
            db.close()
        except:
            pass

if __name__ == '__main__':
    # Run database test
    print("Testing database operations...")
    success = test_database_operations()
    
    if success:
        print("🎉 Database operations test passed!")
    else:
        print("💥 Database operations test failed!")