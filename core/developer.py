"""DEPRECATED. Needs to be rewritten after off-chain is designed."""

from blockchain.blockchain_utils import *
from blockchain.ipfs_utils import *

from custom.keras import model_from_serialized, get_optimizer
from core.utils.keras import serialize_weights, deserialize_weights

class DMLDeveloper(object):
    """
    This class creates StateMachine smart contracts to train models.
    """
    def __init__(self, clientAddress=None):
        '''
        By default, this will listen and transact through our own testnet account.
        However, if a clientAddress is specified, this developer will work through that.
        '''
        if clientAddress:
            self.web3 = Web3(IPCProvider())
            assert self.web3.isConnected()
            assert is_address(clientAddress)
            self.clientAddress = self.web3.toChecksumAddress(clientAddress)
        else:
            self.web3 = Web3(HTTPProvider(BETA_URL))
            assert self.web3.isConnected()
            self.clientAddress = self.web3.toChecksumAddress(BETA_ADDR)

        # Start reading in the contracts
        self.delegator = self.web3.eth.contract(
            address = self.web3.toChecksumAddress(TEMP_DELEGATOR_ADDR),
            abi = TEMP_DELEGATOR_ABI)

    def deploy_with_model(self, model, [addrs]=self.clientAddress):
        '''
        Takes in a model and deploys it using default addresses.
        Testing method ONLY.
        '''
        model_architecture = model.to_json()
        model_optimizer = get_optimizer(model)
        model_json = {
            "architecture": model_architecture,
            "optimizer": model_optimizer
        }
        serialized_weights = serialize_weights(model.get_weights())
        weights_bytes = weights2bytes32(serialized_weights)
        complete_json = {'serialized_model' : model_json,
                'job_type' : 'train',
                'framework_type' : 'keras'}
        json_bytes = json2bytes32(complete_json)
        return self.deploy_StateMachine(addrs, [json_bytes, weights_bytes])

    def deploy_StateMachine(self, targetAddrs, modelAddrsBytes):
        '''
        As per our style philosophy, this method should only take in the arguments
        it directly needs to instantiate a StateMachine, which is why this takes in
        only the addresses as bytes.
        Internal method only; should be called from higher-level functions that take
        user input directly.
        '''

        # Check that we're getting actual addresses or this will cause problems later.
        for addr in targetAddrs:
            assert(is_address(addr))

        # Deploy StateMachine
        self.web3.personal.unlockAccount(self.clientAddress, 'panda')
        tx_hash = self.delegator.functions.makeQuery(
            targetAddrs, modelAddrsBytes).transact({'from': self.clientAddress})

        # Parse the output

        self.web3.eth.waitForTransactionReceipt(tx_hash)
        tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        self.web3.personal.lockAccount(self.clientAddress)
        attr_dict = self.delegator.events.NewQuery().processReceipt(tx_receipt)
        print(attr_dict)
        addr = attr_dict[0]['args']['addr']
        print(addr)
        # Read in the new StateMachine

        self.stateMachine = self.web3.eth.contract(
            address = self.web3.toChecksumAddress(addr),
            abi = TEMP_STATEMACHINE_ABI)
    def terminate(self):
        '''
        Terminates decentralized training.
        Should not be called directly.
        '''
        tx_hash = self.stateMachine.functions.terminate().transact({'from': self.clientAddress})
        self.web3.eth.waitForTransactionReceipt(tx_hash)
        tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        attr_dict = self.stateMachine.events.DoneTraining().processReceipt(tx_receipt)
        print(attr_dict)

    def update_weights(self, model):
        '''
        Takes in a model.
        Extracts the weights from the model and puts them into a file.
        Puts it on IPFS and returns the Bytes32 of the IPFSHash.
        Calls update_StateMachine() with this new argument.
        '''
        weights = model.get_weights()
        serialized_weights = serialize_weights(weights)
        self.update_StateMachine(weights2bytes32(serialized_weights))

    def update_StateMachine(self, weightsAddrBytes):
        '''
        Takes in the Bytes32 referencing an IPFS Hash of a model weights file.
        Updates StateMachine with its argument.
        Asserts that the updated value in StateMachine is equal to its input.
        '''
        print(weightsAddrBytes)
        tx_hash = self.stateMachine.functions.newWeights(weightsBytes).transact({'from': self.clientAddress})
        self.web3.eth.waitForTransactionReceipt(tx_hash)
        tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
        attr_dict = self.stateMachine.events.NewWeights().processReceipt(tx_receipt)
        print(attr_dict)
        addr = attr_dict[0]['args']['addr']
        print(addr)
        assert weightAddrsBytes == addr

    def checkBalance(self):
        '''
        Internal method to test the balance of the account.
        '''
        myBalance = self.web3.eth.getBalance(self.clientAddress)
        print(myBalance)
        return myBalance

if __name__ == '__main__':
    from models.keras_lstm import KerasLSTM
    model = KerasLSTM(is_training=True).model
    developer = DMLDeveloper()
    developer.checkBalance()
    developer.deploy_with_model(model)
    developer.update_weights(model)
