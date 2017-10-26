# -*- coding: utf-8 -*-
"""
Return from Lambda
"""

import os
import logging

EVENT = {
    'RequestType':
    'Create',
    'ServiceToken':
    'arn:aws:lambda:us-east-1:123456789123:function:test-AMIInfoFunction',
    'ResponseURL':
    'https://cloudformation-custom-resource-response-',
    'StackId':
    'arn:aws:cloudformation:us-east-1:123456789123:stack/test/',
    'RequestId':
    '7998bdb7-c690-4d54-',
    'LogicalResourceId':
    'AMIInfo',
    'ResourceType':
    'AWS::CloudFormation::CustomResource',
    'ResourceProperties': {
        'ServiceToken':
        'arn:aws:lambda:us-east-1:123456789123:function:test-AMIInfoFunction',
        'OSName':
        'cwFrontEnd'
    }
}


def enable_info_logging():
    """Enable Info Level Logging Messages"""
    logging_conf = {
        'level': logging.INFO,
        'format': '%(asctime)s %(levelname)s %(message)s',
        "datefmt": '%H:%M:%S'
    }
    logging.basicConfig(**logging_conf)


if __name__ == '__main__':
    enable_info_logging()
    # ensures the cwd is root of project
    __WS_DIR__ = os.path.dirname(os.path.realpath(__file__))
    os.chdir('{}/..'.format(__WS_DIR__))

    # execute lambda_handler
    from handler import lambda_handler
    lambda_handler(EVENT, None)
