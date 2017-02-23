# Readme


## Overview

This repository contains some example Python code to help audit your Enterprise Slack. It is designed to be executed in an AWS Lambda function. The code will poll either the [team.accessLogs](https://api.slack.com/methods/team.accessLogs) api or the [team.integrationLogs](https://api.slack.com/methods/team.integrationLogs) api and push any new logs to an S3 bucket.

## Setup

You will need:

1. An OAuth token with an admin scope. see [here](https://api.slack.com/tutorials/slack-apps-and-postman)
2. An S3 bucket and a KMS key.
3. An IAM role that gives access to your bucket and the KMS key that can be applied ot the Lambda function.
4. Create a Lambda function with the follow environment variables:

  * `KMS_REGION` = the region of your KMS key
  * `SLACK_TOKEN` = your admin token (encrypted with KMS)
  * `BUCKET_NAME` = the name of your log bucket

## AWS Lambda help

Here are a few pointers to help people who are new to AWS Lambda to get started. You will need to bundle up the slackclient library with your code to run this. Pip can be used to install it to a directory:

```
pip install slackclient -t ./src/ --upgrade
```

Then use this bash script to upload to your Lambda job:

```
#!/bin/bash

echo "Bundling code and pushing to Lambda"
cd ./src/
zip -r bundle.zip *
aws lambda update-function-code --function-name $FUNCTIONNAME --region $REGION --zip-file fileb://bundle.zip
rm bundle.zip
cd ..
echo "Done"
```

## Issue Reporting

If you have found a bug or if you have a feature request, please report them at this repository issues section. Please do not report security vulnerabilities on the public GitHub issue tracker. The [Responsible Disclosure Program](https://auth0.com/whitehat) details the procedure for disclosing security issues.

For Auth0 related questions or support please use the [Support Center](https://support.auth0.com).

## Author

[Auth0](https://auth0.com)

## License

This project is licensed under the MIT license.
