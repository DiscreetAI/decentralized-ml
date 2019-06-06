import re
import time
import secrets
import decimal
import hashlib

import jwt
import boto3
import requests
from flask_cors import CORS
from boto3.dynamodb.conditions import Key
from flask import Flask, request, jsonify

from deploy import run_deploy_routine


JWT_SECRET = "datajbsnmd5h84rbewvzx6*cax^jgmqw@m3$ds_%z-4*qy0n44fjr5shark"
JWT_ALGO = "HS256"

app = Flask(__name__)
CORS(app)

@app.route("/userdata", methods=["GET"])
def get_user_data():
    # Check authorization
    claims = authorize_user(request)
    if claims is None: return jsonify(make_unauthorized_error()), 400

    # Get data
    user_id = claims["pk"]
    try:
        user_data = _get_user_data(user_id)
        repos_remaining = user_data['ReposRemaining']
    except:
        return jsonify(make_error("Error while getting user's permissions.")), 400
    return jsonify({"ReposRemaining": True if repos_remaining > 0 else False})

@app.route("/repo/<repo_id>", methods=["GET"])
def get_repo(repo_id):
    # Check authorization
    claims = authorize_user(request)
    if claims is None: return jsonify(make_unauthorized_error()), 400

    # Get data
    user_id = claims["pk"]
    try:
        repo_details = _get_repo_details(user_id, repo_id)
    except:
        return jsonify(make_error("Error while getting the details for this repo.")), 400
    return jsonify(repo_details)

@app.route("/repo", methods=["POST"])
def create_new_repo():
    # Check authorization
    claims = authorize_user(request)
    if claims is None: return jsonify(make_unauthorized_error()), 400

    # Get parameters
    # TODO: Sanitize inputs.
    params = request.get_json()
    if "RepoName" not in params:
        return jsonify(make_error("Missing repo name from request.")), 400
    if "RepoDescription" not in params:
        return jsonify(make_error("Missing repo description from request.")), 400
    repo_name = params["RepoName"][:20]
    repo_description = params["RepoDescription"][:80]

    # TODO: Check repo doesn't already exist.

    user_id = claims["pk"]
    repo_name = re.sub('[^a-zA-Z0-9-]', '-', repo_name)
    try:
        _assert_user_has_repos_left(user_id)
        repo_id = _create_new_repo_document(user_id, repo_name, repo_description)
        api_key, true_api_key = _create_new_api_key(user_id, repo_id)
        _update_user_data_with_new_repo(user_id, repo_id, api_key)
        _create_new_cloud_node(repo_id, api_key)
    except Exception as e:
        # TODO: Revert things.
        return jsonify(make_error(str(e))), 400

    return jsonify({
        "Error": False,
        "Results": {
            "RepoId": repo_id,
            "TrueApiKey": true_api_key
        }
    })

@app.route("/repos", methods=["GET"])
def get_all_repos():
    # Check authorization
    claims = authorize_user(request)
    if claims is None: return jsonify(make_unauthorized_error()), 400

    # Get data
    user_id = claims["pk"]
    try:
        repo_list = _get_all_repos(user_id)
    except:
        return jsonify(make_error("Error while getting list of repos.")), 400
    return jsonify(repo_list)

@app.route("/logs/<repo_id>", methods=["GET"])
def get_logs(repo_id):
    # Check authorization
    claims = authorize_user(request)
    if claims is None: return jsonify(make_unauthorized_error()), 400

    # Get data
    user_id = claims["pk"]
    try:
        _assert_user_can_read_repo(user_id, repo_id)
        logs = _get_logs(repo_id)
    except Exception as e:
        return jsonify(make_error(str(e))), 400
    return jsonify(logs)

@app.route("/coordinator/status/<repo_id>", methods=["GET"])
def get_coordinator_status(repo_id):
    # Check authorization
    claims = authorize_user(request)
    if claims is None: return jsonify(make_unauthorized_error()), 400

    # Get data
    user_id = claims["pk"]
    try:
        repo_details = _get_repo_details(user_id, repo_id)
        cloud_node_url = repo_details['CoordinatorAddress']
        # TODO: Remove the 'http' here and add 'https' to the URL constructor.
        r = requests.get("http://" + cloud_node_url + "/status")
        status_data = r.json()
        assert "Busy" in status_data
    except Exception as e:
        return jsonify(make_error("Error while checking coordinator's status.")), 400
    return jsonify(status_data)

@app.route("/model", methods=["POST"])
def download_model():
    # Check authorization
    claims = authorize_user(request)
    if claims is None: return jsonify(make_unauthorized_error()), 400

    # Get parameters
    params = request.get_json()
    if "RepoId" not in params:
        return jsonify(make_error("Missing repo id from request.")), 400
    if "SessionId" not in params:
        return jsonify(make_error("Missing session id from request.")), 400
    if "Round" not in params:
        return jsonify(make_error("Missing round from request.")), 400
    repo_id  = params.get('RepoId', None)
    session_id  = params.get('SessionId', None)
    round  = params.get('Round', None)
    bucket_name = "updatestore"
    object_name = "{0}/{1}/{2}/model.h5".format(repo_id, session_id, round)

    # Get presigned URL
    user_id = claims["pk"]
    try:
        _assert_user_can_read_repo(user_id, repo_id)
        url = _create_presigned_url(bucket_name, object_name)
    except Exception as e:
        return jsonify(make_error(str(e))), 400

    # Return url
    return jsonify({'DownloadUrl': url})


