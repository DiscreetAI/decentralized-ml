from core.utils.dmljob import serialize_job, deserialize_job

class DMLResult(object):
    """
    DML Result

    This class is created by the Runners whenever they're done running a job,
    and it's passed to the Communication Manager on success or back to the
    Scheduler on error.

    TODO: Right now the DMLResult object is passing around the DMLJob that
    originated the results, but we can do better.

    """

    def __init__(
        self,
        status,
        job_type,
        results={},
        error_message="",
    ):
        """
        Initializes a DML Result object.

        Args:
            status (str): status of the job [successful|failed].
            job_type (str): job type of the job that finished running.
            results (dict): results from running the job.
            error_message (str): error message of why the job failed (if it did).
        """
        self.status = status
        self.job_type = job_type
        self.results = results
        self.error_message = error_message


def serialize_result(dmlresult_job):
    """
    Serializes a DML Result object into a dictionary.

    Args:
        dmlresult_job (DMLResult): result object.

    Returns:
        dict: The serialized version of the DML Result.
    """
    return {
        'status': dmlresult_job.status,
        'job_type': dmlresult_job.job_type,
        'results': dmlresult_job.results,
        'error_message': dmlresult_job.error_message,
    }


def deserialize_result(serialized_result):
    """
    Deserializes a serialized version of a DML Result object.

    Args:
        serialized_result (dict): serialized version of a DML Result object.

    Returns:
        DMLResult: A DML Result object from serialized_result.
    """
    return DMLResult(
        status=serialized_result['status'],
        job_type=serialized_result['job_type'],
        results=serialized_result['results'],
        error_message=serialized_result['error_message'],
    )
