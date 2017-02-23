import os
import json
import time
from base64 import b64decode

import boto3
import botocore

from slackclient import SlackClient

ENCRYPTED_SLACK_TOKEN = os.environ['SLACK_TOKEN']
KMS_REGION = os.environ['KMS_REGION']
SLACK_TOKEN = boto3.client('kms', region_name=KMS_REGION).decrypt(CiphertextBlob=b64decode(ENCRYPTED_SLACK_TOKEN))['Plaintext']
BUCKET_NAME = os.environ['BUCKET_NAME']


def lambda_handler(event, context):
    """ Entry point for AWS Lambda function """

    print "Starting execution"
    state_file_name = "integrations_state.csv"

    # create our api clients for aws and slack
    bucket = boto3.resource('s3').Bucket(BUCKET_NAME)
    slack_client = SlackClient(SLACK_TOKEN)

    # State is the last log we saw - the slack api returns logs in order,
    # so we will pop logs off the stack until we find one that matches state.
    # Pull the state file from S3.
    try:
        bucket.download_file(state_file_name, '/tmp/state.csv')
    except botocore.exceptions.ClientError as e:
        print "No state file creating a new one"
        junk_state_file = open('/tmp/state.csv', 'w+')
        junk_state_file.write("user,10000,\n")
        junk_state_file.close()

    state_file = open('/tmp/state.csv', 'r+')

    # Read the first line and parse comma separated values.
    s_state = state_file.readline().split(',')
    s_user_id = s_state[0]
    s_date = s_state[1]

    # Get the last 500 logs from the integrationLogs api
    response = slack_client.api_call(
        "team.integrationLogs",
        count=500,
        page=1
    )

    logs = response['logs']

    # Create a temporary file to write the slack access logs
    temp_file = open('/tmp/file', 'w+')

    # Loop until we match our state log.
    for log in logs:
        if (
                str(log['user_id']) == str(s_user_id) and
                int(log['date']) == int(s_date)):

            print "We have seen this before!"
            break

        else:
            # store each log in the temp file.
            temp_file.write(json.dumps(log)+"\n")

    temp_file.close()

    bucket_key = "slacklogs/integrations/Slack_"+str(int(time.time()))+".log"
    # Upload the Slack logs to S3
    bucket.upload_file('/tmp/file', bucket_key)

    # Set the state to be the first log on the stack
    new_state_file = open('/tmp/newstatefile', 'w+')
    new_state_file.write(
        "%s,%s\n" % (logs[0]['user_id'], logs[0]['date'])
    )

    new_state_file.close()

    # Write the state file back to S3
    bucket.upload_file('/tmp/newstatefile', state_file_name)

    print "Finished Execution"
