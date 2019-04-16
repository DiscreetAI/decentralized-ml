import time
import uuid

import boto3

import state
from model import TEMP_FOLDER


def store_update(type, message, with_weights=True):
    print("[{0}]: {1}".format(type, message))

    if with_weights:
        try:
            session_id = state.state['session_id']
            round = state.state['current_round']
            s3 = boto3.resource('s3')
            weights_s3_key = 'test/{0}/{1}/model.h5'.format(session_id, round)
            object = s3.Object('updatestore', weights_s3_key)
            h5_filepath = TEMP_FOLDER + "/{0}/model{1}.h5".format(session_id, round)
            object.put(Body=open(h5_filepath, 'rb'))
        except Exception as e:
            print("S3 Error: {0}".format(e))

    try:
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table("updatestore_" + state.state["repo_id"])
        item = {
            'Id': str(uuid.uuid4()),
            'RepoId': state.state["repo_id"],
            'Timestamp': int(time.time()),
            'ContentType': type,
            'SessionId': state.state["session_id"],
            'Content': repr(message),
        }
        if with_weights:
            item['WeightsS3Key'] = "s3://updatestore/" + weights_s3_key
        table.put_item(Item=item)
    except Exception as e:
        print("DB Error: {0}".format(e))
