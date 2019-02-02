import logging
import time

from core.utils.enums 					import ActionableEventTypes, RawEventTypes, MessageEventTypes
from core.utils.enums 					import JobTypes, callback_handler_no_default
from core.utils.dmljob 					import (DMLJob, DMLAverageJob, DMLCommunicateJob, DMLServerJob, \
												DMLInitializeJob, DMLSplitJob, DMLTrainJob, DMLValidateJob)
from core.utils.keras 					import serialize_weights, deserialize_weights
from core.utils.dmlresult 				import DMLResult
from core.blockchain.blockchain_utils	import TxEnum, content_to_ipfs
from core.fed_avg_optimizer import FederatedAveragingOptimizer


class CloudConnectedOptimizer(FederatedAveragingOptimizer):
    """
    This is a clone of FedAvgOptimizer, but for two differences.
    1) This Optimizer requires the job_uuid field to be set in
    its initialization payload
    2) When this is finished training, it uploads statistics to
    a centralized cloud repo
    """
    def __init__(self, initialization_payload, dataset_manager):
        super().__init__(initialization_payload, dataset_manager)
        job_info = initialization_payload.get(TxEnum.CONTENT.name)
        serialized_job = job_info.get('serialized_job')
        self.job_data["job_uuid"] = serialized_job["job_uuid"]
    
    def _done_training(self, dmlresult_obj):
        """
		"LEVEL 2" Callback for a training job that just completed. Returns a
		DML Job of type communication and uploads to cloud server.

		NOTE: Assumes that the training succeeded. In the future, we may care
		about a degree of accuracy needing to be reached before updating the
		weights.
		"""
        new_weights = dmlresult_obj.results.get('weights')
        self.job_data["omega"] = dmlresult_obj.results.get('omega')
        # if we don't have sigma_omega yet, we will now
        self.job_data["sigma_omega"] = self.job_data["omega"] + self.job_data["sigma_omega"]
        # TODO: Key validation in next PR
        self._update_weights(new_weights)
        self.job_data["job_type"] = JobTypes.JOB_COMM.name
        self.job_data["round_num"] = self.curr_round
        comm_job = DMLCommunicateJob(
            # TODO: Consider synchronization issues
            round_num=self.curr_round,
            key=self.old_weights,
            weights=self.job_data["weights"],
            omega=self.job_data["omega"],
            sigma_omega=self.job_data["sigma_omega"]
        )
        server_job = DMLServerJob(job_uuid = self.job_data["job_uuid"], 
                                statistics=dmlresult_obj.results.get('train_stats'),
                                dataset_uuid = self.job_data["dataset_uuid"],
                                round_num = self.curr_round)
        return ActionableEventTypes.SCHEDULE_JOBS.name, [comm_job, server_job]
    