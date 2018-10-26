import threading

from core.configuration import ConfigurationManager
from core.dataset_manager import DatasetManager
from core.communication_manager import CommunicationManager
from core.scheduler import DMLScheduler


def bootstrap():
    """
    Bootstraps the data provider unix service.

    It instantiates the Configuration Manager, Dataset Manager, Communication
    Manager and the Execution Pipeline.

    Note: for now, both the Execution Pipeline's Listener and Communication
    Manager are debug versions based on flask.
    """
    # 1. Set up Configuration Manager.
    config_manager = ConfigurationManager()
    config_manager.bootstrap()

    # 2. Set up Dataset Manager.
    dataset_manager = DatasetManager(
        config_manager=config_manager
    )

    # 3. Set up the Communication Manager.
    communication_manager = CommunicationManager()

    # 4. Set up the Execution Pipeline (Scheduler, Runners)
    # and run the Scheduler's cron on a new thread.
    scheduler = DMLScheduler(
        config_manager=config_manager,
    )
    scheduler.configure(
        communication_manager=communication_manager
    )
    t1 = threading.Thread(
        target=scheduler.start_cron,
        args=(0.05,),
        daemon=False,
    )
    t1.start()

    # 5. Set up Blockchain Gateway and start listening on a new thread.
    # TODO: The Blockchain Client to be implemented.

    # 6. Configure the Communication Manager with the components it talks to.
    communication_manager.configure(
        scheduler=scheduler
    )

    # 7. Wait for the threads to end.
    # TODO: Need to make it work as a daemon.
    t1.join()
