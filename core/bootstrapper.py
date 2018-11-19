import threading
import ipfsapi

from core.configuration import ConfigurationManager
from core.dataset_manager import DatasetManager
from core.communication_manager import CommunicationManager
from core.scheduler import DMLScheduler
from core.blockchain.blockchain_gateway import BlockchainGateway


def bootstrap():
    """
    Bootstraps the data provider unix service.

    It instantiates the Configuration Manager, Dataset Manager, Communication
    Manager and the Execution Pipeline.
    """
    # 1. Set up Configuration Manager.
    config_manager = ConfigurationManager()
    config_manager.bootstrap()

    # 2. Set up the IPFS Client used by the service
    config = config_manager.get_config()
    client = None
    try:
        client = ipfsapi.connect(config.get('BLOCKCHAIN', 'host'), 
            config.getint('BLOCKCHAIN', 'ipfs_port'))
    except Exception as e:
        # TODO: Can this log the exception?
        # logging.info("IPFS daemon not started, got: {0}".format(e))
        raise(e)
    # 2. Set up Dataset Manager.
    dataset_manager = DatasetManager(
        config_manager=config_manager
    )
    dataset_manager.configure(ipfs_client=client)
    
    # 3. Set up the Communication Manager.
    communication_manager = CommunicationManager()

    # 4. Set up the Execution Pipeline (Scheduler, Runners)
    # and run the Scheduler's cron on a new thread.
    scheduler = DMLScheduler(
        config_manager=config_manager,
    )
    scheduler.configure(
        communication_manager=communication_manager,
        ipfs_client=client
    )
    t1 = threading.Thread(
        target=scheduler.start_cron,
        args=(0.05,),
        daemon=False,
    )
    t1.start()

    # 5. Configure the Communication Manager with the components it talks to.
    communication_manager.configure(
        scheduler=scheduler
    )

    # 6. Set up Blockchain Gateway and start listening on a new thread.
    blockchain_gateway = BlockchainGateway()
    blockchain_gateway.configure(config_manager=config_manager,
        communication_manager=communication_manager,
        ipfs_client=client)
    t2 = threading.Thread(
        target=blockchain_gateway.start_cron,
        args=(0.05,),
        daemon=False,
    )
    t2.start()

    # 7. Wait for the threads to end.
    # TODO: Need to make it work as a daemon.
    t1.join()
