import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from scheduler.daily_task import daily_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def start_scheduler():
    trigger = CronTrigger(second='*/5')  # Runs every 5 seconds (for testing)
    scheduler.add_job(daily_task, trigger, name="Daily Trading Task")
    scheduler.start()
    logger.info("Scheduler started.")
