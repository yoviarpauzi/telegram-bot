from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from scripts.database.userDatabase import resetTokensForAllUsers

def schedule_token_reset():
    scheduler = BackgroundScheduler()
    scheduler.add_job(resetTokensForAllUsers, CronTrigger(hour=0, minute=0), kwargs={'default_token': 3})
    scheduler.start()