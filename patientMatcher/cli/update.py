#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from clint.textui import progress
import click
from patientMatcher.constants import PHENOTYPE_TERMS

@click.group()
def update():
    """Update patientMatcher resources"""
    pass

@update.command()
def resources():
    """Updates HPO terms and disease ontology from the web.
    Specifically collect files from:
    http://purl.obolibrary.org/obo/hp.obo
    http://compbio.charite.de/jenkins/job/hpo.annotations/lastStableBuild/artifact/misc/phenotype_annotation.tab
    """
    for key,item in PHENOTYPE_TERMS.items():
        url = item['url']
        destination = item['resource_path']
        click.echo('Downloading {}..'.format(key))
        r = requests.get(url, stream=True)
        with open(destination, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                if chunk:
                    f.write(chunk)
                    f.flush()
