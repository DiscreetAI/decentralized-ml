import boto3
import os
from boto3.dynamodb.conditions import Key, Attr
import logging
# Get the service resource.
class DB(object):
    def __init__(self):
        access_key = os.environ["AWS_ACCESS_KEY_ID"]
        secret_key = os.environ["AWS_SECRET_ACCESS_KEY"]
        self.dynamodb = boto3.resource('dynamodb', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name='us-west-1')
        self.users_table = self.dynamodb.Table('jupyterhub-users')
        self.repos_table = self.dynamodb.Table('Repos')
    
    # Only to be used when table needs to be remade
    def create_table(self):
        self.users_table = self.dynamodb.create_table(
            TableName='jupyterhub-users',
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'
                },
                {
                    'AttributeName': 'repo_id',
                    'KeyType': 'SORT'
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'repo_id',
                    'AttributeType': 'S'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        table.meta.client.get_waiter('table_exists').wait(TableName='jupyterhub-users')

    def delete_table(self):
        self.users_table.delete()
        self.users_table = None

    def add_user(self, username, batch=None):
        if not batch:
            batch = self.users_table
        assert batch != None, "Table not initialized!"
        batch.put_item(
            Item={
                'username': username,
                'in_use': False
            }
        )

    def add_multiple_users(self, usernames):
        with self.users_table.batch_writer() as batch:
            for username in usernames:
                self.add_user(username, batch=batch)


    def get_username(self, user_id, repo_id):
        creds = self._get_creds(user_id, repo_id)
        if creds != 'N/A':
            return creds
        return self._get_next_available_username(user_id, repo_id)

    def _get_next_available_username(self, user_id, repo_id):
        response = self.users_table.scan(
            FilterExpression=Attr('in_use').eq(False)
        )
        items = response['Items']
        assert items, "No more usernames available!"
        self._set_user_creds(user_id, repo_id, items[0]['username'])
        self._set_creds_in_use(items[0]['username'], True)
        return items[0]['username']

    def _set_user_creds(self, user_id, repo_id, username):
        self.repos_table.update_item(
            Key={
                'Id': repo_id,
                'OwnerId': user_id
            },
            UpdateExpression='SET creds = :val1',
            ExpressionAttributeValues={
                ':val1': username
            }
        )

    def _set_creds_in_use(self, username, in_use):              
        self.users_table.update_item(
            Key={
                'username': username,
            },
            UpdateExpression='SET in_use = :val1',
            ExpressionAttributeValues={
                ':val1': in_use
            }
        )

    def _get_creds(self, user_id, repo_id):
        response = self.repos_table.get_item(
            Key={
                'Id': repo_id,
                'OwnerId': user_id
            }
        )
        item = response['Item']
        return item['creds']

# db = DB()

# items = db.users_table.scan()['Items']

# for item in items:
#     print(item)
#     db.users_table.update_item(
#         Key={
#             'username': item['username']
#         },
#         UpdateExpression='SET in_use = :val1',
#         ExpressionAttributeValues={
#             ':val1': False
#         }
#     )

# db.repos_table.update_item(
#     Key={
#         'Id': '3e55b6e37447aca26c807c2aa5961d89',
#         'OwnerId': 50
#     },
#     UpdateExpression='SET creds = :val1',
#     ExpressionAttributeValues={
#         ':val1': 'N/A'
#     }
# )

# item = db.repos_table.get_item(
#     Key={
#         'Id': '3e55b6e37447aca26c807c2aa5961d89',
#         'OwnerId': 50
#     }
# )
# print(item)
# # db.get_next_available_username()