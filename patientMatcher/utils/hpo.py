# -*- coding: utf-8 -*-
import logging

from patientMatcher.resources import path_to_hpo_terms

LOG = logging.getLogger(__name__)

ROOT = "HP:0000001"

class HPO(object):
    """Parse and HPO ontology to make it available for phenotype matching"""
    def __init__(self):
        self.root = ROOT
        self.terms = {}

    def parse_ontolology(self):
        """Parse HPO ontology file, that is available under patientMatcher/resources"""
        with open(path_to_hpo_terms, encoding='utf-8') as :