# NOTE: This function was added in the auth-enterprise app instead.
# @app.route("/userdata", methods=["POST"])
# def create_user_data():
#     # Check authorization
#     claims = authorize_user(request)
#     if claims is None: return jsonify(make_unauthorized_error()), 400
#
#     # Create document
#     user_id = claims["pk"]
#     try:
#         _create_user_data(user_id)
#     except Exception as e:
#         return jsonify(make_error(str(e))), 400
#     return jsonify({})
#
# def _create_user_data(user_id):
#     """Only creates it if doesn't exist already."""
#     table = _get_dynamodb_table("UsersDashboardData")
#     try:
#         item = {
#             'UserId': user_id,
#             'ReposManaged': set(["null"]),
#             'ApiKeys': set(["null"]),
#             'ReposRemaining': 5,
#         }
#         table.put_item(
#             Item=item,
#             ConditionExpression="attribute_not_exists(UserId)"
#         )
#     except:
#         raise Exception("Error while creating the user data.")

def _assert_user_has_repos_left(user_id):
    user_data = _get_user_data(user_id)
    assert int(user_data['ReposRemaining']) > 0, "You don't have any repos left."

def _assert_user_can_read_repo(user_id, repo_id):
    try:
        user_data = _get_user_data(user_id)
        repos_managed = user_data['ReposManaged']
    except:
        raise Exception("Error while getting user's permissions.")
    assert repo_id in repos_managed, "You don't have permissions for this repo."

def _get_logs(repo_id):
    logs_table = _get_dynamodb_table("UpdateStore")
    try:
        response = logs_table.query(
            KeyConditionExpression=Key('RepoId').eq(repo_id)
        )
        logs = response["Items"]
    except Exception as e:
        raise Exception("Error while getting logs for repo. " + str(e))
    return logs

def _get_user_data(user_id):
    table = _get_dynamodb_table("UsersDashboardData")
    try:
        response = table.get_item(
            Key={
                "UserId": user_id,
            }
        )
        data = response["Item"]
    except:
        raise Exception("Error while getting user dashboard data.")
    return data

def _get_repo_details(user_id, repo_id):
    repos_table = _get_dynamodb_table("Repos")
    try:
        response = repos_table.get_item(
            Key={
                "Id": repo_id,
                "OwnerId": user_id,
            }
        )
        repo_details = response["Item"]
    except:
        raise Exception("Error while getting repo details.")
    return repo_details

def _update_user_data_with_new_repo(user_id, repo_id, api_key):
    table = _get_dynamodb_table("UsersDashboardData")
    try:
        response = table.update_item(
            Key={
                'UserId': user_id,
            },
            UpdateExpression="SET ReposRemaining = ReposRemaining - :val " + \
                             "ADD ReposManaged :repo_id, " + \
                             "ApiKeys :api_key",
            ExpressionAttributeValues={
                ':val': decimal.Decimal(1),
                ':repo_id': set([repo_id]),
                ':api_key': set([api_key]),
            }
        )
    except:
        raise Exception("Error while updating user data with new repo data.")

def _create_new_repo_document(user_id, repo_name, repo_description):
    table = _get_dynamodb_table("Repos")
    repo_id = secrets.token_hex(16)
    try:
        item = {
            'Id': repo_id,
            'Name': repo_name,
            'Description': repo_description,
            'OwnerId': user_id,
            'ContributorsId': [],
            'CoordinatorAddress': _construct_cloud_node_url(repo_id),
            'CreatedAt': int(time.time()),
            # 'ExploratoryData': None,
        }
        table.put_item(Item=item)
    except:
        raise Exception("Error while creating the new repo document.")
    return repo_id

def _create_new_api_key(user_id, repo_id):
    table = _get_dynamodb_table("ApiKeys")
    true_api_key = secrets.token_urlsafe(32)
    h = hashlib.sha256()
    h.update(true_api_key.encode('utf-8'))
    api_key = h.hexdigest()
    try:
        item = {
            'Key': api_key,
            'OwnerId': user_id,
            'RepoId': repo_id,
            'CreatedAt': int(time.time()),
        }
        table.put_item(Item=item)
    except:
        raise Exception("Error while creating a new API key.")
    return api_key, true_api_key

def _get_all_repos(user_id):
    try:
        user_data = _get_user_data(user_id)
        repos_managed = user_data['ReposManaged']

        repos_table = _get_dynamodb_table("Repos")
        all_repos = []
        for repo_id in repos_managed:
            if repo_id == "null": continue
            response = repos_table.get_item(
                Key={
                    "Id": repo_id,
                    "OwnerId": user_id,
                }
            )

            if 'Item' in response:
                all_repos.append(response['Item'])
    except:
        raise Exception("Error while getting all repos.")
    return all_repos

def _create_new_cloud_node(repo_id, api_key):
    try:
        run_deploy_routine(repo_id)
    except Exception as e:
        raise Exception("Error while creating new cloud node.")

def _create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name
            },
            ExpiresIn=expiration
        )
    except ClientError as e:
        raise Exception("Error while creating S3 presigned url.")

    # The response contains the presigned URL
    return response

def _get_dynamodb_table(table_name):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
    table = dynamodb.Table(table_name)
    return table

def _construct_cloud_node_url(repo_id):
    CLOUD_NODE_ADDRESS_TEMPLATE = "{0}.au4c4pd2ch.us-west-1.elasticbeanstalk.com"
    return CLOUD_NODE_ADDRESS_TEMPLATE.format(repo_id)


def authorize_user(request):
    try:
        jwt_string = request.headers.get("Authorization").split('Bearer ')[1]
        claims = jwt.decode(jwt_string, JWT_SECRET, algorithms=[JWT_ALGO])
    except:
        return None
    return claims

def make_unauthorized_error():
    return make_error('Authorization failed.')

def make_error(msg):
    return {'Error': True, 'Message': msg}


if __name__ == "__main__":
    app.run(port=5001)
