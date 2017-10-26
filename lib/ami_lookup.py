# -*- coding: utf-8 -*-
""" Looking up Amazon Machine Image IDs

Todo:
    * N/A
"""

import os
import json
import logging
import boto3
from botocore.vendored import requests
SUCCESS = 'SUCCESS'


def main(event, context):
    """The main worker for this code"""
    data = import_config()
    server = parse_event_data(event, data)
    images = describe_images(server)
    responseData = sort_images(images)
    responseBody = build_response_body(event, context, SUCCESS, responseData)
    send_response_body(responseBody, event)


def enable_logging(event, responseUrl, responseBody):
    """Enables Logging for Console and CloudWatch"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info('Event: ' + str(event))
    logger.info('ResponseURL: ' + responseUrl)
    logger.info('Response body: ' + str(responseBody))


def import_config():
    """Import ./data/config.json"""
    with open(os.path.abspath('./data/config.json')) as json_config:
        config_template = json.load(json_config)
        data = config_template.get('default')
    return data


def parse_event_data(event, data):
    "Parse server name in config.json against selection from AWS CloudFormation"
    servers = data.get('servers')
    osName = event.get('ResourceProperties').get('OSName')
    if osName in servers:
        return servers.get(osName)


def describe_images(server):
    "Return EC2 image from AWS Marketplace"
    ec2 = boto3.client('ec2')
    response = ec2.describe_images(
        Filters=[{
            'Name': 'name',
            'Values': [server]
        }], Owners=['self'])
    images = response.get('Images')
    return images


def sort_images(images):
    "Sort EC2 image based on CreationDate"
    sorted_images = sorted(
        images, key=lambda image: image['CreationDate'], reverse=True)
    image = sorted_images[0]
    responseData = {}
    responseData['Id'] = image.get('ImageId')
    return responseData


def build_response_body(event, context, responseStatus, responseData):
    "Build the response body to be returned"
    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['PhysicalResourceId'] = context.log_stream_name
    responseBody[
        'Reason'] = 'See CloudWatch Log Stream' + context.log_stream_name
    responseBody['StackId'] = event.get('StackId')
    responseBody['RequestId'] = event.get('RequestId')
    responseBody['LogicalResourceId'] = event.get('LogicalResourceId')
    responseBody['Data'] = responseData
    return responseBody


def send_response_body(responseBody, event):
    """Send response body back to AWS CloudFormation using ResponseURL"""
    responseUrl = event.get('ResponseURL')
    json_responseBody = json.dumps(responseBody)
    enable_logging(event, responseUrl, json_responseBody)
    requests.put(responseUrl, data=json_responseBody)
