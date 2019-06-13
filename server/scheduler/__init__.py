"""Scheduler for scheduling."""
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from .modules import random_channel


class Scheduler():
    """The scheduler class for scheduling everything."""

    def __init__(self, flask_app, config, credentials):
        """Initialize scheduler class."""
        self.__scheduler = BackgroundScheduler()
        self.__args = (flask_app, config, credentials)

        self.__init_periodic_tasks()

        atexit.register(self.__scheduler.shutdown)

    def start(self):
        """Start the scheduler, officially."""
        self.__scheduler.start()

    def __init_periodic_tasks(self):
        """Add jobs that fire every interval."""
        self.__scheduler.add_job(func=random_channel.do_it, trigger='cron',
                                 args=self.__args, day_of_week='sat',
                                 hour=12, name=random_channel.NAME)
