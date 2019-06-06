import boto3

from rest_framework import serializers
from rest_auth.serializers import UserDetailsSerializer

class UserSerializer(UserDetailsSerializer):
    occupation = serializers.CharField(min_length=3, max_length=100, source="enterpriseuserprofile.occupation")
    company = serializers.CharField(min_length=3, max_length=100, source="enterpriseuserprofile.company")

    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ('occupation', 'company', )

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('enterpriseuserprofile', {})

        instance = super(UserSerializer, self).update(instance, validated_data)

        # Get and update user profile.
        if profile_data:
            profile = instance.enterpriseuserprofile

            occupation = profile_data.get('occupation')
            if occupation != None:
                profile.occupation = occupation

            company = profile_data.get('company')
            if company != None:
                profile.company = company

            profile.save()
        return instance

from rest_auth.registration.serializers import RegisterSerializer
from allauth.account import app_settings as allauth_settings
from allauth.utils import email_address_exists
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    company = serializers.CharField(source="enterpriseuserprofile.company", required=True, min_length=3, max_length=100, write_only=True)
    occupation = serializers.CharField(source="enterpriseuserprofile.occupation", required=True, min_length=3, max_length=100, write_only=True)

    def get_cleaned_data(self):
        profile_data = self.validated_data.pop('enterpriseuserprofile', {})
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'occupation': profile_data.get('occupation', "N/A"),
            'company': profile_data.get('company', "N/A")
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user.save()

        profile = user.enterpriseuserprofile
        occupation = self.cleaned_data.get('occupation')
        if occupation != None:
            profile.occupation = occupation

        company = self.cleaned_data.get('company')
        if company != None:
            profile.company = company
        profile.save()

        self._createUserData(user.id)
        self._createTestRepo(user.id)
        return user

    def _createUserData(self, user_id):
        """Only creates it if doesn't exist already."""
        dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
        table = dynamodb.Table("UsersDashboardData")
        try:
            item = {
                'UserId': user_id,
                'ReposManaged': set(["test"]),
                'ApiKeys': set(["null"]),
                'ReposRemaining': 5,
            }
            table.put_item(
                Item=item,
                ConditionExpression="attribute_not_exists(UserId)"
            )
        except:
            raise Exception("Error while creating the user dashboard data.")

    def _createTestRepo(self, user_id):
        dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
        table = dynamodb.Table("Repos")
        try:
            item = {
                'Id': "test",
                'Name': "hello-i-am-a-test-repo",
                'Description': "This is just a test repo. There's nothing here and will never be. Well, maybe.",
                'OwnerId': user_id,
                'ContributorsId': [],
                'CoordinatorAddress': "cloud-node-env99.au4c4pd2ch.us-west-1.elasticbeanstalk.com",
                # 'ExploratoryData': None,
            }
            table.put_item(Item=item)
        except:
            raise Exception("Error while creating the new repo document.")
