import threading

from core.configuration import ConfigurationManager
from core.dataset_manager import DatasetManager
from core.debug_communication import FlaskTestingCommunicationManager
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
    # NOTE: This is the test version until the P2P one is implemented.
    communication_manager = FlaskTestingCommunicationManager(
        config_manager=config_manager
    )

    # 4. Set up the Execution Pipeline (Scheduler, Runners)
    # and run the Scheduler's cron on a new thread.
    scheduler = DMLScheduler(
        config_manager=config_manager,
    )
    t1 = threading.Thread(
        target=scheduler.start_cron,
        args=(0.05,),
        daemon=True,
    )
    t1.start()

    # 5. Start listening on a new thread.
    communication_manager.configure(
        scheduler=scheduler
    )
    t2 = threading.Thread(
        target=communication_manager.start,
        args=(),
        daemon=True,
    )
    t2.start()

    # 6. Wait for the threads to end.
    t1.join()
    t2.join()
