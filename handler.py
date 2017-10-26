# -*- coding: utf-8 -*-
"""
Entry point that calls the main source code

handler.lambda_handler calls .lib/ami_lookup.py

TO DO: None
"""

import logging


def lambda_handler(event, context):
    """Entry Point"""
    enable_logging(event)
    execute_main(event, context)


def enable_logging(event):
    "Enables Logging for Console and CloudWatch"
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info('Event: ' + str(event))


def execute_main(event, context):
    """Calls the main code"""
    from lib.ami_lookup import main
    main(event, context)
