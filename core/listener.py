import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from core.blockchain.blockchain_utils import *
from core.blockchain.ipfs_utils import *

from web3.auto import w3
from core.scheduler import DMLScheduler
from core.utils.dmljob import DMLJob, deserialize_job

class DMLListener(object):
    """
    This class handles all interactions with the blockchain.
    This includes listening, as well as sending weights over P2P.
    Implements the Singleton pattern.
    """
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if DMLListener.__instance == None:
            DMLScheduler()
        return DMLListener.__instance 

    def __init__(self, clientAddress=None):
        """ Virtually private constructor. """
        if DMLListener.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            DMLListener.__instance = self

        # Connect scheduler
        self.scheduler = DMLScheduler.getInstance()
        if clientAddress:
            self.web3 = Web3(IPCProvider())
            assert self.web3.isConnected()
            assert is_address(clientAddress)
            self.clientAddress = self.web3.toChecksumAddress(clientAddress)
        else:
            self.web3 = Web3(HTTPProvider(ALPHA_URL))
            assert self.web3.isConnected()
            self.clientAddress = self.web3.toChecksumAddress(ALPHA_ADDR)

    async def start_listening(self, event_to_listen, poll_interval=5):
        while True:
            lst = event_to_listen.get_new_entries()
            if lst:
                # print(lst[0])
                return lst[0]
            await asyncio.sleep(poll_interval)

    def filter_set(self, event_sig, contract_addr, handler):
        print(contract_addr)
        event_signature_hash = self.web3.sha3(text=event_sig).hex()
        event_filter = self.web3.eth.filter({
            "address": contract_addr.lower(),
            "topics": [event_signature_hash]
            })
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        try:
            inter = loop.run_until_complete(
                self.start_listening(event_filter, 2))
            check = handler(inter)
        finally:
            loop.close()
        return check

    def handle_newstatemachine(self, event_data, models=None):
        event_json = decode_event(TEMP_DELEGATOR_ABI, event_data)
        stateMachineAddress = event_json['addr']
        print(stateMachineAddress)
        models = event_json['models']
        print(models[0])
        model_json = bytes322json(models[0])
        self.model_json = model_json
        model_weights = bytes322bytes(models[1])
        # # print("Type of data is {}".format(isinstance(model_weights, bytes)))
        job_dict = {
            'weights' : model_weights,
            'job_data' : {
                'job_type' : 'train',
                'serialized_model' : model_json,
                'model_type' : 'keras'
            }
        }
        # model = self._initialize_model(model_json, 'keras')
        # model = bytes322weights(model, models[1])
        # self.model = model
        # model_weights = model.get_weights()
        new_job = serialize_job(job_dict)
        self.scheduler.add_job(new_job)
        # serialized_model = model_json['serialized_model']
        # model_weights = bytes322weights(serialized_model, models[1])
        # print(models)
        validator = event_json['validator']
        # print(event_json)
        self.listen_statemachine(stateMachineAddress)

    def listen_delegator(self, event_data=None):
        self.filter_set(
            "NewQuery(address,bytes32[2],address)",
            TEMP_DELEGATOR_ADDR, self.handle_newstatemachine)

    def listen_statemachine(self, address):
        self.filter_set("NewWeights(bytes32)", address, self.handle_newWeights)
        # self.filter_set("DoneTraining()", address, self.checkBalance)

    def checkBalance(self, event_data):
        print(event_data)
        expectedBalance = event_data.split("000000000000000000000000")[2]
        myBalance = self.web3.eth.getBalance(self.clientAddress)
        assert myBalance == expectedBalance

    def handle_newWeights(self, event_data):
        event_json = decode_event(TEMP_STATEMACHINE_ABI, event_data)
        model_addr_bytes = event_json['addr']
        model_weights = bytes322bytes(model_addr_bytes)
        job_dict = {
            'weights' : model_weights,
            'job_data' : {
                'job_type' : 'train',
                'serialized_model' : self.model_json,
                'model_type' : 'keras'
            }
        }
        new_job = deserialize_job(job_dict)
        self.scheduler.add_job(new_job)
        print("MEGADONE")
        return "I'm done!"
        # model =
        # model_weights = get_model(base322ipfs(model_addr))
        # new_job = DMLJob(model_json)
        # self.scheduler.add_job(new_job)
        # return event_data.split("000000000000000000000000")

    def main(self):
        # print(self.web3.eth.getBlock('latest'))
        self.handle_newstatemachine("",[bytearray(b'\xa8*\x06\xd4\x92\x8b\xfe\xa5\tX\x8d\x818\xc9"\xba\t^d\x1c\xe9\xc8R\x93:\xf2h\x8aX|\x9a\x1a'), bytearray(b'\x8c\xb3NR\xce\xdf\xf8\xfd\xf9F\x18\x92.\x123[\xe8\xc4\x82\x857\xb8\xb8\x90\x88\xd5\x11\x0b-4#D')])

if __name__ == '__main__':
    listener = DMLListener()
    listener.main()
