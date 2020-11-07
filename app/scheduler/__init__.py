"""Scheduler for scheduling."""
import atexit
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from .modules.random_channel import RandomChannelPromoter
from .modules.pairing import PairingSchedule
from .modules.base import ModuleBase
from db.facade import DBFacade
from typing import Tuple, List
from config import Config


class Scheduler:
    """The scheduler class for scheduling everything."""

    def __init__(self,
                 scheduler: BackgroundScheduler,
                 args: Tuple[Flask, Config],
                 facade: DBFacade):
        """Initialize scheduler class."""
        self.scheduler = scheduler
        self.args = args
        self.facade = facade
        self.modules: List[ModuleBase] = []

        self.__init_periodic_tasks()

        atexit.register(self.scheduler.shutdown)

    def start(self):
        """Start the scheduler, officially."""
        self.scheduler.start()

    def __add_job(self, module: ModuleBase):
        """Add module as a job."""
        self.scheduler.add_job(func=module.do_it, **module.get_job_args())
        self.modules.append(module)

    def __init_periodic_tasks(self):
        """Add jobs that fire every interval."""
        self.__add_job(RandomChannelPromoter(*self.args))
        # Feature toggle the pairings based on the
        # existence of the `SLACK_PAIRING_CHANNEL` env variable
        if len(self.args[1].slack_pairing_channel) != 0:
            self.__add_job(PairingSchedule(*self.args, self.facade))
