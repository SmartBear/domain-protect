from __future__ import print_function
import json
import os
from urllib import request, parse


def lambda_handler(event, context):  # pylint:disable=unused-argument

    slack_url = os.environ["SLACK_WEBHOOK_URL"]
    slack_channel = os.environ["SLACK_CHANNEL"]
    slack_username = os.environ["SLACK_USERNAME"]
    slack_emoji = os.environ["SLACK_EMOJI"]

    subject = event["Records"][0]["Sns"]["Subject"]

    payload = {
        "channel": slack_channel,
        "username": slack_username,
        "icon_emoji": slack_emoji,
        "attachments": [],
        "text": subject,
    }

    message = event["Records"][0]["Sns"]["Message"]
    json_data = json.loads(message)
    
    try:
        findings = json_data["Findings"]

        slack_message = {"fallback": "A new message", "fields": [{"title": "Vulnerable domains"}]}

        for finding in findings:

            print(f"{finding['Domain']} in {finding['Account']} AWS Account")

            slack_message["fields"].append(
                {"value": finding["Domain"] + " in " + finding["Account"] + " AWS Account", "short": False}
            )

    except KeyError:
        pass
    
    try:
        takeovers = json_data["Takeovers"]

        slack_message = {"fallback": "A new message", "fields": [{"title": "Domains taken over"}]}

        for takeover in takeovers:

            print(f"{takeover['TakeoverStatus']}: {takeover['ResourceType']} {takeover['TakeoverDomain']} domain created in {takeover['TakeoverAccount']} AWS account to protect {takeover['TakeoverDomain']} in {takeover['VulnerableAccount']} account")

            slack_message["fields"].append(
                {"value": takeover['TakeoverStatus'] + ": " + takeover['ResourceType'] + " " + takeover['TakeoverDomain'] + " created in " + takeover['TakeoverAccount'] + " to protect " + takeover['VulnerableDomain'] + " in " + takeover['VulnerableAccount'] + " AWS Account", "short": False}
            )

    except KeyError:
        pass

    payload["attachments"].append(slack_message)

    data = parse.urlencode({"payload": json.dumps(payload)}).encode("utf-8")
    req = request.Request(slack_url)

    with request.urlopen(req, data):
        print(f"Message sent to {slack_channel} Slack channel")
