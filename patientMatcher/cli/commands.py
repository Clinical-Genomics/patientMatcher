#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import click

LOG = logging.getLogger(__name__)

@click.group()
def base():
    """Entry point to the CLI"""
    LOG.info('HELLO THERE!')
