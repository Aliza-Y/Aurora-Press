from apscheduler.schedulers.background import BackgroundScheduler
import logging
import os
from datetime import datetime
from rss_crawler import fetch_rss
from trend_extractor import extract_trends
from tfidf_trend_extractor import extract_and_save_trends
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
LOG_FILE = os.path.join(LOGS_DIR, 'scheduler.log')

# Create logs directory
os.makedirs(LOGS_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('trend_scheduler')

def update_trends():
    """Function to update trends by running all necessary components"""
    try:
        message = f"Starting trend update process at {datetime.now()}"
        print(message)
        logger.info(message)
        
        # Step 1: Fetch new RSS articles
        logger.info("Fetching RSS feeds...")
        fetch_rss()
        
        # Step 2: Extract named entities and classify them
        logger.info("Extracting named entities and trends...")
        extract_trends()
        
        # Step 3: Run TF-IDF analysis
        logger.info("Running TF-IDF analysis...")
        extract_and_save_trends()
        
        message = f"Trend update process completed successfully at {datetime.now()}"
        print(message)
        logger.info(message)
    except Exception as e:
        error_msg = f"Error in trend update process: {str(e)}"
        print(error_msg)
        logger.error(error_msg)

def main():
    try:
        # Create scheduler
        scheduler = BackgroundScheduler()
        
        # Add job to run every 2 hours
        scheduler.add_job(
            update_trends,
            'interval',
            hours=2,
            id='trend_update',
            name='Update trends every 2 hours'
        )
        
        # Start the scheduler
        scheduler.start()
        message = "Scheduler started! Trends will be updated every 2 hours."
        print(message)
        logger.info(message)
        print(f"Logs will be written to: {LOG_FILE}")
        
        # Run the first update immediately
        update_trends()
        
        # Keep the script running
        try:
            while True:
                pass
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            logger.info("Scheduler shutdown complete!")
    except Exception as e:
        logger.error(f"Error in scheduler: {str(e)}")
        raise

if __name__ == "__main__":
    main() 